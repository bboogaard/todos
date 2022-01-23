(function( $ ) {

    function SnippetApi(settings) {
        this.container = settings.container;
        this.updateUrl = settings.updateUrl;
        this.navigation = {
            prev: null,
            next: null
        }
        this.easyMDE = null;

    }

    SnippetApi.prototype = {

        init: function() {

            this.init_edit_handlers();

            this.render();

        },

        init_edit_handlers: function() {

            let self = this;

            this.container.on('submit', 'form', function(event) {
                event.preventDefault();
                $.post($(this).attr('action'), $(this).serialize())
                .done(function(res) {
                    self.initEditor(res.html);
                    self.toggleButtons();
                });
            });

            this.container.on('click', '[data-action="save"]', function () {
                $(this).parents('form').submit();
            });

            this.container.on('click', '[data-action="new"]', function () {
                $(this).parents('form').find('textarea').val('');
                $(this).parents('form').attr('action', self.updateUrl + '?action=new');
                $(this).parents('form').submit();
            });

            this.container.on('click', '[data-action="delete"]', function () {
                $(this).parents('form').attr('action', $(this).data('action-url'));
                $(this).parents('form').submit();
            });

            this.container.on('click', '[data-action="prev"]', function (event) {
                event.preventDefault();
                self.prev();
            });

            this.container.on('click', '[data-action="next"]', function (event) {
                event.preventDefault();
                self.next();
            });

        },

        render: function(object_id=null) {

            let self = this;

            $.get(this.updateUrl + (object_id ? "?object_id=" + object_id : ""))
            .done(function(res) {
                self.initEditor(res.html);
                self.toggleButtons();
            });

        },

        initEditor: function(html) {

            this.container.html(html);
            if (this.easyMDE) {
                this.easyMDE.toTextArea();
                this.easyMDE = null;
            }
            this.easyMDE = new EasyMDE(
                {element: this.container.find('textarea')[0], maxHeight: "250px", forceSync: true}
            );

        },

        toggleButtons: function() {

            this.container.find('[data-action="save"]').prop('disabled', false);
            this.container.find('[data-action="new"]').prop('disabled', false);
            this.container.find('[data-action="delete"]').prop('disabled', false);
            this.navigation = JSON.parse(document.getElementById('snippet-navigation').textContent);
            this.container.find('[data-action="prev"]').prop('disabled', this.navigation.prev === null);
            this.container.find('[data-action="next"]').prop('disabled', this.navigation.next === null);

        },

        prev: function() {

            this.render(this.navigation.prev);

        },

        next: function() {

            this.render(this.navigation.next);

        }

    }

    $.fn.Snippet = function(settings) {

        let snippet = new SnippetApi({
            container: $(this),
            updateUrl: settings.updateUrl
        });
        snippet.init();

        return this;

    };

}( jQuery ));