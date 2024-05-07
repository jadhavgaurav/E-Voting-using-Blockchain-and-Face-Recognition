<?php
?>
<script type="text/javascript" src="js/jquery-1.11.1.min.js"></script>
<script src="js/web3.min.js"></script>
<script src="js/truffle-contract.js"></script>

 
<script type="text/javascript"> 
		
		$.getJSON('./contract/Votingsol.json', function (data) {			
		
		var web3 = new Web3(new Web3.providers.HttpProvider('http://localhost:8545'));
		//let account = await web3.eth.accounts.privateKeyToAccount('0x'+privateKey);
		//web3.eth.defaultAccount = web3.eth.accounts[0];
		console.log(data.abi);
		PNBContract = web3.eth.contract(data.abi);
		console.log(PNBContract);
		var PNB = PNBContract.at('0xE943E0fe9618Bf05C01ed154C43CddF969A602AF');
		console.log(PNB);
		
		//get candidate count
		PNB.getCandidatecount((err, res) => {
           		if (res) {
						console.log("count"+res);
            	}
      		 	});
		
		//Add Candidate 
		PNB.addCandidate("XYZA1","TestElection2","file.jpg" , {
            from:"0x437e0Ba4953F13869086d39496Cc50379271e208",
            gas:4000000}, (err, res) => {
               if (err) {
                   console.log("error in set!")
                   //$("#loader").hide();
               }
			   else
			   {console.log(res);
			   }
			}
           );
		//get candidate names
		PNB.getCandidatesname("TestElection2", (err, res) => {
           		if (res) {
						console.log("insidename");
						console.log(res.length);
						var out =res;
						console.log(res);
					var iterator = res.values();
					for (let elements of iterator) {
						if (elements != "")
						{
					
						var text = elements;
						console.log(text);
						const myArray = text.split("-");
						console.log(myArray[1]);
						}
					}						
		
            	}
				if(err)
				{
					console.log(err);
				}
      		 	});
		//Voting 
		/*PNB.vote(0,"TestElection2" , {
            from:"0x4a7A9DC2a45Def5e58757a32e1a83A075F8EEE56",
            gas:4000000}, (err, res) => {
               if (err) {
                   console.log("error in set!")                   
               }
			   else
			   {console.log(res);
			   }
			}
           );*/			
		
		});
		
</script> 
