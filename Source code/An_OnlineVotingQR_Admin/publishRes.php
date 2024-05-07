<?php
require "util.php";
$subtype=$_GET['subtype'];
$etype = $_GET['etype'];
$edate = $_GET['edate'];
$ename = $_GET['ename'];

//$sql = "select distinct ename,etype,edate,subtype from electioninfo where status='2' and etype='$etype' and subtype='$subtype' and edate='$edate'";

//$sql="select A.cname,aa.total,a.flag from electioninfo a, (select candidate,count(candidate) as total from votes where "
//        . "etype='$etype' and esubtype='$subtype'  group by election,candidate,etype ) as aa where a.id=aa.candidate  and edate='$edate'";
//echo $sql;
error_log("subtype".$subtype);
error_log("subtype".$etype);
error_log("subtype".$edate);
error_log("subtype".$ename);
$sql = "update electioninfo set status='2' where etype='$etype' and subtype='$subtype' and edate='$edate' and ename='$ename'";
$res = $db->query($sql);
$result= Array();   
if($res)
{
$result['status']="ok";
echo json_encode($result);
}
else
{
$result['status']="error";
echo json_encode($result);
}
?>