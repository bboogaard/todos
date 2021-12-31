function Widget(settings) {
    this.id = settings.id;
    this.url = settings.url;
    this.callback = settings.callback;
    this.refreshInterval = settings.refreshInterval;
}

Widget.prototype = {

    load: function() {

        let self = this;

        $.get(this.url)
        .done(function(res) {
            $('#' + self.id).find('.card-text').html(res.html);
            self.initJs();
        });

    },

    initJs: function() {

        if (this.callback) {
            this.callback();
        }

    }

}