<?php
error_reporting(E_ERROR );
$db = new mysqli('localhost', 'root', '', 'evoting');

    session_start();
   if($db->connect_errno){
      //echo $db->connect_errno;
	  die("Connection failed: " . $conn->connect_error);
   } else {
     // echo "Opened database successfully\n";
   }
?>
