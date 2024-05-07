module.exports = {
  // See <http://truffleframework.com/docs/advanced/configuration>
  // for more about customizing your Truffle configuration!
  networks: {
    development: {
      host: "127.0.0.1",
      port: 8545,
      network_id: "*", // Match any network id      
	    gas: 6721975, // Use `gas` & `gasPrice` only if creating type 0 transactions
      gasPrice: 2000000000, // (20 Gwei) All gas values specified in wei
      // maxFeePerGas: 10, // Use only if creating type 2 transactions
      maxPriorityFeePerGas: 10
    }
  },
  compilers: {
    solc: {
        version: "0.8.0" ,
		settings: {
        optimizer: {
          enabled: true,
          runs: 200,
        },
        evmVersion: "istanbul", // homestead, tangerineWhistle, spuriousDragon, byzantium, constantinople, petersburg, istanbul or berlin
    }
}
  }
};
