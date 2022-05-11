(function( $ ) {

    function BackgroundApi(settings) {
        this.element = settings.element;
        this.provider = settings.provider;
        this.gallery = this.provider.gallery;

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
            provider: settings.provider
        });
        background.init();

        return this;

    };

})(jQuery);