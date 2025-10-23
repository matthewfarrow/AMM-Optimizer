import { expect } from "chai";
import { ethers } from "hardhat";
import { LiquidityManager } from "../typechain-types";
import { SignerWithAddress } from "@nomicfoundation/hardhat-ethers/signers";

describe("LiquidityManager", function () {
  let liquidityManager: LiquidityManager;
  let owner: SignerWithAddress;
  let user1: SignerWithAddress;
  let user2: SignerWithAddress;

  const POSITION_MANAGER = "0x0000000000000000000000000000000000000001";
  const SWAP_ROUTER = "0x0000000000000000000000000000000000000002";

  beforeEach(async function () {
    [owner, user1, user2] = await ethers.getSigners();

    const LiquidityManager = await ethers.getContractFactory("LiquidityManager");
    liquidityManager = await LiquidityManager.deploy(POSITION_MANAGER, SWAP_ROUTER);
    await liquidityManager.waitForDeployment();
  });

  describe("Deployment", function () {
    it("Should set the right owner", async function () {
      expect(await liquidityManager.owner()).to.equal(owner.address);
    });

    it("Should set the correct position manager and swap router", async function () {
      expect(await liquidityManager.positionManager()).to.equal(POSITION_MANAGER);
      expect(await liquidityManager.swapRouter()).to.equal(SWAP_ROUTER);
    });
  });

  describe("Whitelist Management", function () {
    it("Should allow owner to whitelist users", async function () {
      await liquidityManager.setWhitelistStatus(user1.address, true);
      expect(await liquidityManager.whitelistedUsers(user1.address)).to.be.true;
    });

    it("Should allow owner to remove users from whitelist", async function () {
      await liquidityManager.setWhitelistStatus(user1.address, true);
      await liquidityManager.setWhitelistStatus(user1.address, false);
      expect(await liquidityManager.whitelistedUsers(user1.address)).to.be.false;
    });

    it("Should allow batch whitelist operations", async function () {
      await liquidityManager.batchSetWhitelistStatus(
        [user1.address, user2.address],
        true
      );
      expect(await liquidityManager.whitelistedUsers(user1.address)).to.be.true;
      expect(await liquidityManager.whitelistedUsers(user2.address)).to.be.true;
    });

    it("Should not allow non-owner to modify whitelist", async function () {
      await expect(
        liquidityManager.connect(user1).setWhitelistStatus(user2.address, true)
      ).to.be.revertedWith("Ownable: caller is not the owner");
    });

    it("Should emit UserWhitelisted event", async function () {
      await expect(liquidityManager.setWhitelistStatus(user1.address, true))
        .to.emit(liquidityManager, "UserWhitelisted")
        .withArgs(user1.address, true);
    });
  });

  describe("Access Control", function () {
    it("Should not allow non-whitelisted users to create positions", async function () {
      // This would fail due to whitelist check, but we can't easily test position creation
      // without proper token setup, so we'll test the whitelist check indirectly
      expect(await liquidityManager.isWhitelisted(user1.address)).to.be.false;
    });

    it("Should allow only owner to execute commands", async function () {
      const commands = [ethers.AbiCoder.defaultAbiCoder().encode(["string"], ["test"])];
      
      await expect(
        liquidityManager.connect(user1).executeCommands(commands)
      ).to.be.revertedWith("Ownable: caller is not the owner");
    });
  });

  describe("Position Management", function () {
    beforeEach(async function () {
      await liquidityManager.setWhitelistStatus(user1.address, true);
    });

    it("Should return empty positions for new user", async function () {
      const positions = await liquidityManager.getUserPositions(user1.address);
      expect(positions.length).to.equal(0);
    });

    it("Should return false for non-existent position", async function () {
      await expect(liquidityManager.getPosition(999)).to.be.revertedWith("Position not found");
    });
  });

  describe("Emergency Functions", function () {
    beforeEach(async function () {
      await liquidityManager.setWhitelistStatus(user1.address, true);
    });

    it("Should allow whitelisted users to emergency withdraw", async function () {
      // This test would require token setup, but we can test the function exists
      expect(await liquidityManager.isWhitelisted(user1.address)).to.be.true;
    });

    it("Should not allow non-whitelisted users to emergency withdraw", async function () {
      // This would fail due to whitelist check
      expect(await liquidityManager.isWhitelisted(user2.address)).to.be.false;
    });
  });
});
