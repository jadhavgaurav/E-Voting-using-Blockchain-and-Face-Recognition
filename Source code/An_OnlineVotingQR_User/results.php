<?PHP
require "util.php";

/*$sql = "select distinct ename,etype,edate,subtype from electioninfo where status='2' order by edate DESC limit 1";
//echo $sql; 
$res = $db->query($sql);
$result= Array();   
$i=0;
         while ($row = $res->fetch_assoc()) {
          $result[$i]=$row;
          $i=$i+1;
         }
         if($i==0){
             
             $result1['ename']='No Records Found';
             $result1['etype']=' ';
             $result1['edate']=' ';
             $result1['subtype']=' ';
             $result[0]=$result1;
			 echo $result[0];
             
            // [{"ename":"State Election 2018","etype":"state","edate":"0012-12-12","subtype":"Mylapore"}]
             
         }

*/

?>
<!DOCTYPE HTML>
<html>
<head>
<title>Election a Society and People Category </title>
<!-- for-mobile-apps -->
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<meta name="keywords" content="Election Responsive web template, Bootstrap Web Templates, Flat Web Templates, Android Compatible web template,
Smartphone Compatible web template, free webdesigns for Nokia, Samsung, LG, SonyEricsson, Motorola web design" />
<script type="application/x-javascript"> addEventListener("load", function() { setTimeout(hideURLbar, 0); }, false);
function hideURLbar(){ window.scrollTo(0,1); } </script>
<!-- //for-mobile-apps -->
<link href="assets/css/bootstrap.css" rel='stylesheet' type='text/css' />
<link href='//fonts.googleapis.com/css?family=Raleway:400,100,200,300,500,600,700,800,900' rel='stylesheet' type='text/css'>
<link href='//fonts.googleapis.com/css?family=Open+Sans:400,300,300italic,400italic,600,600italic,700,700italic,800,800italic' rel='stylesheet' type='text/css'>
<link rel="stylesheet" type="text/css" href="assets/css/style.css">
<!---strat-slider---->
<script type="text/javascript" src="assets/js/jquery-1.11.1.min.js"></script>
<script type="text/javascript" src="assets/js/canvasjs.min.js"></script>
<script type="text/javascript" src="assets/js/jquery.canvasjs.min.js"></script>

<script src="https://cdnjs.cloudflare.com/ajax/libs/web3/1.8.1/web3.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/truffle-contract@4.0.16/dist/truffle-contract.js"></script>
<script type="text/javascript" src="config.js"></script>
<!---//-slider---->
<script>
var chart ;
window.onload = function() {

chart = new CanvasJS.Chart("chartContainer", {
	animationEnabled: true,
	title: {
		text: ""
	},
	data: [{
		type: "pie",
		startAngle: 240,
		yValueFormatString: "##0.00\"%\"",
		indexLabel: "{label} {y}",
		dataPoints: [
			{y: 79.45,label: "Party1"},
			{y: 7.31, label: "Party2"},
			{y: 7.06, label: "Party3"},
			{y: 4.91, label: "Party4"},
			{y: 1.26, label: "Party5"}
			
		]
	}]
});

chart.render();

}
</script>
<script>
/*
This script is identical to the above JavaScript function.
*/
$(document).ready(function(){
   
$('#etype').on('change', function() {
if(this.value!="-------CHOOSE Election-------"){
$.getJSON( "./getlist.php?type="+this.value, function( data ) {
 var listitems = '';
$.each(data, function(key, value){
    listitems += '<option value="' + key + '">' + value + '</option>';
});
$("#subtype").find('option').remove();
$("#subtype").append('<option >CHOOSE Constituency</option>');
$("#subtype").append(listitems);
});
  }
  else{
    $("#subtype").find('option').remove();
$("#subtype").append('<option >CHOOSE Constituency</option>');
  }
});

    $('#search').on('click', function() {
    $("#target_table_id tbody tr").remove();
    $("#resdiv").css("display","none");
    etype=$("#etype").val();
    stype=$("#subtype").val();
	console.log(stype);
  $.getJSON("./fetchElectionResList.php?etype="+etype+"&subtype="+stype , function(data) {
    var tbl_body = document.createElement("tbody");
    var odd_even = false;
    $("#target_table_id tbody tr").remove();
    $.each(data, function() {
        var tbl_row = tbl_body.insertRow();
        tbl_row.className = odd_even ? "odd rrow" : "even rrow";
        $.each(this, function(k , v) {
            var cell = tbl_row.insertCell();
            console.log(v.toString(),k.toString());
            if(k.toString()=="ename"){
            cell.appendChild(document.createTextNode(v.toString()));
        }
        else
            cell.appendChild(document.createTextNode(v.toString()));
        })        
        odd_even = !odd_even;               
    })
     $("#target_table_id").append(tbl_body);
     $(".rrow").click(function(){
        //+$(this).prop('id')
        console.log("row clicked");
    row=this;
    elnam=$(row).children()[0];
    elnam=$(elnam).text();
    eltype=$(row).children()[1];
    eltype=$(eltype).text();
    eldate=$(row).children()[2];
    eldate=$(eldate).text();
    elsubtype=$(row).children()[3];
    elsubtype=$(elsubtype).text();
    
       // updateResult(elnam,eltype,eldate,elsubtype);
		getcandidates(elnam);
    });
   
});
});
});

