(function( $ ) {

    function SnippetApi(settings) {
        this.container = settings.container;
        this.updateUrl = settings.updateUrl;
        this.navigation = {
            prev: null,
            next: null
        }

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
                    self.container.html(res.html);
                    self.parseNavigation();
                });
            });

            this.container.on('click', '[data-action="save"]', function () {
                $(this).parents('form').submit();
            });

            this.container.on('click', '[data-action="new"]', function () {
                $(this).attr('action', self.updateUrl);
                $(this).parents('form').submit();
            });

        },

        render: function(object_id=null) {

            let self = this;

            $.get(this.updateUrl + (object_id ? "?object_id=" + object_id : ""))
            .done(function(res) {
                self.container.html(res.html);
                new EasyMDE({element: self.container.find('textarea')[0]});
                self.parseNavigation();
            });

        },

        parseNavigation: function() {

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