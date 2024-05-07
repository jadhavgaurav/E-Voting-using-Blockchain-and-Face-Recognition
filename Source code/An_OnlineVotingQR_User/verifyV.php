
<?php
//-----------------------------------code to compare fingerprint----------------//
require 'util.php';
$aahdid=$_POST['aid'];
$str = $_POST['imgVal'];
//$aahdid="1232";
//$basepath="E:/xampp/htdocs/An_OnlineVotingQR/";
//$basepath="C:/xampp/htdocs/OnlineVoting/Vote/An_OnlineVotingQR/";
$basepath="C:/xampp/htdocs/An_OnlineVotingQR_User/";
 $sql = "select * from voterinfo where vaadhar='$aahdid'";
//$sql = "select * from voterinfo where vaadhar='123455432123'";
file_put_contents('./temp/foo.png', base64_decode($str));
$ret = $db->query($sql);
//echo $sql;
$response =0;
$return=0;
if($ret){

    $row=$ret->fetch_assoc();
    $file1 = $basepath."fpimages/". $row['finger'];
    $file2=$basepath."temp/foo.png";
    $post = ['file1'=> $file1,"file2"=>$file2,"type"=>"verify"];
 //   print_r($post);
    
  $ch = curl_init();
  curl_setopt($ch, CURLOPT_URL,'http://localhost:8078/');
  curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
  curl_setopt($ch, CURLOPT_POSTFIELDS, http_build_query($post));
  //echo http_build_query($post);
  $response = curl_exec($ch);
  //$response = preg_replace("/\r|\n/", '', $response);
  //echo 'response'.$response;
  $response = str_replace(array("\n", "\r"), '', $response);
  echo $response;
 /*if ($response=1)
 {$return="true";
 echo json_encode($response);}
else{
    $return="false";
 //   echo "ERROR";}
    echo json_encode($response);}
    */
}
else{
    $return="Error";
    //echo "ERROR";
    echo json_encode($return);
}


?>