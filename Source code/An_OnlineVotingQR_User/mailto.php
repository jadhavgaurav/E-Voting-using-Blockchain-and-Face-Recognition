<?php
use PHPMailer\PHPMailer\PHPMailer;
use PHPMailer\PHPMailer\Exception;
require 'PHPMailer-master/src/Exception.php';
require 'PHPMailer-master/src/PHPMailer.php';
require 'PHPMailer-master/src/SMTP.php';
header('Content-Type: application/json');
session_start();
error_reporting(0);
include('includes/config.php');
$result = Array();
/*if(strlen($_SESSION['alogin'])==0)
    {   
header('location:index.php');
}
else{ 
*/
//if(isset($_POST['return']))
//{
/*$rid=intval($_GET['rid']);
error_log("mail"+$_POST['mail'],0);*/
//$fine=$_POST['fine'];
/*$rstatus=1;

$sql="update tblissuedbookdetails set fine=:fine,RetrunStatus=:rstatus where id=:rid";
$query = $dbh->prepare($sql);
$query->bindParam(':rid',$rid,PDO::PARAM_STR);
$query->bindParam(':fine',$fine,PDO::PARAM_STR);
$query->bindParam(':rstatus',$rstatus,PDO::PARAM_STR);
$query->execute();*/
$vname=$_POST['vname'];
$email=$_POST['email'];
$txhash=$_POST['hash'];
console.log($email);
console.log($vname);
//$bookname=$_POST['bookname'];
//$issuedate=$_POST['issuedate'];
//$toreturndate=$_POST['toreturndate'];

$mail = new PHPMailer();
$mail->IsSMTP();
$mail->Mailer = "smtp";
$mail->SMTPDebug  = 1;  
$mail->SMTPAuth   = TRUE;
$mail->SMTPSecure = "tls";
$mail->Port       = 587;
$mail->Host       = "smtp.gmail.com";
$mail->Username   = echo "<script>document.writeln(gOptions.mailaddress);</script>";
$mail->Password   = echo "<script>document.writeln(gOptions.mailpassword);</script>";
$mail->IsHTML(true);
$mail->AddAddress($email, $vname);
$mail->SetFrom(echo "<script>document.writeln(gOptions.mailaddress);</script>";, "Admin Manager");
//$mail->AddReplyTo("reply-to-email@domain", "reply-to-name");
//$mail->AddCC("cc-recipient-email@domain", "cc-recipient-name");
$mail->Subject = "Vote Successfully Casted";
$content = "<b>Dear Mr/Ms ".$vname." You have successfully casted your voted. Your Blockchain Transaction Referrence is ".$txhash." Thanks for showing your Social Responsibilites.";
//$content ="test mail ".$fullname;
$mail->MsgHTML($content); 
if(!$mail->Send()) {
	$result['status']=false;
	$result['message']='Error sending message';
  echo json_encode($result);	  
} else {
	$result['status']=true;
	$result['message']='Message sent successfully';
	echo json_encode($result); 
}
?>