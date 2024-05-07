// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.0;
pragma experimental ABIEncoderV2;
import "@openzeppelin/contracts/utils/Strings.sol";


//pragma experimental ABIEncoderV2;

contract Votingsol {


struct Candidate {
        uint id;
        string name;
        string electionName;
        string symbol;
        uint voteCount;
    }

//struct VotedUser {
//    string electionname;    
//   mapping(address => string) voterLookup;
//}
	mapping(address=>mapping(string=>bool)) public votedUser;
    //mapping(address => bool) public voterLookup;
    //input Election Name to 
    //mapping(address => string) public voterLookup;
    
	mapping(uint => Candidate) public candidateLookup; // Each candidate will be identified with a unique ID

	uint public candidateCount; // Keeps a track of the number of candidates and also fulfills the function to generate a unique ID

function addCandidate(string memory name,string memory electionName,string memory symbol) external {
  candidateLookup[candidateCount] = Candidate(candidateCount, name,electionName,symbol, 0);
  candidateCount++;   
}

function getCandidatecount() external view returns (uint){
  return candidateCount;   
}

function addVoter(address _Id,string memory _name, bool _status)public {
    		votedUser[_Id][_name]=_status;
    }

function getVoter(address _Id,string memory _name)public view returns(bool)
	{
  		return votedUser[_Id][_name];
  }

function getCandidates(string memory electionName) external view returns (string[] memory) {
//function getCandidates(string memory electionName) external view returns (string[] memory, uint[] memory) {
    string[] memory names = new string[](candidateCount);    
   // uint[] memory voteCounts = new uint[](candidateCount);
    //uint count=2;
    //names[0]="test";
    for (uint i = 0; i < candidateCount; i++) {        
        //check the length of both string to reduce gas expenses
        if (bytes(candidateLookup[i].electionName).length == bytes(electionName).length) {
            if ( keccak256(abi.encodePacked(candidateLookup[i].electionName)) == keccak256(abi.encodePacked(electionName)))
            {
                    string memory name = string(abi.encodePacked(candidateLookup[i].name,"-"));
                    name = string(abi.encodePacked(name,candidateLookup[i].symbol));
                    name = string(abi.encodePacked(name,"-"));
                    names[i]=string(abi.encodePacked(name,Strings.toString(i)));
                   // voteCounts[i] = candidateLookup[i].voteCount;
            }

        }
        
    }
    //names[candidateCount]="test";
    //return (names, voteCounts);
    return(names);
}

function getCandidatesname(string memory electionName) external view returns (string[] memory) {
//function getCandidates(string memory electionName) external view returns (string[] memory, uint[] memory) {
    string[] memory names = new string[](candidateCount);    
    //string[] memory voteCounts = new string[](candidateCount);
    //uint count=2;
    for (uint i = 0; i < candidateCount; i++) {        
        //check the length of both string to reduce gas expenses
        if (bytes(candidateLookup[i].electionName).length == bytes(electionName).length) {
            if ( keccak256(abi.encodePacked(candidateLookup[i].electionName)) == keccak256(abi.encodePacked(electionName)))
            {
                    string memory name = string(abi.encodePacked(candidateLookup[i].name,"-"));
                    names[i] = string(abi.encodePacked(name,Strings.toString(candidateLookup[i].voteCount)));
                    //voteCounts[i] = string(abi.encode(candidateLookup[i].voteCount));                    
            }

        }
        
    }
    //names[candidateCount]="test";
    return (names);
    //return(names);
}

    function vote(uint id,string memory electionName) external returns (uint uid){
         
    //    bool status = getVoter(msg.sender,electionName);
    //    if(!status)
    //    {
        require (id >= 0 && id <= candidateCount-1);                
        candidateLookup[id].voteCount++;
        addVoter(msg.sender,electionName,true);
        emit votedEvent(id);
        return(id);
    //    }
    }

    event votedEvent(uint indexed id);
   
  
}