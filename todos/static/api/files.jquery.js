(function( $ ) {

    function FilesApi(settings) {
        this.container = settings.container;
        this.provider = settings.provider;

        this.items = {};
        this.searchQuery = settings.provider.searchQuery;
        this.searching = this.searchQuery !== null;
    }

    FilesApi.prototype = {

        init: function() {

            this.initEditHandlers();

            this.loadItems();

        },

        initEditHandlers: function() {

            let self = this;

            this.container.on('click', 'a[data-id]', function(event) {
                event.preventDefault();
                self.delete($(this).attr('data-id'));
            });

        },

        loadItems: function() {

            let self = this;

            let data = {};
            if (this.searchQuery !== null) {
                data.id = this.searchQuery;
            }

            this.provider.list(data).done(function(items) {
                self.render(items);
            }).fail(function() {
                self.render([]);
            });

        },

        render: function(items) {

            this.items = items;
            let lines = this.items.map(function(item) {
                return '<a href="' + item.url + '" target="_blank">' + item.name + '</a>&nbsp;' +
                '<small><a href="" data-id="' + item.id + '">delete</a></small><br>';
            });
            let html = lines.length ? lines.join('') : 'No files uploaded yet';
            this.container.html(html);

        },

        delete: function(id) {

            let self = this;

            let data = {id: id};

            $.when(this.provider.delete(data))
            .then(self.loadItems());
        }

    }

    $.fn.Files = function(settings) {

        let files = new FilesApi({
            container: $(this),
            provider: settings.provider
        });
        files.init();

        return this;

    };

}( jQuery ));