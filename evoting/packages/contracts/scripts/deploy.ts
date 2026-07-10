import { ethers, network } from "hardhat";
import * as fs from "fs";
import * as path from "path";

/**
 * Deploy EVoting and write the address + ABI to deployments/<network>.json so the
 * backend and web app can consume them. The deployer receives ADMIN_ROLE.
 */
async function main(): Promise<void> {
  const [deployer] = await ethers.getSigners();
  const adminAddress = process.env.ADMIN_ADDRESS ?? deployer.address;

  console.log(`Network:  ${network.name} (chainId ${network.config.chainId})`);
  console.log(`Deployer: ${deployer.address}`);
  console.log(`Admin:    ${adminAddress}`);

  const factory = await ethers.getContractFactory("EVoting");
  const contract = await factory.deploy(adminAddress);
  await contract.waitForDeployment();

  const address = await contract.getAddress();
  console.log(`EVoting deployed at: ${address}`);

  const artifact = await import("../artifacts/contracts/EVoting.sol/EVoting.json");
  const outDir = path.resolve(__dirname, "../deployments");
  fs.mkdirSync(outDir, { recursive: true });

  const record = {
    network: network.name,
    chainId: Number(network.config.chainId ?? 0),
    address,
    admin: adminAddress,
    deployedAt: new Date().toISOString(),
    abi: artifact.abi,
  };

  const outFile = path.join(outDir, `${network.name}.json`);
  fs.writeFileSync(outFile, JSON.stringify(record, null, 2));
  // Also write a stable "latest" pointer the services read by default.
  fs.writeFileSync(path.join(outDir, "latest.json"), JSON.stringify(record, null, 2));

  console.log(`Deployment written to: ${outFile}`);
  console.log(`Set EVOTING_CONTRACT_ADDRESS=${address} in your .env`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
