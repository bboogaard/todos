(function( $ ) {

    function UploadApi(settings) {
        this.element = settings.element;
        this.url = settings.url;
        this.responseHandler = settings.responseHandler;
    }

    UploadApi.prototype = {

        init: function () {

            let self = this;

            this.element.change(function() {
                self.uploadFile();
            });

        },

        uploadFile: function() {

            let self = this;

            let formData = new FormData();
            formData.append(this.element.attr('name'), this.element.get(0).files[0]);

            let request = new XMLHttpRequest();
            request.open("POST", this.url);
            request.setRequestHeader('X-CSRFToken', csrftoken);
            request.send(formData);
            request.onreadystatechange = function() {
                if (this.readyState === 4 && this.status === 200) {
                   self.responseHandler();
                }
            };

        },

    }

    $.fn.Upload = function(settings) {

        let uploadApi = new UploadApi({
            element: $(this),
            url: settings.url,
            responseHandler: settings.responseHandler
        });
        uploadApi.init();

        return this;

    };

})(jQuery);