function Widget(settings) {
    this.id = settings.id;
    this.url = settings.url;
    this.refreshInterval = settings.refreshInterval;
}

Widget.prototype = {

    addCallback: function(callback) {

        this.callback = callback;

    },

    init: function() {

        let self = this;

        if (this.refreshInterval) {
            setInterval(function() {
                self.load();
            }, this.refreshInterval);
        }

    },

    load: function() {

        let self = this;

        $.get(this.url + window.location.search)
        .done(function(res) {
            $('#' + self.id).find('.card-text').html(res.html);
            if (self.callback) {
                self.callback();
            }
        });

    }

}