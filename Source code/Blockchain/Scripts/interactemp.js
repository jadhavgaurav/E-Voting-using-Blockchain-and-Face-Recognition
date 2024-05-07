
// interact.js
var ethers = require('ethers');
if (process.env.NODE_ENV !== 'production') {
    require('dotenv').config();
}
const contract = require("../build/contracts/Votingsol.json");

const PRIVATE_KEY = process.env.PRIVATE_KEY_LOCAL;
const CONTRACT_ADDRESS = process.env.CONTRACT_ADDRESS_LOCAL;

const etherProvider = new ethers.providers.JsonRpcProvider();

// signer - you
const signer = new ethers.Wallet(PRIVATE_KEY, etherProvider);

// contract instance
const coupDetailsContract = new ethers.Contract(CONTRACT_ADDRESS, contract.abi, signer);

main();

//function
async function main() {

    console.log("Add Candidate...");
    console.log(CONTRACT_ADDRESS);
   /*
    //add candidate --working
    try{
    const txResponse = await coupDetailsContract.addCandidate("Sudhakar","TestElection1","4b76d5fb.png");
    console.log("Transaction value: " + txResponse);
    const receipt = await txResponse.wait();
    console.log("Transaction hash: " + txResponse.hash);
    //get candidates count
    const candidatecount = await coupDetailsContract.getCandidatecount();
    console.log("Transaction receipt: " + candidatecount);
    
    }
    catch (error)
    {
        console.log("Transaction error: " + error);
    }*/ 
    //vote for candidate
    try{const vote = await coupDetailsContract.vote(20,"qwerty");
    
    const receipt = await vote.wait();
    console.log("receipt"+receipt);
    console.log("Transaction hash: " + vote.hash);
    }
    catch (error)
    {
        console.log("Transaction error: " + error);
    } 
    
    //getcoupon -working
        console.log("Get Candidtes with id and symbol...");
        const txResponse = await coupDetailsContract.getCandidates("postelection");
        console.log("The new message is txReceipt: " + txResponse);
        console.log("Get Candidtes with vote count...");
        const txResponse1 = await coupDetailsContract.getCandidatesname("postelection");
        console.log("The new message is txReceipt: " + txResponse1);
    /*    const numCabdidate = txResponse[0].length;
        const FIELD_CAND  = 0
        let FIELD_VOTES = 1
        
        let candidStructs = []
        for (let i = 0; i < numCabdidate; i++) {
        if (txResponse[FIELD_CAND][i] !=="")
        {
        const candidate = {
        cand:  txResponse[FIELD_CAND][i],
        votes: txResponse[FIELD_VOTES][i],
        }
        
        candidStructs.push(candidate)
        }

       
        
}

console.log('peopleStructs =', candidStructs)*/
       
const txResponsec = await coupDetailsContract.getCandidatecount();
console.log("The total candidates count is : " + txResponsec);
}

