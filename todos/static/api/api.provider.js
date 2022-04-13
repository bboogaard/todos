function ApiProvider(settings) {
    this.urls = settings.urls;
    this.search_query = settings.search_query;
}

ApiProvider.prototype = {

    list: function () {

        return $.ajax({
            url: this.urls['list'],
            type: "GET",
            data: this.search_query
        });

    },

    create: function (data) {

        return $.ajax({
            url: this.urls['create'],
            type: "POST",
            data: JSON.stringify( data ),
            contentType: "application/json; charset=utf-8",
            dataType: "json"
        });

    },

    update: function (data) {

        return $.ajax({
            url: this.urls['update'],
            type: "POST",
            data: JSON.stringify( data ),
            contentType: "application/json; charset=utf-8",
            dataType: "json"
        });

    },

    delete: function (data) {

        return $.ajax({
            url: this.urls['delete'],
            type: "POST",
            data: JSON.stringify( data ),
            contentType: "application/json; charset=utf-8",
            dataType: "json"
        });

    }

}
