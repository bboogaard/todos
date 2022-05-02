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
        provider.importUrl = this.settings.urls['import'];
        return provider;

    },

    createNotesProvider: function () {

        let provider = this.createProvider();
        provider.importUrl = this.settings.urls['import'];
        return provider;

    },

    createSnippetsProvider: function () {

        let provider = this.createProvider();
        provider.importUrl = this.settings.urls['import'];
        return provider;

    },

    createFilesProvider: function () {

        let provider = this.createProvider();
        provider.importUrl = this.settings.urls['import'];
        return provider;

    },

    createImagesProvider: function () {

        let provider = this.createProvider();
        provider.carouselUrl = this.settings.carouselUrl;
        provider.importUrl = this.settings.urls['import'];
        return provider;

    },

    createEventsProvider: function () {

        let self = this;
        let provider = this.createProvider();
        provider.weeks = function (data) {
            return $.ajax({
                url: self.settings.urls['weeks'],
                type: "GET",
                data: data
            });
        }
        provider.year = this.settings.year;
        provider.month = this.settings.month;
        return provider;

    },

    createCarouselProvider: function () {

        let self = this;

        let provider = this.createProvider();
        provider.getStartPage = function () {
            return $.ajax({
                url: self.settings.urls['find_page'],
                type: "GET",
                data: {id: self.settings.imageId}
            });
        }
        return provider;

    },

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
    },

    createEvents: function() {
        return new ApiProviderFactory(JSON.parse(document.getElementById('event-vars').textContent)).createEventsProvider();
    },

    createCarousel: function() {
        return new ApiProviderFactory(JSON.parse(document.getElementById('carousel-vars').textContent)).createCarouselProvider();
    }

}