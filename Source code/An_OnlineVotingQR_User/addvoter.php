<?php
require "util.php";

$image;
$aadhar;
$name;
$mobile;
$dob;
$check;
$number;
$status="Pending";
$password;
//$error = Array();
$result = Array();
//$result['test']='test';
//if(isset($_POST['submit'])){
	
	 if($_POST) {
	
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
        $result['image']='Please Upload an image';
    }
    if(!isset($aadhar) || $aadhar=='' ){
        $result['aadhar']='Please Enter the Aadhar Id';
    }
	 if(!isset($password) || $password=='' ){
        $result['password']='Please Enter the pssword';
    }
	$email = $_POST["email"];
	if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
	$result['email'] = "Invalid email format";
	}
	 if($check<12 || $check>12 || !is_numeric($aadhar)){
        $result['aadhar']='Please Enter valid 12 Digit Aadhar Id';
    }
	if($ids>10 || $ids<10 || !is_numeric($id)){
		$result['id']='Plese Enter valid 10 Digit Voter Id';
	}
    if(!isset($name) || $name=='' ){
        $result['name']='Please Enter the name';
    }
      if(!isset($id) || $id=='' ){
        $result['id']='Please Enter the Voter ID';
    }
    if($dob<18)
    {
     $result['dob']='18 plus aged people are only eligible for elections';  
	 
    }
	 if(!isset($baddress) || $baddress=='' ){
     $result['baddress']='Please Enter the Blockchain Address';
    }
	//$result['sqle']='Please Enter the Blockchain Address';
/**********************************/

    $folderPath = "voterImages/";

    $image_parts = explode(";base64,", $img);

    $image_type_aux = explode("image/", $image_parts[0]);

    $image_type = $image_type_aux[1];

    $image_base64 = base64_decode($image_parts[1]);

    $fileName = uniqid() . '.png';

    $file = $folderPath . $fileName;

    file_put_contents($file, $image_base64);
	error_log("result is empty".sizeof($result),0);
    if(sizeof($result)==0)
    {
		reset($result);
		error_log("result is empty",0);
		//$fingerimage="d16e7d9f1e1c68c49b30c9364d3e0b23.png";	 
        
          $sql="insert into voterinfo (vimage,vaadhar,vname,password,email,vid,dob,area,status,baddress)"
              . "values('".$fileName."','".$aadhar."','".$name."','".$password."','".$email."','".$id."','".$dob."','$area','".$status."','".$baddress."')";
			//   header('Location: '.'./voters.php'); 
		//var status=$db->query($sql)
	//	error_log($db->query($sql),0);
      if($db->query($sql)){
		  $result['stat']=true;
		  $result['message']='Voter Added Successfully ...Waiting for Approval';
		  
         }
      else{
          $er = $db->error;
		  $result['stat']=false;
		 
           unlink($fpath);
          unlink( $target_path);
		  
          if(strpos($er, 'key 3') !== false){
              $result['ER_EM']='Voter id already registered';
			
          }
          elseif ((strpos($er, 'key 2') !== false)) {
           $result['ER_EM']='Aadhar id already registered';
		   
		  }
		  else{
          $result['ER_EM']=$er;
		  	  
          }
 
       }
    }
	else{
		$result['stat']=false;
	}
	
	error_log( print_r(json_encode($result), TRUE));

	echo(json_encode($result));

    }

?>
