function ApiProviderFactory(settings) {
    this.settings = settings;
}

ApiProviderFactory.prototype = {

    create_todos_provider: function () {

        let provider = new ApiProvider({
            urls: this.settings.urls,
            search_query: this.settings.search_query
        });
        let self = this;
        provider.activate = function (data) {
            return $.ajax({
                url: self.settings.urls['activate'],
                type: "POST",
                data: JSON.stringify( data ),
                contentType: "application/json; charset=utf-8",
                dataType: "json"
            });
        }
        return provider;

    }

}

let apiProviderFactory = {

    create_todos: function() {
        return new ApiProviderFactory(JSON.parse(document.getElementById('todo-vars').textContent)).create_todos_provider();
    }

}