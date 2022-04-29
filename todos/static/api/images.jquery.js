(function( $ ) {

    function ImagesApi(settings) {
        this.container = settings.container;
        this.provider = settings.provider;

        this.items = {};
        this.carouselUrl = settings.provider.carouselUrl;
        this.searchQuery = settings.provider.searchQuery;
        this.searching = this.searchQuery !== null;
    }

    ImagesApi.prototype = {

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

            this.container.on('click', 'a[data-carousel-id]', function(event) {
                event.preventDefault();
                $('#todos-modal').FullModal({
                    title: 'Images',
                    url: self.carouselUrl + '?image_id=' + $(this).attr('data-carousel-id')
                });
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
                return '<div class="thumbnail" style="display: inline-grid">' +
                '<a href="' + item.url + '" data-carousel-id="' + item.id + '" target="_blank">' +
                '<img src="' + item.thumbnail + '" alt="' + item.name + '" style="width:50px"></a>' +
                '<small><a href="" data-id="' + item.id + '">delete</a></small>' +
                '</div>&nbsp;&nbsp;';
            });
            let html = lines.length ? lines.join('') : 'No images uploaded yet';
            this.container.html(html);

        },

        delete: function(id) {

            let self = this;

            let data = {id: id};

            $.when(this.provider.delete(data))
            .then(function() {
                self.loadItems();
            });
        }

    }

    $.fn.Images = function(settings) {

        let images = new ImagesApi({
            container: $(this),
            provider: settings.provider
        });
        images.init();

        return this;

    };

}( jQuery ));