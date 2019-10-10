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

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

$(document).ready(function() {
    $("#btnFetch").click(function() {
      // disable button
      $(this).prop("hidden", true);
      $("#btnFetch1").prop("hidden", false)
    });
});
