import { ethers } from "hardhat";
import * as fs from "fs";
import * as path from "path";

async function main() {
  const [deployer] = await ethers.getSigners();
  const network = await ethers.provider.getNetwork();
  const chainId = Number(network.chainId);

  console.log("Deploying EVoting with account:", deployer.address);
  console.log("Network chainId:", chainId);

  const EVoting = await ethers.getContractFactory("EVoting");
  const evoting = await EVoting.deploy();
  await evoting.waitForDeployment();
  const address = await evoting.getAddress();

  console.log("EVoting deployed to:", address);

  // ADMIN_ROLE is granted to deployer in constructor; no extra grant needed.

  const abiPath = path.join(
    __dirname,
    "../artifacts/contracts/EVoting.sol/EVoting.json"
  );
  const artifactPath = path.relative(process.cwd(), abiPath);

  const deploymentsDir = path.join(__dirname, "../deployments");
  if (!fs.existsSync(deploymentsDir)) {
    fs.mkdirSync(deploymentsDir, { recursive: true });
  }

  const deployment = {
    chainId,
    EVoting: {
      address,
      abiPath: "./artifacts/contracts/EVoting.sol/EVoting.json",
    },
  };

  const defaultPath = path.join(deploymentsDir, "default.json");
  fs.writeFileSync(defaultPath, JSON.stringify(deployment, null, 2), "utf-8");
  console.log("Deployment artifact written to:", path.relative(process.cwd(), defaultPath));

  console.log("\n--- Backend consumption ---");
  console.log("ABI path:", deployment.EVoting.abiPath);
  console.log("Contract address:", address);
  console.log("Chain ID:", chainId);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
