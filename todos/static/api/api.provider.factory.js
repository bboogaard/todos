function ApiProviderFactory(settings) {
    this.settings = settings;
}

ApiProviderFactory.prototype = {

    create_todos_provider: function () {

        return new ApiProvider({
            urls: this.settings.urls,
            search_query: this.settings.search_query
        });

    }

}

let apiProviderFactory = {

    create_todos: function() {
        return new ApiProviderFactory(JSON.parse(document.getElementById('todo-vars').textContent)).create_todos_provider();
    }

}