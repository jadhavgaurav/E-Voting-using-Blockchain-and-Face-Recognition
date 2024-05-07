<?php
?>
<script type="text/javascript" src="js/jquery-1.11.1.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/web3/1.8.1/web3.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/truffle-contract@4.0.16/dist/truffle-contract.js"></script>



<form name="sendMail" id="sendMailForm">
		<div class="form-group user-name">
			<label for="name" class="sr-only">Name</label>
			<!-- "id" for taking name -->
			<input type="text" class="form-control" required="" id="name" placeholder="First Name">
		</div>
		<div class="form-group user-email">
			<label for="email" class="sr-only">Email</label>
			<!-- "id" for taking email -->
			<input type="email" class="form-control" required="" id="email" placeholder="Email Address">
		</div>
		<div class="form-group user-phone">
			<label for="contactNumber" class="sr-only">Contact Number</label>
			<!-- "id" for taking contact number -->
			<input type="text" class="form-control" required="" id="contactNumber" placeholder="Phone">
		</div>
		<div class="form-group user-message">
			<label for="message" class="sr-only">Message</label>
			<!-- "id" for taking message -->
			<textarea class="form-control" required="" id="message" placeholder="Write Message"></textarea>
		</div>
	<!-- Notifications for 'error' Or 'successfully'-->
		<div class="col-md-12 mailResponse" style="display:none;">
			<div class="alert alert-dismissible" role="alert">
				<button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">×</span></button>
				<p class="mailResponseText"></p>
			</div>
		</div>
	<!-- submit button -->
	<button type="submit" class="btn btn-primary">Send Message <i class="fa fa-paper-plane"></i></button>
</form>

 <script>
 
// #sendMailForm takes the data from the form with given ID
$( '#sendMailForm' ).submit(function ( e ) {
    var data = {
        'vname': ename,
        'email': $('#email').val()        
    };
    // POST data to the php file
	console.log("js");
    $.ajax({ 
        url: 'mail.php', 
        data: data,
        type: 'POST',
        success: function (data) {
			// For Notification
            document.getElementById("sendMailForm").reset();
            var $alertDiv = $(".mailResponse");
            $alertDiv.show();
            $alertDiv.find('.alert').removeClass('alert-danger alert-success');
            $alertDiv.find('.mailResponseText').text("");
            if(data.error){
                $alertDiv.find('.alert').addClass('alert-danger');
                $alertDiv.find('.mailResponseText').text(data.message);
            }else{
                $alertDiv.find('.alert').addClass('alert-success');
                $alertDiv.find('.mailResponseText').text(data.message);
            }
        }
    });
    e.preventDefault();
});

 </script>
 
 <script type="text/javascript" src="assets/js/bootstrap-3.1.1.min.js"></script>
