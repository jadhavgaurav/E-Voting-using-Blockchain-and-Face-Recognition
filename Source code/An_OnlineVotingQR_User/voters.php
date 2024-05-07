<?PHP
require "util.php";
//session_start();

/*
$image;
$aadhar;
$name;
$mobile;
$dob;
$check;
$number;
$status="Pending";
$password;
$error = Array();
if(isset($_POST['submit'])){
    //$image=$_POST['vimage'];
	$img = $_POST['image'];
    $aadhar=$_POST['vaadhar'];
    $name=$_POST['vname'];
    $id=$_POST['vid'];
    $dob=$_POST['dob'];
    //$fpstr=$_POST['b64img'];
    $area=$_POST['area'];
	$password = $_POST['password'];
	//$email = $_POST['email'];
    $check = strlen($aadhar);
	$ids = strlen($id);
	$baddress = $_POST['baddress'];
	
//    echo "SASDASD ";
   // echo "image".$img;
    //echo $name==="";
    if(!isset($img) || $img==''){
     //   echo "Says";
        $error['image']='Please Upload an image';
    }
    if(!isset($aadhar) || $aadhar=='' ){
        $error['aadhar']='Please Enter the Aadhar Id';
    }
	 if(!isset($password) || $password=='' ){
        $error['password']='Please Enter the pssword';
    }
	$email = $_POST["email"];
	if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
	$emailErr = "Invalid email format";
	}
	 if($check<12 || $check>12 || !is_numeric($aadhar)){
        $error['aadhar']='Please Enter valid 12 Digit Aadhar Id';
    }
	if($ids>10 || $ids<10 || !is_numeric($id)){
		$error['id']='Plese Enter valid 10 Digit Voter Id';
	}
    if(!isset($name) || $name=='' ){
        $error['name']='Please Enter the name';
    }
      if(!isset($id) || $id=='' ){
        $error['id']='Please Enter the Voter ID';
    }
    if($dob<18)
    {
     $error['dob']='18 plus aged people are only eligible for elections';  
	 
    }
	 if(!isset($baddress) || $baddress=='' ){
        $error['id']='Please Enter the Blockchain Address';
    }
	
/**********************************/

 /*   $folderPath = "voterImages/";

    $image_parts = explode(";base64,", $img);

    $image_type_aux = explode("image/", $image_parts[0]);

    $image_type = $image_type_aux[1];

    $image_base64 = base64_decode($image_parts[1]);

    $fileName = uniqid() . '.png';

    $file = $folderPath . $fileName;

    file_put_contents($file, $image_base64);

    if(sizeof($error)==0)
    {
		$fingerimage="d16e7d9f1e1c68c49b30c9364d3e0b23.png";	 
        
          $sql="insert into voterinfo (vimage,vaadhar,vname,password,email,vid,dob,area,status,finger,baddress)"
              . "values('".$fileName."','".$aadhar."','".$name."','".$password."','".$email."','".$id."','".$dob."','$area','".$status."','".$fingerimage."','".$baddress."')";
			   header('Location: '.'./voters.php'); 
      
      if($db->query($sql)){
		  $success="Voter Added Successfully ...Waiting for Approval";
         }
      else{
          $er = $db->error;
          //echo $er;
           unlink($fpath);
          unlink( $target_path);
          if(strpos($er, 'key 3') !== false){
              $error['ER_EM']='Voter id already registered';
          }
          elseif ((strpos($er, 'key 2') !== false)) {
           $error['ER_EM']='Aadhar id already registered';
      }
      else{
          $error['ER_EM']=$er;;
      }
 
       }
    }
    }
    else{
        $error=[];
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
<script src="https://ajax.googleapis.com/ajax/libs/jquery/2.1.1/jquery.min.js"></script>
<script type="application/x-javascript"> addEventListener("load", function() { setTimeout(hideURLbar, 0); }, false);
function hideURLbar(){ window.scrollTo(0,1); } </script>
<!-- //for-mobile-apps -->
<link href="assets/css/bootstrap.css" rel='stylesheet' type='text/css' />
<!--<link href='//fonts.googleapis.com/css?family=Raleway:400,100,200,300,500,600,700,800,900' rel='stylesheet' type='text/css'>-->
<!--<link href='//fonts.googleapis.com/css?family=Open+Sans:400,300,300italic,400italic,600,600italic,700,700italic,800,800italic' rel='stylesheet' type='text/css'>-->
<link rel="stylesheet" type="text/css" href="assets/css/style.css">
<!---strat-slider---->
<!--script type="text/javascript" src="assets/js/jquery-1.11.1.min.js"></script-->
<script src="https://code.jquery.com/jquery-2.2.4.min.js" integrity="sha256-BbhdlvQf/xTY9gja0Dq3HiwQF8LaCRTXxZKRutelT44=" crossorigin="anonymous"></script>
<!---//-slider---->
<!--script type="text/javascript" src="assets/js/adapter.min.js"></script>
<script type="text/javascript" src="assets/js/vue.min.js"></script>
<script type="text/javascript" src="assets/js/instascan.min.js"></script-->
<script src="https://cdnjs.cloudflare.com/ajax/libs/webcamjs/1.0.25/webcam.min.js"></script>

<script src="https://cdnjs.cloudflare.com/ajax/libs/web3/1.8.1/web3.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/truffle-contract@4.0.16/dist/truffle-contract.js"></script>

<script src="mfs100-9.0.2.6.js"></script>
<script type="text/javascript" src="config.js"></script>


<script language="javascript" type="text/javascript">
var datauri="";
    function processResult(str){
    //alert(str);
    $xmlDoc = $.parseXML( str );
  
  uid = $xmlDoc.children[0].getAttribute('uid');
  $("#aid").val(uid);
  uid = $xmlDoc.children[0].getAttribute('name');
  $("#vname").val(uid);
  uid = $xmlDoc.children[0].getAttribute('dob');
  var parts =uid.split('/');
  var mydate = new Date(parts[2], parts[1] - 1, parts[0]); 
  $("#dob").val(mydate);
  }
 </script>

<script>
    var _MS_PER_DAY = 1000 * 60 * 60 * 24;
function chkForm(){
    var a    = new Date();
    dateStr = document.getElementById("dob").value;

    b =new Date(dateStr);
    //alert(b);
//var b    = new Date("2017-07-25"); 
var remainingDays    = dateDiffInDays(b, a);
if(remainingDays<6570){
    alert("Age should be above 18 yrs");
    return false;
}
return true;
}    

function dateDiffInDays(a, b) {
  // Discard the time and time-zone information.
  var utc1 = Date.UTC(a.getFullYear(), a.getMonth(), a.getDate());
  var utc2 = Date.UTC(b.getFullYear(), b.getMonth(), b.getDate());

  return Math.floor((utc2 - utc1) / _MS_PER_DAY);
}
</script>
    
</head>
<body>
<!-- header -->
	<div class="header_bg">
		<div class="container">
			<!-----start-header----->
			<div class="header">
				<div class="logo">
				<!--	<a href="#"><img src="images/logo.png" alt=" " /></a> -->
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
						<ul class="nav navbar-nav">							
                                                        <li ><a href="index.php">Home</a></li>
                                                        <!--<li><a href="admin.php">Login</a></li>-->
                                                        <li><a href="voting.php">Voting</a></li>
														<li><a href="user.php">User Login</a></li>
														<li class="act"><a href="voters.php">User Register</a></li>
                                                        <li><a href="results.php">Results</a></li>
							                            
						</ul>
					</div><!-- /.navbar-collapse -->
					
				</nav>
			</div>
		</div>
	</div>
	<div class="header_bottom">
	</div>
<!-- //end-header -->
<!-- banner1 -->
	
<!-- //banner1 -->
<!--typography-page -->
	<div class="typo">
	<form action="#" method="post" id="myform" onsubmit="return chkForm();" enctype="multipart/form-data">
		<div class="container">
			<h3 class="title">Welcome for Online Voting</h3>
			<p class="nihil">Vote For Real Government.</p>
			<div class="grid_3 grid_4">
				<h3 class="hdg">Voter Citizen Details</h3>
				<div id="response" class="alert alert-danger collapse" role="alert">
  				</div>
				<div id="success" class="alert alert-success collapse" role="alert">
 				</div>
				<div class="bs-example" style="width:50%;float:left">
				
					<table class="table">
					
					
						<tbody>
                                                    <tr>
                                                        <td>
                                                            <!--?php 
                                                            foreach ($error as $value) {
                                                                echo "<span style='color:red'>$value</span><br/>";
                                                            }
                                                            ?>
															  <!--?php 
                                                            foreach ($success as $value) {
                                                                echo "<span style='color:green'>$value</span><br/>";
                                                            }
                                                            ?-->
                                                        </td>
					    </tr>
						<tr>
                                                    <td><h4 id="h4.-bootstrap-heading"><b>Voter Image</b></h4><br/><input type="file" name="vimage" onchange="previewFile()" style="border: none; border-bottom: 2px solid steelblue;width: 80%;height:50px" /></td>
													
					    </tr>
						
							<tr>
                                                            <td><h4 id="h4.-bootstrap-heading"><b>Voter Adhar Number</b></h4><input type="text" name="vaadhar" id="aid" style="border: none; border-bottom: 2px solid steelblue;width: 80%;height:50px" value="<?php echo  isset($aadhar) ?  $aadhar:"" ?>"/></td>
							</tr>
							<tr>
                                                            <td><h4 id="h4.-bootstrap-heading"><b>Voter Name</b></h4><input type="text" name="vname"  id="vname" style="border: none; border-bottom: 2px solid steelblue;width: 80%;height:50px"  value="<?php echo isset($name)? $name : "" ?>"/></td>
							</tr>
								<tr>
                                                            <td><h4 id="h4.-bootstrap-heading"><b>Voter Password</b></h4><input type="password" name="password"  id="passwrd" style="border: none; border-bottom: 2px solid steelblue;width: 80%;height:50px"  value="<?php echo isset($password)? $password : "" ?>"/></td>
							</tr>
							<tr>
                                                            <td><h4 id="h4.-bootstrap-heading"><b>Voter Email</b></h4><input type="text" name="email"  id="email" style="border: none; border-bottom: 2px solid steelblue;width: 80%;height:50px"  value="<?php echo isset($email)? $email : "" ?>"/></td>
							</tr>
							<tr>
                                                            <td><h4 id="h4.-bootstrap-heading"><b>Voter Id</b></h4><input type="text" name="vid" style="border: none; border-bottom: 2px solid steelblue;width: 80%;height:50px" value="<?php echo isset($id)?$id:"" ?>"/></td>
							</tr>
							<tr>
                                                            <td><h4 id="h4.-bootstrap-heading"><b>Area</b></h4>
                                                            <select name="area" id="subtype" style="border: none; border-bottom: 2px solid steelblue;width: 80%;height:50px" required>
							<option>-------CHOOSE HERE-------</option>
                                                         <?php
                                                         
$sql="select distinct area from constituency";
$ret = $db->query($sql);
//echo $sql;
while($row = $ret->fetch_assoc()) {
echo  "<option value=\"".$row['area']."\">".$row['area']."</option>";
}
                                                         ?>
						    <!--option value="Alandur">By Election</option-->
							</select>
                            </td>
							</tr>
							<tr>
                            <td><h4 id="h4.-bootstrap-heading"><b>Voter Date Of Birth</h4><input type="date" name="dob"  id="dob" data-date-inline-picker="true" style="border: none; border-bottom: 2px solid steelblue;width: 80%;height:50px"  value="<?php echo isset($dob)?$dob:"" ?>"/></td>
							</tr>
							<tr>
                            <td><h4 id="h4.-bootstrap-heading"><b>Blockchain Address</b></h4><input type="text" name="baddress" style="border: none; border-bottom: 2px solid steelblue;width: 80%;height:50px" value="<?php echo isset($baddress)? $baddress : "" ?>"/></td>
							</tr>
							
						</tbody>
					</table>
				</div>
			<div lass="grid_3 grid_5" style="width:40%;float:right" tyle="margin-left: 770px;float: left;margin-top: -260px">
            <div id="app" style="width:100px">
            <section class="cameras">
          
		  <h3>Cameras</h3>
			<div id="my_camera"></div>
			<div id="container">
				<!--video width="200" height="200" autoplay="true" id="video">
				</video-->
				<!--input type=button value="Take Snapshot" onClick="take_snapshot()"-->
				<input type="button" id="btnCapture" value="Capture" class=" capturebuttonpadding btn btn-primary btn-lg submit_buttom_padding" onClick="take_snapshot()" style="margin-top:20px"/>		
				<input type="hidden" name="image" class="image-tag">
				</div>				
				<br> </br>
				<img id="blah" alt="your photo here" src="assets/images/no-image.webp" width="250" height="250" /><br/><br/>
		
        </section>
                                
        </div>		
		</div>	
        </div>
			
			
        <p class="one"><input type="button" id="submit" name="submit" value=" ADD VOTER DETAILS" style="background-color:steelblue;color:white ;height: 50px;width: 100%;border: 2px solid steelblue;"></p>
		
		</div>	
		</form>					<!-- /.row -->
		
		</div>
	
<!-- footer -->
	
	
<!-- //footer -->
		<!-- scroll_top_btn -->
		<script type="text/javascript" src="assets/js/move-top.js"></script>
		<script type="text/javascript" src="assets/js/easing.js"></script>
	    <script type="text/javascript">
			$(document).ready(function() {
				//$("#success").toggleClass("hidden");
				//$("#response").toggleClass("hidden");
				var defaults = {
		  			containerID: 'toTop', // fading element id
					containerHoverID: 'toTopHover', // fading element hover id
					scrollSpeed: 1200,
					easingType: 'linear' 
		 		};
							
				$().UItoTop({ easingType: 'easeOutQuart' });
				
			});
</script>
<script>

$('#submit').click(function(event){
	//$("#success").toggleClass("hidden");
	//$("#response").toggleClass("hidden");
	event.preventDefault();
        var myFormData = new FormData($(this).parents('form')[0]);
		
		 $("response").empty();
		jQuery('#response').html('');
		$.ajax({
        url: 'addvoter.php',
        type: 'POST',
        processData: false, // important
        contentType: false, // important
		datatype : "application/json",
		//contentType: "text/plain"
        data: myFormData,success: function(result)
        {
			
               res = $.parseJSON(result);
			   console.log(res);
			   console.log(res['stat']);
			    //$("response").empty();
			   if (res['stat']==true)
			   {
				   Addvoterface();
				   console.log("inside true");
				   //  $("#success").toggleClass("hidden");
					// $("#response").toggleClass("hidden");
					
					$('#response').hide();
					$('#success').show();
				
				//var element = document.getElementById("response");
				//element.style.color = "#008000";
				
				for (var i in res) {
				   if (i !='stat')
				   {					
					$("#success").append(res[i]+ " "+"<br/>");
				   }				
					}
				$('#myform')[0].reset();
				//$(this).closest('myform').find("input[type=text], textarea").val("");					
			   }
			   else{
				   /*if ($("success").is(":hidden")) {}
					else{				   
				    $("#success").toggleClass("hidden");
				   }*/
				   //if ($("response").is(":hidden")) {				   					
				   // $("#response").toggleClass("hidden");
				   //}
				    $('#response').show();
					$('#success').hide();
					//var element = document.getElementById("response");
					//element.style.color = "#FF0000";
			   for (var i in res) {
				   if (i !='stat')
				   {
					//$("#response").append(i+ ":" + res[i]+ " "+"<br/>");
					$("#response").append(res[i]+ " "+"<br/>");
				   }
				
				}
				
				}
			  			
            }
        });
	
});

