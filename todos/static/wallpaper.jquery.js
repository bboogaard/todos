(function( $ ) {

    function WallpaperApi(settings) {
        this.element = settings.element;
        this.items = settings.items;

        this.index = 0;
    }

    WallpaperApi.prototype = {

        init: function() {

            var self = this;

            this.setBackground();

            setInterval(function() {
                self.nextBackground();
            }, 30000);

            this.element.on('next-wallpaper', function() {
                self.nextBackground();
            });

        },

        nextBackground: function() {

            if (this.index < this.items.length - 1) {
                this.index += 1;
            }
            else {
                this.index = 0;
            }
            this.setBackground();

        },

        setBackground: function() {

            this.element.css('background', 'url(' + this.items[this.index] + ') no-repeat center center fixed');

        }

    }

    $.fn.wallPaper = function(settings) {

        let wallPaper = new WallpaperApi({
            element: $(this),
            items: settings.items
        });
        wallPaper.init();

        return this;

    };

})(jQuery);