(function( $ ) {

    function BackgroundApi(settings) {
        this.element = settings.element;
        this.provider = settings.provider;
        this.gallery = this.provider.gallery;
        this.galleryToggle = settings.galleryToggle;
        this.galleryProvider = settings.galleryProvider;

        this.items = {};
        this.item = null;
        this.page = 1;
    }

    BackgroundApi.prototype = {

        init: function() {

            var self = this;

            setInterval(function() {
                self.nextBackground();
            }, 30000);

            this.element.on('next-wallpaper', function() {
                self.nextBackground();
            }).trigger('next-wallpaper');

            this.galleryToggle.click(function(event) {
                event.preventDefault();
                let data = self.galleryToggle.map(function() {
                    return {
                        id: $(this).attr('data-gallery-id'),
                        active: false
                    }
                }).get();
                let activeGalleryItem = $(this);
                let activeData = [
                    {
                        id: activeGalleryItem.attr('data-gallery-id'),
                        active: true
                    }
                ];
                $.when(self.galleryProvider.update(data))
                .then(function() {
                    $.when(self.galleryProvider.update(activeData))
                    .then(function() {
                        self.gallery = activeGalleryItem.attr('data-gallery-id');
                        self.galleryToggle.removeClass('active');
                        activeGalleryItem.addClass('active');
                        self.loadItems();
                    });
                })
            });

        },

        nextBackground: function() {

            this.loadItems(this.items.next !== undefined && this.items.next !== null ? this.page + 1 : 1);

        },

        loadItems: function(page=null) {

            let self = this;

            let data = {};
            if (this.gallery !== null) {
                data.gallery = this.gallery;
            }
            if (page !== null) {
                data.page = page;
            }

            this.provider.list(data).done(function(items) {
                self.setBackground(items);
            });

        },

        setBackground: function(items) {

            this.items = items;
            this.item = this.items.results.length > 0 ? this.items.results[0] : null;
            this.page = this.items.page;
            if (this.item) {
                this.element.css('background', 'url(' + this.item.image + ') no-repeat center center fixed');
            }

        }

    }

    $.fn.Background = function(settings) {

        let background = new BackgroundApi({
            element: $(this),
            galleryToggle: settings.galleryToggle,
            provider: settings.provider,
            galleryProvider: settings.galleryProvider
        });
        background.init();

        return this;

    };

})(jQuery);