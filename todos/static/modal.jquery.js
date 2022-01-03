(function( $ ) {

    function ModalApi(settings) {
        this.modal = settings.modal;
        this.title = settings.title;
        this.content = settings.content;
        this.url = settings.url;
        this.onClose = settings.onClose;
        this.cssClasses = settings.cssClasses;
        this.bodyCssClasses = settings.bodyCssClasses;
    }

    ModalApi.prototype = {

        init: function() {

            this.modal.find('.modal-title').text(this.title);
            this.modal.find('.modal-dialog').addClass(this.cssClasses);
            this.modal.find('.modal-body').text(this.content).addClass(this.bodyCssClasses);
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

        let baseCss = 'modal-dialog modal-dialog-centered';
        let bodyCss = 'modal-body';

        let modal = new ModalApi({
            modal: $(this),
            title: settings.title,
            content: settings.content ? settings.content : '',
            url: settings.url,
            onClose: settings.onClose,
            cssClasses: settings.cssClasses ? baseCss + ' ' + settings.cssClasses : baseCss,
            bodyCssClasses: settings.bodyCssClasses ? bodyCss + ' ' + settings.bodyCssClasses : bodyCss
        });
        modal.init();

        return this;

    };

    $.fn.FullModal = function(settings) {

        settings.cssClasses = 'modal-xl';
        settings.bodyCssClasses = 'modal-filling';
        return $(this).Modal(settings);

    }

})(jQuery);