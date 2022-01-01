function Widget(settings) {
    this.id = settings.id;
    this.url = settings.url;
    this.refreshInterval = settings.refreshInterval;
}

Widget.prototype = {

    load: function(callback=null) {

        let self = this;

        $.get(this.url)
        .done(function(res) {
            $('#' + self.id).find('.card-text').html(res.html);
            if (callback) {
                callback();
            }
        });

    }

}