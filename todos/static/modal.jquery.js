(function( $ ) {

    function ModalApi(settings) {
        this.modal = settings.modal;
        this.title = settings.title;
        this.content = settings.content;
        this.url = settings.url;
        this.onClose = settings.onClose;
    }

    ModalApi.prototype = {

        init: function() {

            this.modal.find('.modal-title').text(this.title);
            this.modal.find('.modal-body').text(this.content);
            if (this.url) {
                this.modal.find('.modal-body').empty().prepend(
                    '<iframe class="embed-responsive-item modal-tmp" src="' + this.url +
                    '" style="border:0px;width:100%;height:75vh;display:block;" scrolling="no"></iframe>'
                );
            }
            if (this.onClose) {
                this.modal.on('hide.bs.modal', this.onClose);
            }
            this.modal.modal({});

        }

    }

    $.fn.Modal = function(settings) {

        let modal = new ModalApi({
            modal: $(this),
            title: settings.title,
            content: settings.content ? settings.content : '',
            url: settings.url,
            onClose: settings.onClose
        });
        modal.init();

        return this;

    };

})(jQuery);