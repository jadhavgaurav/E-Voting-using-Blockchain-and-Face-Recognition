import { expect } from "chai";
import { ethers } from "hardhat";
import { loadFixture, time } from "@nomicfoundation/hardhat-toolbox/network-helpers";

describe("EVoting", function () {
  async function deployFixture() {
    const [admin, voterA, voterB, nonAdmin] = await ethers.getSigners();
    const EVoting = await ethers.getContractFactory("EVoting");
    const evoting = await EVoting.deploy();
    return { evoting, admin, voterA, voterB, nonAdmin };
  }

  async function electionReadyFixture() {
    const { evoting, admin, voterA, voterB, nonAdmin } = await loadFixture(deployFixture);
    const start = (await time.latest()) + 60;
    const end = start + 3600;
    await evoting.connect(admin).createElection(start, end);
    await evoting.connect(admin).addCandidates(0, 3);
    await time.increaseTo(start + 1);
    return { evoting, admin, voterA, voterB, nonAdmin };
  }

  describe("Deployment", function () {
    it("grants ADMIN_ROLE to deployer", async function () {
      const { evoting, admin } = await loadFixture(deployFixture);
      const ADMIN_ROLE = await evoting.ADMIN_ROLE();
      expect(await evoting.hasRole(ADMIN_ROLE, admin.address)).to.be.true;
    });
  });

  describe("Election lifecycle", function () {
    it("creates election with valid start/end and emits ElectionCreated", async function () {
      const { evoting, admin } = await loadFixture(deployFixture);
      const start = (await time.latest()) + 60;
      const end = start + 3600;
      await expect(evoting.connect(admin).createElection(start, end))
        .to.emit(evoting, "ElectionCreated")
        .withArgs(0, start, end);
      const [startTime, endTime, exists] = await evoting.getElection(0);
      expect(startTime).to.equal(start);
      expect(endTime).to.equal(end);
      expect(exists).to.be.true;
    });

    it("reverts createElection when startTime >= endTime", async function () {
      const { evoting, admin } = await loadFixture(deployFixture);
      const t = (await time.latest()) + 60;
      await expect(evoting.connect(admin).createElection(t, t)).to.be.revertedWithCustomError(
        evoting,
        "InvalidElectionWindow"
      );
      await expect(evoting.connect(admin).createElection(t + 100, t)).to.be.revertedWithCustomError(
        evoting,
        "InvalidElectionWindow"
      );
    });

    it("reverts createElection when endTime <= block.timestamp", async function () {
      const { evoting, admin } = await loadFixture(deployFixture);
      const start = (await time.latest()) - 100;
      const end = (await time.latest()) - 1;
      await expect(evoting.connect(admin).createElection(start, end)).to.be.revertedWithCustomError(
        evoting,
        "InvalidElectionWindow"
      );
    });

    it("reverts createElection when caller lacks admin role", async function () {
      const { evoting, nonAdmin } = await loadFixture(deployFixture);
      const start = (await time.latest()) + 60;
      const end = start + 3600;
      await expect(
        evoting.connect(nonAdmin).createElection(start, end)
      ).to.be.revertedWithCustomError(evoting, "AccessControlUnauthorizedAccount");
    });
  });

  describe("Candidates", function () {
    it("addCandidates sets candidateCountPerElection and isCandidate", async function () {
      const { evoting, admin } = await loadFixture(deployFixture);
      const start = (await time.latest()) + 60;
      const end = start + 3600;
      await evoting.connect(admin).createElection(start, end);
      await expect(evoting.connect(admin).addCandidates(0, 3))
        .to.emit(evoting, "CandidatesAdded")
        .withArgs(0, 0, 3);
      expect(await evoting.getCandidateCount(0)).to.equal(3);
      expect(await evoting.isCandidate(0, 0)).to.be.true;
      expect(await evoting.isCandidate(0, 1)).to.be.true;
      expect(await evoting.isCandidate(0, 2)).to.be.true;
      expect(await evoting.isCandidate(0, 3)).to.be.false;
    });

    it("reverts addCandidates when not admin", async function () {
      const { evoting, admin, nonAdmin } = await loadFixture(deployFixture);
      const start = (await time.latest()) + 60;
      const end = start + 3600;
      await evoting.connect(admin).createElection(start, end);
      await expect(
        evoting.connect(nonAdmin).addCandidates(0, 3)
      ).to.be.revertedWithCustomError(evoting, "AccessControlUnauthorizedAccount");
    });

    it("reverts addCandidates when election does not exist", async function () {
      const { evoting, admin } = await loadFixture(deployFixture);
      await expect(evoting.connect(admin).addCandidates(99, 3)).to.be.revertedWithCustomError(
        evoting,
        "ElectionDoesNotExist"
      );
    });

    it("reverts addCandidates when voting already started", async function () {
      const { evoting, admin } = await loadFixture(deployFixture);
      const start = (await time.latest()) + 2;
      const end = start + 3600;
      await evoting.connect(admin).createElection(start, end);
      await time.increaseTo(start + 1);
      await expect(evoting.connect(admin).addCandidates(0, 3)).to.be.revertedWithCustomError(
        evoting,
        "ElectionNotStarted"
      );
    });
  });

  describe("Voting", function () {
    it("vote emits VoteCast and updates hasVoted and candidateVoteCount", async function () {
      const { evoting, voterA } = await loadFixture(electionReadyFixture);
      const tx = await evoting.connect(voterA).vote(0, 0);
      const receipt = await tx.wait();
      const block = receipt && (await ethers.provider.getBlock(receipt.blockNumber));
      expect(block).to.not.be.null;
      await expect(tx)
        .to.emit(evoting, "VoteCast")
        .withArgs(0, voterA.address, 0, block!.timestamp);
      expect(await evoting.hasVoted(0, voterA.address)).to.be.true;
      expect(await evoting.getVoteCount(0, 0)).to.equal(1);
      expect(await evoting.hasVotedForElection(0, voterA.address)).to.be.true;
    });

    it("reverts second vote from same voter (double vote)", async function () {
      const { evoting, voterA } = await loadFixture(electionReadyFixture);
      await evoting.connect(voterA).vote(0, 0);
      await expect(evoting.connect(voterA).vote(0, 1)).to.be.revertedWithCustomError(
        evoting,
        "AlreadyVoted"
      );
    });

    it("reverts vote for invalid candidate index", async function () {
      const { evoting, voterA } = await loadFixture(electionReadyFixture);
      await expect(evoting.connect(voterA).vote(0, 99)).to.be.revertedWithCustomError(
        evoting,
        "InvalidCandidate"
      );
    });

    it("reverts vote before startTime", async function () {
      const { evoting, admin, voterA } = await loadFixture(deployFixture);
      const start = (await time.latest()) + 100;
      const end = start + 3600;
      await evoting.connect(admin).createElection(start, end);
      await evoting.connect(admin).addCandidates(0, 3);
      await expect(evoting.connect(voterA).vote(0, 0)).to.be.revertedWithCustomError(
        evoting,
        "ElectionNotStarted"
      );
    });

    it("reverts vote after endTime", async function () {
      const { evoting, voterA } = await loadFixture(electionReadyFixture);
      const [, endTime] = await evoting.getElection(0);
      await time.increaseTo(Number(endTime) + 1);
      await expect(evoting.connect(voterA).vote(0, 0)).to.be.revertedWithCustomError(
        evoting,
        "ElectionEnded"
      );
    });

    it("reverts vote for non-existent election", async function () {
      const { evoting, voterA } = await loadFixture(electionReadyFixture);
      await expect(evoting.connect(voterA).vote(99, 0)).to.be.revertedWithCustomError(
        evoting,
        "ElectionDoesNotExist"
      );
    });

    it("reverts vote for candidate index not in isCandidate (out of range)", async function () {
      const { evoting, voterA } = await loadFixture(electionReadyFixture);
      await expect(evoting.connect(voterA).vote(0, 3)).to.be.revertedWithCustomError(
        evoting,
        "InvalidCandidate"
      );
    });
  });

  describe("Tally", function () {
    it("getVoteCount and candidateVoteCount match after multiple voters", async function () {
      const { evoting, voterA, voterB } = await loadFixture(electionReadyFixture);
      await evoting.connect(voterA).vote(0, 0);
      await evoting.connect(voterB).vote(0, 1);
      expect(await evoting.getVoteCount(0, 0)).to.equal(1);
      expect(await evoting.getVoteCount(0, 1)).to.equal(1);
      expect(await evoting.getVoteCount(0, 2)).to.equal(0);
      expect(await evoting.candidateVoteCount(0, 0)).to.equal(1);
      expect(await evoting.candidateVoteCount(0, 1)).to.equal(1);
    });

    it("voteChoice stores voter choice for receipt lookup", async function () {
      const { evoting, voterA } = await loadFixture(electionReadyFixture);
      await evoting.connect(voterA).vote(0, 2);
      expect(await evoting.voteChoice(0, voterA.address)).to.equal(2);
    });
  });

  describe("Access control", function () {
    it("non-admin cannot create election", async function () {
      const { evoting, nonAdmin } = await loadFixture(deployFixture);
      const start = (await time.latest()) + 60;
      const end = start + 3600;
      await expect(
        evoting.connect(nonAdmin).createElection(start, end)
      ).to.be.revertedWithCustomError(evoting, "AccessControlUnauthorizedAccount");
    });

    it("non-admin cannot add candidates", async function () {
      const { evoting, admin, nonAdmin } = await loadFixture(deployFixture);
      const start = (await time.latest()) + 60;
      const end = start + 3600;
      await evoting.connect(admin).createElection(start, end);
      await expect(
        evoting.connect(nonAdmin).addCandidates(0, 3)
      ).to.be.revertedWithCustomError(evoting, "AccessControlUnauthorizedAccount");
    });
  });
});
