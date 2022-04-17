(function( $ ) {

    function TodosApi(settings) {
        this.list = settings.list;
        this.saveButton = settings.saveButton;
        this.deleteButton = settings.deleteButton;
        this.activateButton = settings.activateButton;

        this.provider = settings.provider;
        this.searchQuery = settings.provider.searchQuery;
        this.searching = this.searchQuery !== null;
    }

    TodosApi.prototype = {

        init: function() {

            if (!this.searching) {
                this.initEditHandlers();
            }
            else {
                this.initSearchHandlers();
            }

            this.loadItems();

        },

        initEditHandlers: function() {

            let self = this;

            this.saveButton.click(function () {
                self.save();
            });

            this.deleteButton.click(function () {
                self.delete();
            });

            this.list.on('input', function () {
                if ($(this).html() === '') {
                    $(this).html('<li>Enter item</li>');
                }
            });

        },

        initSearchHandlers: function() {

            let self = this;

            this.activateButton.click(function () {
                self.activate();
            });

        },

        loadItems: function () {

            let self = this;

            let data = {};
            if (this.searchQuery) {
                data.search = this.searchQuery;
            }

            this.provider.list(data)
                .done(function(items) {
                    self.render(items);
                });

        },

        render: function(items) {

            this.list.empty();
            if (!items.length && !this.searching) {
                items.push({
                    'id': null,
                    'description': 'Enter item'
                });
            }

            let html = items.map(function (item) {
                return '<li data-id="' + item['id'] + '"><input type="checkbox"> ' + item['description'] + '</li>';
            }).join("");
            this.list.html(html);

        },

        save: function() {

            let self = this;

            let ids = [];

            let items = this.list.find('li').map(function () {
                let id = ids.indexOf($(this).data('id')) === -1 ? $(this).data('id') : null;
                ids.push($(this).data('id'));
                return {
                    id: id,
                    description: $(this).text().trim()
                };
            }).get();

            let createItems = items.filter(function(item) {
                return item.id === null;
            }).map(function(item) {
                return {
                    description: item.description
                }
            });

            let updateItems = items.filter(function(item) {
                return item.id !== null;
            });

            $.when(this.provider.create(createItems), this.provider.update(updateItems))
            .then(function() {
                self.loadItems();
            });

        },

        activate: function() {

            let self = this;

            let ids = this.list.find('input[type="checkbox"]:checked').map(function () {
                return $(this).parent().data('id');
            }).get();

            $.when(this.provider.activate({id: ids}))
            .then(function() {
                self.loadItems();
            });

        },

        delete: function() {

            let self = this;

            let ids = this.list.find('input[type="checkbox"]:checked').map(function () {
                return $(this).parent().data('id');
            }).get();

            $.when(this.provider.delete({id: ids}))
            .then(function() {
                self.loadItems();
            });

        }

    }

    $.fn.Todos = function(settings) {

        let todos = new TodosApi({
            list: $(this),
            saveButton: settings.saveButton,
            deleteButton: settings.deleteButton,
            activateButton: settings.activateButton,
            provider: settings.provider
        });
        todos.init();

        return this;

    };

}( jQuery ));