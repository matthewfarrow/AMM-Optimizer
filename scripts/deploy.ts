import { ethers } from "hardhat";

async function main() {
  console.log("Deploying LiquidityManager...");

  // Base Network addresses (Base Sepolia)
  const POSITION_MANAGER = "0x03a520b32C04BF3bEEf7BFdF5497F0D5c9b18b5b"; // Uniswap V3 Position Manager on Base Sepolia
  const SWAP_ROUTER = "0x2626664c2603336E57B271c5C0b26F421741e481"; // Uniswap V3 SwapRouter on Base Sepolia

  const LiquidityManager = await ethers.getContractFactory("LiquidityManager");
  const liquidityManager = await LiquidityManager.deploy(POSITION_MANAGER, SWAP_ROUTER);

  await liquidityManager.waitForDeployment();

  const address = await liquidityManager.getAddress();
  console.log(`LiquidityManager deployed to: ${address}`);

  // Whitelist the deployer initially
  const [deployer] = await ethers.getSigners();
  console.log(`Deployer address: ${deployer.address}`);
  
  const tx = await liquidityManager.setWhitelistStatus(deployer.address, true);
  await tx.wait();
  console.log(`Deployer whitelisted: ${tx.hash}`);

  console.log("Deployment complete!");
  console.log(`Contract address: ${address}`);
  console.log(`Deployer: ${deployer.address}`);
  console.log(`Position Manager: ${POSITION_MANAGER}`);
  console.log(`Swap Router: ${SWAP_ROUTER}`);
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