function getcandidates(ename)
	{
		$.getJSON('./contract/Votingsol.json', function (data) {			
		
		var web3 = new Web3(new Web3.providers.HttpProvider('http://localhost:8545'));
		console.log("contract");
		console.log(data.abi);
		web3.eth.net.isListening()
		.then(() => {
		console.log('is connected');
		PNBContract = new web3.eth.Contract(data.abi,gOptions.contractaddress);		
		chart.data[0].dataPoints.splice(0);
		total=0;
		var iterator;
		PNBContract.methods.getCandidatesname(ename).call(function(err, res){
		      		if (res) {
						//console.log("insidename");
						console.log(res.length);
						var out =res;
						console.log(res);
						iterator = res.values();
					//console.log(iterator); to get total no of votes
					for (let elements of iterator ) {
						if (elements != "" && elements !== 'test')
						{					
						var text = elements;						
						const myArray = text.split("-");
						var candidate = myArray[0];
						var vote = myArray[1];						
						
						total =total+ parseInt(vote);//,10); 
						console.log(candidate);						
						console.log(total);
						
						}
						
					}	
					console.log(total);
					iterator = res.values();
					//console.log(iterator);
					//Chart code starts
					$("#candilist tbody tr").remove();
					var tbl_body = document.createElement("tbody");
					for (let elements of iterator) {
						if (elements != "" && elements !== 'test')
						{					
						//	for(i=0;i<data.length;i++){
						//		console.log(data[i]);
							var text = elements;						
							const myArray = text.split("-");
							var candidate = myArray[0];
							var vote = myArray[1];
							console.log(candidate);
							//rr=data[i];
							perc=(vote/total)*100;
							console.log(perc);
							//name=rr['cname'];
							chart.data[0].dataPoints.push({y:perc,label:candidate});
								
							var tbl_row = tbl_body.insertRow();
							var cell = tbl_row.insertCell();
									
							cell.appendChild(document.createTextNode(candidate));
							var cell1 = tbl_row.insertCell();
							cell1.appendChild(document.createTextNode(vote));

						}
					}	
						chart.render();
						$("#candilist").append(tbl_body);
						$("#resdiv").css("display","block");
					}
				
						//-----------------------------------------	
		           	
				if(err)
				{
					console.log(err);
				}
      		 	});
				})
				.catch(e => {
				console.log('Wow. Something went wrong: '+ e);
				alert("Ganache Server not Running");
				});	
		
			});
	}

</script>
<style>
    .rrow{
        cursor: pointer;
    }
