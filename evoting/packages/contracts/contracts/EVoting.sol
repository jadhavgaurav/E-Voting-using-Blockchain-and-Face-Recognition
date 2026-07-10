// SPDX-License-Identifier: MIT
pragma solidity 0.8.24;

import {AccessControl} from "@openzeppelin/contracts/access/AccessControl.sol";
import {Pausable} from "@openzeppelin/contracts/utils/Pausable.sol";

/**
 * @title EVoting
 * @author E-Voting platform
 * @notice On-chain election lifecycle, admin-only candidate registration, and
 *         one-vote-per-address voting with an on-chain tally.
 *
 * @dev Design principles:
 *      - The chain is the source of truth for votes. Candidate names/symbols and
 *        election titles live off-chain (in PostgreSQL), keyed by numeric ids so
 *        the contract never stores or compares free-text strings.
 *      - `msg.sender` IS the voter. The backend relayer submits a transaction
 *        signed by the voter's custodial key; the contract never accepts a
 *        "vote on behalf of X" parameter.
 *      - All privileged actions are gated by ADMIN_ROLE (OpenZeppelin AccessControl).
 */
contract EVoting is AccessControl, Pausable {
    bytes32 public constant ADMIN_ROLE = keccak256("ADMIN_ROLE");

    struct Election {
        uint64 startTime;
        uint64 endTime;
        uint32 candidateCount;
        bool exists;
        bool votingBegun;
    }

    /// @notice Auto-incrementing id assigned to the next created election.
    uint256 public nextElectionId;

    /// @dev electionId => election metadata
    mapping(uint256 => Election) private _elections;
    /// @dev electionId => voter => voted?
    mapping(uint256 => mapping(address => bool)) private _hasVoted;
    /// @dev electionId => candidateIndex => vote count
    mapping(uint256 => mapping(uint256 => uint256)) private _tally;
    /// @dev electionId => voter => chosen candidate index (for receipt/audit)
    mapping(uint256 => mapping(address => uint256)) private _choice;

    event ElectionCreated(uint256 indexed electionId, uint64 startTime, uint64 endTime);
    event CandidatesAdded(uint256 indexed electionId, uint32 previousCount, uint32 newCount);
    event VoteCast(
        uint256 indexed electionId,
        address indexed voter,
        uint256 indexed candidateIndex,
        uint256 timestamp
    );

    error InvalidElectionWindow();
    error ElectionDoesNotExist(uint256 electionId);
    error VotingNotStarted(uint256 electionId);
    error VotingEnded(uint256 electionId);
    error VotingStillOpen(uint256 electionId);
    error CandidatesLocked(uint256 electionId);
    error ZeroCandidates();
    error AlreadyVoted(uint256 electionId, address voter);
    error InvalidCandidate(uint256 electionId, uint256 candidateIndex);

    constructor(address admin) {
        _grantRole(DEFAULT_ADMIN_ROLE, admin);
        _grantRole(ADMIN_ROLE, admin);
    }

    // ─────────────────────────────── Admin ───────────────────────────────

    /**
     * @notice Create an election with a voting window. Admin only.
     * @param startTime Unix timestamp voting opens (must be in the future, < endTime).
     * @param endTime   Unix timestamp voting closes.
     * @return electionId The id assigned to the new election.
     */
    function createElection(uint64 startTime, uint64 endTime)
        external
        onlyRole(ADMIN_ROLE)
        returns (uint256 electionId)
    {
        if (startTime >= endTime) revert InvalidElectionWindow();
        if (endTime <= block.timestamp) revert InvalidElectionWindow();

        electionId = nextElectionId++;
        _elections[electionId] = Election({
            startTime: startTime,
            endTime: endTime,
            candidateCount: 0,
            exists: true,
            votingBegun: false
        });

        emit ElectionCreated(electionId, startTime, endTime);
    }

    /**
     * @notice Register `count` candidate slots for an election. Admin only, allowed until
     *         the first vote is cast so an already-open election can still finalize its
     *         ballot; the candidate set is frozen the moment voting actually begins.
     * @dev Candidates are referenced by index [0, candidateCount). Their names/parties
     *      are stored off-chain against the same indices.
     */
    function addCandidates(uint256 electionId, uint32 count) external onlyRole(ADMIN_ROLE) {
        Election storage e = _elections[electionId];
        if (!e.exists) revert ElectionDoesNotExist(electionId);
        if (count == 0) revert ZeroCandidates();
        if (e.votingBegun) revert CandidatesLocked(electionId);

        uint32 previous = e.candidateCount;
        e.candidateCount = previous + count;

        emit CandidatesAdded(electionId, previous, e.candidateCount);
    }

    /// @notice Emergency stop — blocks voting. Admin only.
    function pause() external onlyRole(ADMIN_ROLE) {
        _pause();
    }

    /// @notice Resume voting after a pause. Admin only.
    function unpause() external onlyRole(ADMIN_ROLE) {
        _unpause();
    }

    // ─────────────────────────────── Voting ──────────────────────────────

    /**
     * @notice Cast a vote. The caller (msg.sender) is the voter.
     * @param electionId     Election to vote in.
     * @param candidateIndex Candidate index in [0, candidateCount).
     *
     * Reverts if: election missing, outside the window, paused, caller already
     * voted, or candidate index is out of range.
     */
    function vote(uint256 electionId, uint256 candidateIndex) external whenNotPaused {
        Election storage e = _elections[electionId];
        if (!e.exists) revert ElectionDoesNotExist(electionId);
        if (block.timestamp < e.startTime) revert VotingNotStarted(electionId);
        if (block.timestamp > e.endTime) revert VotingEnded(electionId);
        if (_hasVoted[electionId][msg.sender]) revert AlreadyVoted(electionId, msg.sender);
        if (candidateIndex >= e.candidateCount) revert InvalidCandidate(electionId, candidateIndex);

        _hasVoted[electionId][msg.sender] = true;
        _choice[electionId][msg.sender] = candidateIndex;
        if (!e.votingBegun) {
            e.votingBegun = true;
        }
        unchecked {
            _tally[electionId][candidateIndex] += 1;
        }

        emit VoteCast(electionId, msg.sender, candidateIndex, block.timestamp);
    }

    // ─────────────────────────────── Views ───────────────────────────────

    function getElection(uint256 electionId)
        external
        view
        returns (uint64 startTime, uint64 endTime, uint32 numCandidates, bool exists)
    {
        Election storage e = _elections[electionId];
        return (e.startTime, e.endTime, e.candidateCount, e.exists);
    }

    function candidateCount(uint256 electionId) external view returns (uint32) {
        return _elections[electionId].candidateCount;
    }

    function hasVoted(uint256 electionId, address voter) external view returns (bool) {
        return _hasVoted[electionId][voter];
    }

    function voteCount(uint256 electionId, uint256 candidateIndex) external view returns (uint256) {
        return _tally[electionId][candidateIndex];
    }

    /// @notice Full result vector for an election: index i = votes for candidate i.
    function results(uint256 electionId) external view returns (uint256[] memory counts) {
        Election storage e = _elections[electionId];
        if (!e.exists) revert ElectionDoesNotExist(electionId);
        counts = new uint256[](e.candidateCount);
        for (uint256 i = 0; i < e.candidateCount; i++) {
            counts[i] = _tally[electionId][i];
        }
    }

    /**
     * @notice The candidate a voter chose. Reverts if they have not voted, so callers
     *         should gate on `hasVoted` first.
     */
    function choiceOf(uint256 electionId, address voter) external view returns (uint256) {
        if (!_hasVoted[electionId][voter]) revert AlreadyVoted(electionId, voter);
        return _choice[electionId][voter];
    }
}
