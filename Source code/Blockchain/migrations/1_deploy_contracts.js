var Votingsol = artifacts.require("Votingsol");

module.exports = function(deployer, network, accounts) {
  deployer.deploy(Votingsol);
};
