import { expect } from "chai";
import { ethers } from "hardhat";
import { time } from "@nomicfoundation/hardhat-network-helpers";
import { EVoting } from "../typechain-types";
import { SignerWithAddress } from "@nomicfoundation/hardhat-ethers/signers";

describe("EVoting", () => {
  let evoting: EVoting;
  let admin: SignerWithAddress;
  let voter1: SignerWithAddress;
  let voter2: SignerWithAddress;
  let outsider: SignerWithAddress;

  const HOUR = 3600;

  async function deploy(): Promise<void> {
    [admin, voter1, voter2, outsider] = await ethers.getSigners();
    const factory = await ethers.getContractFactory("EVoting");
    evoting = (await factory.deploy(admin.address)) as unknown as EVoting;
    await evoting.waitForDeployment();
  }

  /** Create an election starting `startIn` seconds from now, open for `duration`. */
  async function createElection(startIn = HOUR, duration = HOUR): Promise<bigint> {
    const now = await time.latest();
    const start = now + startIn;
    const end = start + duration;
    const tx = await evoting.createElection(start, end);
    await tx.wait();
    return 0n; // first election id
  }

  beforeEach(deploy);

  describe("deployment & roles", () => {
    it("grants ADMIN_ROLE and DEFAULT_ADMIN_ROLE to the admin", async () => {
      const ADMIN_ROLE = await evoting.ADMIN_ROLE();
      const DEFAULT_ADMIN_ROLE = await evoting.DEFAULT_ADMIN_ROLE();
      expect(await evoting.hasRole(ADMIN_ROLE, admin.address)).to.equal(true);
      expect(await evoting.hasRole(DEFAULT_ADMIN_ROLE, admin.address)).to.equal(true);
    });

    it("starts with nextElectionId = 0", async () => {
      expect(await evoting.nextElectionId()).to.equal(0n);
    });
  });

  describe("createElection", () => {
    it("creates an election and emits ElectionCreated", async () => {
      const now = await time.latest();
      const start = now + HOUR;
      const end = start + HOUR;
      await expect(evoting.createElection(start, end))
        .to.emit(evoting, "ElectionCreated")
        .withArgs(0n, start, end);

      const [s, e, count, exists] = await evoting.getElection(0n);
      expect(s).to.equal(start);
      expect(e).to.equal(end);
      expect(count).to.equal(0);
      expect(exists).to.equal(true);
      expect(await evoting.nextElectionId()).to.equal(1n);
    });

    it("reverts if start >= end", async () => {
      const now = await time.latest();
      await expect(evoting.createElection(now + HOUR, now + HOUR)).to.be.revertedWithCustomError(
        evoting,
        "InvalidElectionWindow"
      );
    });

    it("reverts if end is in the past", async () => {
      const now = await time.latest();
      await expect(evoting.createElection(now - 2 * HOUR, now - HOUR)).to.be.revertedWithCustomError(
        evoting,
        "InvalidElectionWindow"
      );
    });

    it("rejects a non-admin caller", async () => {
      const now = await time.latest();
      await expect(
        evoting.connect(outsider).createElection(now + HOUR, now + 2 * HOUR)
      ).to.be.revertedWithCustomError(evoting, "AccessControlUnauthorizedAccount");
    });
  });

  describe("addCandidates", () => {
    it("adds candidate slots and emits CandidatesAdded", async () => {
      const id = await createElection();
      await expect(evoting.addCandidates(id, 3))
        .to.emit(evoting, "CandidatesAdded")
        .withArgs(id, 0, 3);
      expect(await evoting.candidateCount(id)).to.equal(3);

      await evoting.addCandidates(id, 2);
      expect(await evoting.candidateCount(id)).to.equal(5);
    });

    it("rejects a non-admin caller", async () => {
      const id = await createElection();
      await expect(
        evoting.connect(outsider).addCandidates(id, 2)
      ).to.be.revertedWithCustomError(evoting, "AccessControlUnauthorizedAccount");
    });

    it("reverts for a missing election", async () => {
      await expect(evoting.addCandidates(99n, 2)).to.be.revertedWithCustomError(
        evoting,
        "ElectionDoesNotExist"
      );
    });

    it("reverts on zero candidates", async () => {
      const id = await createElection();
      await expect(evoting.addCandidates(id, 0)).to.be.revertedWithCustomError(
        evoting,
        "ZeroCandidates"
      );
    });

    it("allows adding candidates after voting opens but before the first vote", async () => {
      const id = await createElection();
      await evoting.addCandidates(id, 2);
      await time.increase(HOUR + 1); // move to within the voting window
      await evoting.addCandidates(id, 1); // still allowed: no votes yet
      expect(await evoting.candidateCount(id)).to.equal(3);
    });

    it("locks the candidate set once the first vote is cast", async () => {
      const id = await createElection();
      await evoting.addCandidates(id, 2);
      await time.increase(HOUR + 1); // enter the voting window
      await evoting.connect(voter1).vote(id, 0);
      await expect(evoting.addCandidates(id, 1)).to.be.revertedWithCustomError(
        evoting,
        "CandidatesLocked"
      );
    });
  });

  describe("vote", () => {
    async function openElectionWithCandidates(): Promise<bigint> {
      const id = await createElection();
      await evoting.addCandidates(id, 3);
      await time.increase(HOUR + 1); // enter the voting window
      return id;
    }

    it("records a vote, updates tally and choice, emits VoteCast", async () => {
      const id = await openElectionWithCandidates();
      await expect(evoting.connect(voter1).vote(id, 1))
        .to.emit(evoting, "VoteCast")
        .withArgs(id, voter1.address, 1, (t: bigint) => t > 0n);

      expect(await evoting.hasVoted(id, voter1.address)).to.equal(true);
      expect(await evoting.voteCount(id, 1)).to.equal(1n);
      expect(await evoting.choiceOf(id, voter1.address)).to.equal(1n);
    });

    it("rejects a second vote from the same voter", async () => {
      const id = await openElectionWithCandidates();
      await evoting.connect(voter1).vote(id, 0);
      await expect(evoting.connect(voter1).vote(id, 2)).to.be.revertedWithCustomError(
        evoting,
        "AlreadyVoted"
      );
    });

    it("allows different voters to vote independently and tallies correctly", async () => {
      const id = await openElectionWithCandidates();
      await evoting.connect(voter1).vote(id, 2);
      await evoting.connect(voter2).vote(id, 2);
      expect(await evoting.voteCount(id, 2)).to.equal(2n);
      const counts = await evoting.results(id);
      expect(counts.map((c) => Number(c))).to.deep.equal([0, 0, 2]);
    });

    it("rejects an out-of-range candidate", async () => {
      const id = await openElectionWithCandidates();
      await expect(evoting.connect(voter1).vote(id, 3)).to.be.revertedWithCustomError(
        evoting,
        "InvalidCandidate"
      );
    });

    it("reverts before the window opens", async () => {
      const id = await createElection();
      await evoting.addCandidates(id, 2);
      await expect(evoting.connect(voter1).vote(id, 0)).to.be.revertedWithCustomError(
        evoting,
        "VotingNotStarted"
      );
    });

    it("reverts after the window closes", async () => {
      const id = await openElectionWithCandidates();
      await time.increase(HOUR + 1); // past end
      await expect(evoting.connect(voter1).vote(id, 0)).to.be.revertedWithCustomError(
        evoting,
        "VotingEnded"
      );
    });

    it("reverts for a missing election", async () => {
      await expect(evoting.connect(voter1).vote(99n, 0)).to.be.revertedWithCustomError(
        evoting,
        "ElectionDoesNotExist"
      );
    });

    it("blocks voting while paused and resumes after unpause", async () => {
      const id = await openElectionWithCandidates();
      await evoting.pause();
      await expect(evoting.connect(voter1).vote(id, 0)).to.be.revertedWithCustomError(
        evoting,
        "EnforcedPause"
      );
      await evoting.unpause();
      await evoting.connect(voter1).vote(id, 0);
      expect(await evoting.voteCount(id, 0)).to.equal(1n);
    });

    it("rejects pause from a non-admin", async () => {
      await expect(evoting.connect(outsider).pause()).to.be.revertedWithCustomError(
        evoting,
        "AccessControlUnauthorizedAccount"
      );
    });
  });

  describe("views", () => {
    it("choiceOf reverts if the voter has not voted", async () => {
      const id = await createElection();
      await evoting.addCandidates(id, 2);
      await expect(evoting.choiceOf(id, voter1.address)).to.be.revertedWithCustomError(
        evoting,
        "AlreadyVoted"
      );
    });

    it("results reverts for a missing election", async () => {
      await expect(evoting.results(42n)).to.be.revertedWithCustomError(
        evoting,
        "ElectionDoesNotExist"
      );
    });
  });
});
