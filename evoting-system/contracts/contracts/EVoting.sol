// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/access/AccessControl.sol";

/**
 * @title EVoting
 * @notice On-chain election lifecycle, candidate registration, and one-vote-per-address voting.
 *         Election and candidate metadata live off-chain; only ids and tally are on-chain.
 */
contract EVoting is AccessControl {
    bytes32 public constant ADMIN_ROLE = keccak256("ADMIN_ROLE");

    struct Election {
        uint256 startTime;
        uint256 endTime;
        bool exists;
    }

    uint256 public nextElectionId;
    mapping(uint256 => Election) public elections;
    mapping(uint256 => uint256) public candidateCountPerElection;
    mapping(uint256 => mapping(uint256 => bool)) public isCandidate;
    mapping(uint256 => mapping(address => bool)) public hasVoted;
    mapping(uint256 => mapping(uint256 => uint256)) public candidateVoteCount;
    mapping(uint256 => mapping(address => uint256)) public voteChoice;

    event ElectionCreated(uint256 indexed electionId, uint256 startTime, uint256 endTime);
    event CandidatesAdded(uint256 indexed electionId, uint256 startIndex, uint256 count);
    event VoteCast(uint256 indexed electionId, address indexed voter, uint256 candidateIndex, uint256 timestamp);

    error ElectionDoesNotExist();
    error InvalidElectionWindow();
    error ElectionNotStarted();
    error ElectionEnded();
    error AlreadyVoted();
    error InvalidCandidate();

    constructor() {
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(ADMIN_ROLE, msg.sender);
    }

    /**
     * @notice Create a new election. Only callable by admin.
     * @param startTime Unix timestamp when voting opens
     * @param endTime Unix timestamp when voting closes
     */
    function createElection(uint256 startTime, uint256 endTime) external onlyRole(ADMIN_ROLE) {
        if (startTime >= endTime) revert InvalidElectionWindow();
        if (endTime <= block.timestamp) revert InvalidElectionWindow();

        uint256 electionId = nextElectionId;
        elections[electionId] = Election({ startTime: startTime, endTime: endTime, exists: true });
        nextElectionId++;

        emit ElectionCreated(electionId, startTime, endTime);
    }

    /**
     * @notice Add candidate slots to an election. Only before voting starts. Only callable by admin.
     * @param electionId Id of the election
     * @param count Number of candidate slots to add (indices 0..count-1 from current count)
     */
    function addCandidates(uint256 electionId, uint256 count) external onlyRole(ADMIN_ROLE) {
        if (!elections[electionId].exists) revert ElectionDoesNotExist();
        if (block.timestamp >= elections[electionId].startTime) revert ElectionNotStarted();

        uint256 startIndex = candidateCountPerElection[electionId];
        for (uint256 i = 0; i < count; i++) {
            isCandidate[electionId][startIndex + i] = true;
        }
        candidateCountPerElection[electionId] += count;

        emit CandidatesAdded(electionId, startIndex, count);
    }

    /**
     * @notice Cast a vote. Caller must be the voter (relayer signs tx with voter's key).
     * @param electionId Id of the election
     * @param candidateIndex Index of the candidate (must be valid for this election)
     */
    function vote(uint256 electionId, uint256 candidateIndex) external {
        if (!elections[electionId].exists) revert ElectionDoesNotExist();
        Election storage e = elections[electionId];
        if (block.timestamp < e.startTime) revert ElectionNotStarted();
        if (block.timestamp > e.endTime) revert ElectionEnded();
        if (hasVoted[electionId][msg.sender]) revert AlreadyVoted();
        if (!isCandidate[electionId][candidateIndex]) revert InvalidCandidate();

        hasVoted[electionId][msg.sender] = true;
        candidateVoteCount[electionId][candidateIndex]++;
        voteChoice[electionId][msg.sender] = candidateIndex;

        emit VoteCast(electionId, msg.sender, candidateIndex, block.timestamp);
    }

    function getElection(uint256 id) external view returns (uint256 startTime, uint256 endTime, bool exists) {
        Election storage e = elections[id];
        return (e.startTime, e.endTime, e.exists);
    }

    function getCandidateCount(uint256 electionId) external view returns (uint256) {
        return candidateCountPerElection[electionId];
    }

    function getVoteCount(uint256 electionId, uint256 candidateIndex) external view returns (uint256) {
        return candidateVoteCount[electionId][candidateIndex];
    }

    function hasVotedForElection(uint256 electionId, address voter) external view returns (bool) {
        return hasVoted[electionId][voter];
    }
}
