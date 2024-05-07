<?PHP
require "util.php";
error_log("Failed to connect to database!".$_SESSION['uname'], 0);
if(!isset($_SESSION['uname'])){
    header('Location: '.'./admin.php'); 
}

$ename;
$edate;
$etype;
$noofcandidates;
$cname;
$pname;
$psymbol;
$pflag;
$error = Array();
//if(isset($_POST['submit'])){
    $ename=$_POST['ename'];
    $edate=$_POST['edate'];
    $etype=$_POST['etype'];
    $subtype=$_POST['subtype'];
    $etime = $_POST['etime'];
    $stime = $_POST['stime'];
    $countfiles = count($_FILES['psymbol']['name']);
	 error_log("countfiles".$countfiles, 0);
	 error_log("Election name".$etype, 0);
//echo "$ename on $edate of $etype";
//echo $stime;
    if(!isset($stime) or $stime=="00.00.00"){
        $error['stime']="Please Select Start time";
    }
    
    $cname=$_POST['cname'];

$fileNamelist;
   //var_dump($_FILES);
for ($i = 0; $i < count($_FILES['psymbol']['name'])-1; $i++) {
// Loop to get individual element from the array
error_log("file Names".$_FILES['psymbol']['name'][$i]."id".$i, 0);
$j = 0;     // Variable for indexing uploaded image.
$target_path = "upImages/";     // Declaring Path for uploaded images.
$validextensions = array("jpeg", "jpg", "png");      // Extensions which are allowed.
$ext = explode('.', basename($_FILES['psymbol']['name'][$i]));   // Explode file name from dot(.)
$file_extension = end($ext); // Store extensions in the variable.
$fileNamelist[$i]=md5(uniqid()). "." . $ext[count($ext) - 1];
$target_path = $target_path . $fileNamelist[$i];      // Set the target path with a new name of image.
$j = $j + 1;      // Increment the number of uploaded images according to the files in array.
//error_log("Failed to connect to database!".$target_path."id".$i, 0);
if (     // Approx. 100kb files can be uploaded.
 in_array($file_extension, $validextensions)) {
if (move_uploaded_file($_FILES['psymbol']['tmp_name'][$i], $target_path)) {
// If file moved to uploads folder.
//$error[$j]= '<span id="noerror">Image uploaded successfully!.</span><br/><br/>';
} else {     //  If File Was Not Moved.
$error[$j]= '<span id="error">please try again!.</span><br/><br/>';
}
} else {     //   If File Size And File Type Was Incorrect.
$error[$j]= '<span id="error">***Invalid file Size or Type***</span><br/><br/>';
}
}
error_log("count cname!".count($cname), 0);

$response="";
    if(sizeof($error)==0)
        {
        //echo count($cname);
        for ($i = 0; $i < count($cname)-1; $i++) {            
            $sql="insert into electioninfo (ename,edate,etype,subtype,cname,flag,status,stime,etime)"
              . "values('".$ename."','".$edate."','".$etype."','".$subtype."','".$cname[$i]."','".$fileNamelist[$i]."','1','$stime','$etime')";
     // echo $sql;
      if($db->query($sql))
         {
            $response="success";	  	   
         }
         else {$response="Error";}
        }
	//	echo $response;
    }
	if($response=="success")
	{
	echo json_encode($fileNamelist);
	}
	else {echo $response;}
//}
?>