function ApiProviderFactory(settings) {
    this.settings = settings;
}

ApiProviderFactory.prototype = {

    createProvider: function() {

        return new ApiProvider({
            urls: this.settings.urls,
            searchQuery: this.settings.searchQuery
        });

    },

    createTodosProvider: function () {

        let self = this;
        let provider = this.createProvider();
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

    createNotesProvider: function () {

        return this.createProvider();

    },

    createSnippetsProvider: function () {

        return this.createProvider();

    },

    createFilesProvider: function () {

        return this.createProvider();

    },

    createImagesProvider: function () {

        let provider = this.createProvider();
        provider.carouselUrl = this.settings.carouselUrl;
        return provider;

    }

}

let apiProviderFactory = {

    createTodos: function() {
        return new ApiProviderFactory(JSON.parse(document.getElementById('todo-vars').textContent)).createTodosProvider();
    },

    createNotes: function() {
        return new ApiProviderFactory(JSON.parse(document.getElementById('note-vars').textContent)).createNotesProvider();
    },

    createSnippets: function() {
        return new ApiProviderFactory(JSON.parse(document.getElementById('snippet-vars').textContent)).createSnippetsProvider();
    },

    createFiles: function() {
        return new ApiProviderFactory(JSON.parse(document.getElementById('file-vars').textContent)).createFilesProvider();
    },

    createImages: function() {
        return new ApiProviderFactory(JSON.parse(document.getElementById('image-vars').textContent)).createImagesProvider();
    }

}