function Addvoterface()
{

			var vname=document.getElementById("vname").value;
			var email=document.getElementById("email").value;
			
			var form = new FormData();
			//var blob = dataURItoBlob(datauri)
			file = dataURLtoFile(datauri, "verify.png");
			form.append("name", vname);
			form.append("email", email);
			form.append("file", file);
				
		  var settings = {
					"url": "http://localhost:5001/register",
					"method": "POST",
					"timeout": 0,
					"processData": false,
					"mimeType": "multipart/form-data",
					"contentType": false,
					"data": form
				};

				$.ajax(settings).done(function(response) {
					console.log("---py-res---"+response);		
					
				});
}
	
	function dataURLtoFile(dataurl, filename) {

		var arr = dataurl.split(','), mime = arr[0].match(/:(.*?);/)[1], bstr = atob(arr[1]), n = bstr.length, u8arr = new Uint8Array(
				n);

		while (n--) {
			u8arr[n] = bstr.charCodeAt(n);
		}

		return new File([ u8arr ], filename, {
			type : mime
		});
	}
</script>
<script>



    Webcam.set({

        width: 250,

        height: 250,

        image_format: 'jpeg',

        jpeg_quality: 90

    });

    Webcam.attach( '#my_camera' );
	
	function take_snapshot() {

        Webcam.snap( function(data_uri) {

            $(".image-tag").val(data_uri);
            datauri=data_uri;
			document.getElementById('blah').src=data_uri;
        } );

    }
//load file input image as base64 to img for preview
function previewFile() {
  const preview = document.querySelector('img');
  const file = document.querySelector('input[type=file]').files[0];
  const reader = new FileReader();

  reader.addEventListener("load", () => {
    // convert image file to base64 string
    preview.src = reader.result;
	$(".image-tag").val(reader.result);
	datauri=reader.result;
  }, false);

  if (file) {
    reader.readAsDataURL(file);
  }
}

</script>
		 <a href="#" id="toTop" style="display: block;"><span id="toTopHover" style="opacity: 1;"></span></a>
		<!--end scroll_top_btn -->
<!-- for bootstrap working -->
	 <script type="text/javascript" src="assets/js/bootstrap-3.1.1.min.js"></script>
         
<!-- //for bootstrap working -->
</body>
       
</html>