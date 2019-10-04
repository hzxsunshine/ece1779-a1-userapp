function fileSize(){
    document.cookie = "fileSize=" + document.getElementById('image-file').files[0].size
  }

$('#image-file').on('change',function(){
    //get the file name
    var fileName = $(this).val();
    fileName = fileName.replace(/^C:\\fakepath\\/i, '');
    //replace the "Choose a file" label
    $(this).next('.custom-file-label').html(fileName);
})
