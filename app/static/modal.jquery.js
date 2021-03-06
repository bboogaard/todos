(function( $ ) {

    function ModalApi(settings) {
        this.modal = settings.modal;
        this.title = settings.title;
        this.content = settings.content;
        this.url = settings.url;
        this.onClose = settings.onClose;
        this.cssClasses = settings.cssClasses;
        this.bodyCssClasses = settings.bodyCssClasses;
        this.form = settings.form;
        this.formSetUp = settings.formSetUp;
        this.formHandler = settings.formHandler;
    }

    ModalApi.prototype = {

        init: function() {

            let self = this;

            this.modal.find('.modal-title').text(this.title);
            this.modal.find('.modal-dialog').addClass(this.cssClasses);
            this.modal.find('.modal-body').text(this.content).addClass(this.bodyCssClasses);
            if (this.url) {
                this.modal.find('.modal-body').empty().prepend(
                    '<iframe class="embed-responsive-item modal-tmp" src="' + this.url +
                    '" style="border:0px;width:100%;height:75vh;display:block;" scrolling="no"></iframe>'
                );
            }
            if (this.form) {
                this.modal.find('.modal-body').empty().prepend(
                    '<main role="main" class="container" style="width: 75%; padding: 5px">' +
                    this.form.outerHTML() +
                    '</main>'
                );
                if (this.formSetUp) {
                    this.formSetUp(this.modal.find('form'));
                }
                this.modal.find('form').show();
                function formSubmit(event) {
                    let form = $(this).parents('form');
                    if (self.formHandler) {
                        event.preventDefault();
                        if (form.get(0).reportValidity()) {
                            self.formHandler(form);
                            self.modal.modal('hide');
                        }
                    }
                    else {
                        if (form.get(0).reportValidity()) {
                            form.submit();
                            self.modal.modal('hide');
                        }
                    }
                }
                this.modal.on('click', 'form input[type="submit"]', formSubmit);
                this.modal.on('hide.bs.modal', function() {
                    self.modal.off('click', 'form input[type="submit"]', formSubmit);
                });
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

        if (settings.url && settings.form) {
             throw new Error("'url' and 'form' can't both be set");
        }

        let modal = new ModalApi({
            modal: $(this),
            title: settings.title,
            content: settings.content ? settings.content : '',
            url: settings.url,
            onClose: settings.onClose,
            cssClasses: settings.cssClasses ? baseCss + ' ' + settings.cssClasses : baseCss,
            bodyCssClasses: settings.bodyCssClasses ? bodyCss + ' ' + settings.bodyCssClasses : bodyCss,
            form: settings.form,
            formHandler: settings.formHandler,
            formSetUp: settings.formSetUp
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