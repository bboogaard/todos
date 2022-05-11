Dropzone.options.fileDropzone = {
    init: function() {
        this.on("success", function(file) {
            widgets['files'].load();
            widgets['images'].load();
        });
    }
}
$(function() {
    $('#file-dropzone-clear').click(function(event) {
        event.preventDefault();
        Dropzone.forElement('#file-dropzone').removeAllFiles(true);
    });
});