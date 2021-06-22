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
               if (self.index < self.items.length - 1){
                   self.index += 1;
               }
               else {
                   self.index = 0;
               }
               console.log(self.items[self.index]);
            }, 30000);

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