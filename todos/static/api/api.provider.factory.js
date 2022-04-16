function ApiProviderFactory(settings) {
    this.settings = settings;
}

ApiProviderFactory.prototype = {

    create_provider: function() {

        return new ApiProvider({
            urls: this.settings.urls,
            search_query: this.settings.search_query
        });

    },

    create_todos_provider: function () {

        let self = this;
        let provider = this.create_provider();
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

    },

    create_notes_provider: function () {

        return this.create_provider();

    }

}

let apiProviderFactory = {

    create_todos: function() {
        return new ApiProviderFactory(JSON.parse(document.getElementById('todo-vars').textContent)).create_todos_provider();
    },

    create_notes: function() {
        return new ApiProviderFactory(JSON.parse(document.getElementById('note-vars').textContent)).create_notes_provider();
    }

}