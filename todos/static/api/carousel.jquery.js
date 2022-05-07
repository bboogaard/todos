(function( $ ) {

    function CarouselApi(settings) {
        this.frame = settings.frame;
        this.prevButton = settings.prevButton;
        this.nextButton = settings.nextButton;
        this.provider = settings.provider;

        this.items = {};
        this.item = null;
        this.page = 1;
    }

    CarouselApi.prototype = {

        init: function() {

            let self = this;

            this.initHandlers();

            $.when(this.provider.getStartPage())
            .then(function(res) {
                self.loadItems(parseInt(res.page, 10));
            });

        },

        initHandlers: function() {

            let self = this;

            this.prevButton.click(function(event) {
                event.preventDefault();
                self.prev();
            });

            this.nextButton.click(function(event) {
                event.preventDefault();
                self.next();
            });

        },

        loadItems: function(page=null) {

            let self = this;

            let data = {};
            if (page !== null) {
                data.page = page;
            }

            this.provider.list(data).done(function(items) {
                self.render(items);
            }).fail(function() {
                self.render([]);
            });

        },

        render: function(items) {

            this.items = items;
            this.item = this.items.results.length > 0 ? this.items.results[0] : null;
            this.page = this.items.page;
            this.prevButton.toggle(this.items.previous !== null);
            this.nextButton.toggle(this.items.next !== null);

            let template = '<div class="carousel-item">' +
            '<img class="img-fluid" src="<%= image %>" alt="" style="">' +
            '</div>';

            let context = {
                image: this.item.image
            }

            let html = ejs.render(template, context);
            this.frame.html(html);

        },

        prev: function () {

            this.loadItems(this.page - 1);

        },

        next: function () {

            this.loadItems(this.page + 1);

        }

    }

    $.fn.CarouselApi = function(settings) {

        let carousel = new CarouselApi({
            frame: $(this),
            prevButton: settings.prevButton,
            nextButton: settings.nextButton,
            provider: settings.provider
        });
        carousel.init();

        return this;

    };

}( jQuery ));