<script type="text/javascript"> 


       /*if (typeof web3 !== 'undefined') {
           web3 = new Web3(web3.currentProvider);
       } else {*/
           web3 = new Web3(new Web3.providers.HttpProvider("http://localhost:8545"));
       //}

       web3.eth.defaultAccount = web3.eth.accounts[0];
		//const contract = require('Votingsol.json');
		 //const contract = JSON.parse(Votingsol);
        var PNBContract = new web3.eth.Contract([
    {
      "anonymous": false,
      "inputs": [
        {
          "indexed": true,
          "internalType": "uint256",
          "name": "id",
          "type": "uint256"
        }
      ],
      "name": "votedEvent",
      "type": "event"
    },
    {
      "inputs": [],
      "name": "candidateCount",
      "outputs": [
        {
          "internalType": "uint256",
          "name": "",
          "type": "uint256"
        }
      ],
      "stateMutability": "view",
      "type": "function",
      "constant": true
    },
    {
      "inputs": [
        {
          "internalType": "uint256",
          "name": "",
          "type": "uint256"
        }
      ],
      "name": "candidateLookup",
      "outputs": [
        {
          "internalType": "uint256",
          "name": "id",
          "type": "uint256"
        },
        {
          "internalType": "string",
          "name": "name",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "electionName",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "symbol",
          "type": "string"
        },
        {
          "internalType": "uint256",
          "name": "voteCount",
          "type": "uint256"
        }
      ],
      "stateMutability": "view",
      "type": "function",
      "constant": true
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "",
          "type": "address"
        },
        {
          "internalType": "string",
          "name": "",
          "type": "string"
        }
      ],
      "name": "votedUser",
      "outputs": [
        {
          "internalType": "bool",
          "name": "",
          "type": "bool"
        }
      ],
      "stateMutability": "view",
      "type": "function",
      "constant": true
    },
    {
      "inputs": [
        {
          "internalType": "string",
          "name": "name",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "electionName",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "symbol",
          "type": "string"
        }
      ],
      "name": "addCandidate",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "getCandidatecount",
      "outputs": [
        {
          "internalType": "uint256",
          "name": "",
          "type": "uint256"
        }
      ],
      "stateMutability": "view",
      "type": "function",
      "constant": true
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "_Id",
          "type": "address"
        },
        {
          "internalType": "string",
          "name": "_name",
          "type": "string"
        },
        {
          "internalType": "bool",
          "name": "_status",
          "type": "bool"
        }
      ],
      "name": "addVoter",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "_Id",
          "type": "address"
        },
        {
          "internalType": "string",
          "name": "_name",
          "type": "string"
        }
      ],
      "name": "getVoter",
      "outputs": [
        {
          "internalType": "bool",
          "name": "",
          "type": "bool"
        }
      ],
      "stateMutability": "view",
      "type": "function",
      "constant": true
    },
    {
      "inputs": [
        {
          "internalType": "string",
          "name": "electionName",
          "type": "string"
        }
      ],
      "name": "getCandidates",
      "outputs": [
        {
          "internalType": "string[]",
          "name": "",
          "type": "string[]"
        }
      ],
      "stateMutability": "view",
      "type": "function",
      "constant": true
    },
    {
      "inputs": [
        {
          "internalType": "string",
          "name": "electionName",
          "type": "string"
        }
      ],
      "name": "getCandidatesname",
      "outputs": [
        {
          "internalType": "string[]",
          "name": "",
          "type": "string[]"
        }
      ],
      "stateMutability": "view",
      "type": "function",
      "constant": true
    },
    {
      "inputs": [
        {
          "internalType": "uint256",
          "name": "id",
          "type": "uint256"
        },
        {
          "internalType": "string",
          "name": "electionName",
          "type": "string"
        }
      ],
      "name": "vote",
      "outputs": [
        {
          "internalType": "uint256",
          "name": "uid",
          "type": "uint256"
        }
      ],
      "stateMutability": "nonpayable",
      "type": "function"
    }
  ],"0xE0780150EE5A1f716fE9f33Edb82614D8e89Faf3");

       //var PNB = PNBContract.at('0xE0780150EE5A1f716fE9f33Edb82614D8e89Faf3');
		//console.log(PNB);
			//get candidate count
			/*PNBContract.methods.getCandidatecount().call().then(console.log);
			PNBContract.methods.getCandidatecount().call(function (err, res){
           			if (!err) {
						console.log(res);
           			
            		//$("#countIns").html(res.c + ' Borrowers');
            		//for(i = 1; i < res; i++) {
            			//out += ' , '+ i;
            		//}
            		//$("#loanes").html(out); 
					//console.log("count"+out);
            	}
				else
				{
					console.log(err);
				}
      		 	});*/
			
		   //Add Candidate 
			/*PNB.addCandidate("XYZA1","TestElection2" , {
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
           );*/
		   /*PNBContract.methods.getCandidates("TestElection1").call().then(console.log);
		   PNBContract.methods.getCandidatesname("TestElection1").call(function(err, res){
           			if (res) {
						console.log("inside");
						
						console.log(res);     
						var out =res;						
		            	}
				else
				{
					console.log(err);
				}
      		 	});*/
				
			/*PNB.getCandidatesname( "TestElection2", (err, res) => {
           		if (res) {
						console.log("insidename");
						console.log(res.length);
						var out =res;
					var iterator = res.values();
					for (let elements of iterator) {
						if (elements != "")
						{
					  console.log(elements);
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
				
				
	/*async function f() {			
				// Get Contract
    $.getJSON('./contract/Votingsol.json', function (data) {
        // Get the necessary contract artifact file and instantiate it with truffle-contract
        var VotingArtifact = data;
        var VotingContract = TruffleContract(VotingArtifact);

        // Set the provider for our contract
        VotingContract.setProvider(web3);

        console.log("VotingContract:")
        console.log(VotingContract)
    	
	  const account = "0x437e0Ba4953F13869086d39496Cc50379271e208";
	  var proposalsInstance;
	  VotingContract.deployed().then(function(instance) {
        proposalsInstance = instance;
		console.log("inside instance");
      //  proposalsInstance.getCandidates.call("Electionname").then(function(numProposals) {
        //  var wrapperProposals = $('#wrapperProposals');
        //  wrapperProposals.empty();
        //  var proposalTemplate = $('#proposalTemplate');
        //  for (var i=0; i<numProposals; i++) {
            proposalsInstance.getCandidates.call("TestElection1").then(function(data) {
              var idx = data[0];
			  
			  console.log("data"+data);
              /*proposalTemplate.find('.panel-title').text(data[1]);
              proposalTemplate.find('.numVotesPos').text(data[2]);
              proposalTemplate.find('.numVotesNeg').text(data[3]);
              proposalTemplate.find('.numVotesAbs').text(data[4]);
              proposalTemplate.find('.btn-vote').attr('data-proposal', idx);
              proposalTemplate.find('.btn-vote').attr('disabled', false);
              for (j=0; j<data[5].length; j++) {
				  console.log(data[5][j]);
                if (data[5][j].localeCompare(account)) {
					console.log("Disabled");
                  proposalTemplate.find('.btn-vote').attr('disabled', true);
                }
              }
              wrapperProposals.append(proposalTemplate.html());*/
   //         }).catch(function(err) {
  //            console.log(err.message);
   //         });
   //      // }
  //      }).catch(function(err) {
   //       console.log(err.message);
   //     });
     // });

	//});   /*$("button").click(function () {
     //       FriendContract.setFriend($("name").val(), $("age").val())
   //     })*/
  //  });
//		}   */
       
</script> 


