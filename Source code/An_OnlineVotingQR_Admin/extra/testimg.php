<?PHP
require "util.php";

if(!isset($_SESSION['uname'])){
    header('Location: '.'./admin.php'); 
}

?>
<!DOCTYPE html>
<html>
<head>
	<meta name="viewport" content="width=device-width, initial-scale=1">
	<script type="text/javascript" src="https://code.jquery.com/jquery-3.4.1.min.js"></script>
	
</head>
<body>
<form method='post' enctype='multipart/form-data' action=''>
<table class="table">
					<thead>
						<tr>
							<th style="text-align: center">CANDIDATE NAME</th>
							<!--th style="text-align: center">PARTY NAME</th-->
							<th style="text-align: " colspan="2">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;PARTY SYMBOL</th>
							<!--th style="text-align: center" colspan="2">PARTY FLAG</th-->
						</tr>
						<tr><td></td></tr>

					</thead>
					<tbody>
						<tr>
                                                    
											    <td><select id = "pref1select" class="preferenceSelect" class="cname" style="border: none; border-bottom: 2px solid steelblue;width: 100%;height:50px" name="cname[]" arequire />
												  <option value="Select">Select</option> 
												  <?php
												 $sql="select vname  from voterinfo where status='Accepted'";
                                                 $ret = $db->query($sql);
												 while($row = $ret->fetch_assoc()) {
												  ?>
                                                 <option value="<?php echo $row['vname']; ?>"><?php echo $row['vname']; ?></option> 
												 <?php
												 }
												 ?>
									            <!--td><input type="text" style="border: none; border-bottom: 2px solid steelblue;width: 100%;height:50px" name="party[]"/></td-->
                                                <td><input type="file" id="files" style="border: none; border-bottom: 2px solid steelblue;width: 70%;height:50px" name="files[]" class="psymbol" onchange="readURL(this);"/></td>
                                                    <td><img src="./images/no-image.webp" id="parsym" style="width:50px;height:50px"></td>
                                                    <!--td><input type="file" style="border: none; border-bottom: 2px solid steelblue;width: 70%;height:50px" name="pflag[]" onchange="readURL(this);"/></td>
                                                    <td><img src="./images/no-image.webp" id="parflag" style="width:50px;height:50px"></td-->
						</tr>

					</tbody>
				</table>
	<div class='file_upload' id='f1'><input id='files' name='file[]' type='file'/>1</div>
	<div id='file_tools'>
		<img src='images/file_add.png' id='add_file' title='Add new input'/>
		<img src='images/file_del.png' id='del_file' title='Delete'/>
	</div>
	<input type='button' name='upload' id="upload" value='Upload'/>
</form>

<script type='text/javascript'>
$(document).ready(function(){
	var counter = 2;
	$('#del_file').hide();
	$('img#add_file').click(function(){
		$('#file_tools').before('<div class="file_upload" id="f'+counter+'"><input id="files" name="file[]" type="file">'+counter+'</div>');
		$('#del_file').fadeIn(0);
	counter++;
	});
	$('img#del_file').click(function(){
		if(counter==3){
			$('#del_file').hide();
		}   
		counter--;
		$('#f'+counter).remove();
	});
	
	
	$('#upload').click(function(event){
		console.log("inside");
	var ins = document.getElementById('files').files.length;
				for (var x = 0; x <= ins; x++) {
					console.log(x);
					
				}
	});
});
</script>

 
</body>
</html>