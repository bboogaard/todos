(function( $ ) {

    function HistoricalDatesApi(settings) {
        this.container = settings.container;
        this.dates = settings.dates;

        this.index = 0;
    }

    HistoricalDatesApi.prototype = {

        init: function() {

            let self = this;

            this.index = 0;

            this.container.on('click', 'a', function(event) {
                event.preventDefault();
                self.render();
            });

            this.render();

        },

        render: function() {

            if (this.index >= this.dates.length) {
                this.index = 0;
            }

            let date = this.dates[this.index];

            this.index += 1;

            this.container.find('a').css('display', this.dates.length === 1 ? 'none': '');

            this.container.find('em').text(date.date);
            this.container.find('blockquote').text(date.event);

        }

    }

    $.fn.HistoricalDates = function(settings) {

        let dates = new HistoricalDatesApi({
            container: $(this),
            dates: settings.dates
        });
        dates.init();

        return this;

    };

}( jQuery ));