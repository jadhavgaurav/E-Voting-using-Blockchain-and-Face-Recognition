<?php
//---------------------------------------------Blockchain Portion---------//
require 'util.php';
$sender='4545';
$recipient ="rec123";

$aadhar=$_POST['aadhar'];
$election=$_POST['ename'];
$etype=$_POST['etype'];
$esub=$_POST['esubtype'];
$candidate=$_POST['candidate']; 
$txhash=$_POST['txhash']; 


$myobj->sender=$sender;
$myobj->amount=1;
$myobj->recipient='adasd';
$myobj->aadhar=$aadhar;
$myobj->election=$election;
$myobj->etype=$etype;
$myobj->esub=$esub;
$myobj->candidate=$candidate;

  $curl= curl_init();
  curl_setopt($curl, CURLOPT_URL,'http://localhost:8080/transactions');
  
  curl_setopt($curl, CURLOPT_POST, 1);
  curl_setopt( $curl, CURLOPT_HTTPHEADER, array('Content-Type:application/json'));
  curl_setopt($curl, CURLOPT_POSTFIELDS,
            json_encode($myobj));
  curl_setopt($curl, CURLOPT_RETURNTRANSFER, true);

 // echo(json_encode($myobj));

//  echo('<br><br>');  
  $result = curl_exec($curl);
  // echo($result);
  curl_close($curl);
  $curl= curl_init();
  curl_setopt($curl, CURLOPT_URL,'http://localhost:8080/mine');
  curl_setopt($curl, CURLOPT_RETURNTRANSFER, true);
  $result = curl_exec($curl);
  // echo($result);
  curl_close($curl);
  
        $sql="insert into votes (voter,candidate,time,election,etype,esubtype,txhash)"
              . "values('".$aadhar."','".$candidate."',now(),'".$election."','$etype','$esub','".$txhash."')";
      //$db->query($sql);
	  if($db->query($sql)){
      $res['status']=true;
	  }
	  else
	  {
		  $res['status']=false;
	  }
echo json_encode($res);

?>