</style>
</head>
<body>
<!-- header -->
	<div class="header_bg">
		<div class="container">
			<!-----start-header----->
			<div class="header">
				<div class="logo">
					<a href="index.php"><img src="assets/images/logo.png" alt=" " /></a>
				</div>
				<nav class="navbar navbar-default">
					<!-- Brand and toggle get grouped for better mobile display -->
					<div class="navbar-header">
					  <button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target="#bs-example-navbar-collapse-1">
						<span class="sr-only">Toggle navigation</span>
						<span class="icon-bar"></span>
						<span class="icon-bar"></span>
						<span class="icon-bar"></span>
					  </button>
					</div>

					<!-- Collect the nav links, forms, and other content for toggling -->
					<div class="collapse navbar-collapse nav-wil" id="bs-example-navbar-collapse-1">
						<ul class="nav navbar-nav right">
														<li ><a href="index.php">Home</a></li>
                                                        <!--<li><a href="admin.php">Login</a></li>-->
                                                        <li><a href="voting.php">Voting</a></li>
														<li class="act"><a href="results.php">Results</a></li>
														
                        </ul>
					</div><!-- /.navbar-collapse -->

				</nav>
			</div>
		</div>
	</div>
	<div class="header_bottom">
	</div>
<!-- //end-header -->

<!--typography-page -->
	<div class="typo">
		<div class="container">
			<!--h3 class="title">Welcome For Online Voting</h3>
			<p class="nihil">Vote For Real Government.</p-->
			<form action="#" method="post" enctype="multipart/form-data" onSubmit="return chkForm();">
			<div class="grid_3 grid_4">
				<h3 class="hdg">List Election</h3>
				<div class="bs-example">
                                   <table class="table">
						<tbody>
							<tr>
							<td><h4 id="h4.-bootstrap-heading"><b>Type Of Election</h4>
                                                            <select name="etype"  id="etype" style="border: none; border-bottom: 2px solid steelblue;width: 40%;height:50px" required>
							<option>-------CHOOSE Election-------</option>
							<option value="state">State Election</option>
						    <option value="cental">Central Election</option>
						    <option value="local">Local Election</option>
						    <!--option value="Alandur">By Election</option-->
							</select></td>
							</tr>
							<tr>
                            <td><h4 id="h4.-bootstrap-heading"><b>Constituency</b></h4>
                                                                
                            <select name="subtype" id="subtype" style="border: none; border-bottom: 2px solid steelblue;width: 40%;height:50px" required>
							<option>-------CHOOSE HERE-------</option>

						    <!--option value="Alandur">By Election</option-->
							</select>
                            </td>

							</tr>
                            <tr><td colspan="2"><input type="button" value="Search" id="search" ></td></tr>

							</table>
                                    <table id="target_table_id" class="table table-striped">
                                        <thead>
    
      
      <th scope="col">Election Name </th>
      <th scope="col">Election Type </th>
      <th scope="col">Date</th>
      <th scope="col">Constituency</th>
    
  </thead>
                                    </table>

				</div>
			</div>
            <div class="grid_3 grid_5" id="resdiv" style="display: none">    <!-- result div -->
				<h3>Election Result</h3>
				<div class="col-md-6">
					<table class="table table-bordered" id="candilist">
						<thead>
							    <th>Candidate Name</th>
								<th>Votes</th>
						</thead>
						<tbody>
							<tr>
								<td>X</td>
								<td>Party1</td>
								<td><span class="badge">42</span></td>
							</tr>	
							
						</tbody>
					</table>                    
				</div>
				<div class="col-md-6">
					<div id="chartContainer" style="height: 300px; width: 100%;">
					
					
					</div>
<!--				<script src="https://canvasjs.com/assets/script/canvasjs.min.js"></script>-->
				</div>
			   <div class="clearfix"> </div>
			</div>	 
			
	</form>

		</div>

	</div>
<!-- //typography-page -->


		<!-- scroll_top_btn -->
		<script type="text/javascript" src="assets/js/move-top.js"></script>
		<script type="text/javascript" src="assets/js/easing.js"></script>
	    <script type="text/javascript">
			$(document).ready(function() {

				var defaults = {
		  			containerID: 'toTop', // fading element id
					containerHoverID: 'toTopHover', // fading element hover id
					scrollSpeed: 1200,
					easingType: 'linear'
		 		};


				$().UItoTop({ easingType: 'easeOutQuart' });

			});
		</script>
		 <a href="#" id="toTop" style="display: block;"><span id="toTopHover" style="opacity: 1;"></span></a>
		<!--end scroll_top_btn -->
<!-- for bootstrap working -->
	 <script type="text/javascript" src="assets/js/bootstrap-3.1.1.min.js"></script>
<!-- //for bootstrap working -->
</body>
</html>