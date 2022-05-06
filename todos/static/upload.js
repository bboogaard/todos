function UploadApi(settings) {
    this.url = settings.url;
    this.responseHandler = settings.responseHandler;
}

UploadApi.prototype = {

    uploadFile: function(data) {

        let self = this;

        let formData = new FormData();
        for (var field in data) {
            formData.append(field, data[field]);
        }
        let request = new XMLHttpRequest();
        request.open("POST", this.url);
        request.setRequestHeader('X-CSRFToken', csrftoken);
        request.send(formData);
        request.onreadystatechange = function() {
            if (this.readyState === 4 && this.status === 200) {
               self.responseHandler();
            }
        };

    }

}