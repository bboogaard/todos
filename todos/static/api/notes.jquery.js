(function( $ ) {

    function NotesApi(settings) {
        this.notes = settings.notes;
        this.saveButton = settings.saveButton;
        this.newButton = settings.newButton;
        this.deleteButton = settings.deleteButton;
        this.prevButton = settings.prevButton;
        this.nextButton = settings.nextButton;
        this.provider = settings.provider;

        this.items = {};
        this.item = null;
        this.page = 1;
        this.searchQuery = settings.provider.searchQuery;
        this.searching = this.searchQuery !== null;
    }

    NotesApi.prototype = {

        init: function() {

            this.initEditHandlers();

            let page = Cookies.get('notes-page');
            this.loadItems(page !== undefined ? parseInt(page, 10) : null);

        },

        initEditHandlers: function() {

            let self = this;

            this.saveButton.click(function () {
                self.save();
            });

            this.newButton.click(function () {
                self.new();
            });

            if (!this.searching) {
                this.deleteButton.click(function () {
                    self.delete();
                });
            }

            this.prevButton.click(function () {
                self.prev();
            });

            this.nextButton.click(function () {
                self.next();
            });

        },

        loadItems: function(page=null) {

            let self = this;

            let data = {};
            if (this.searchQuery !== null) {
                data.id = this.searchQuery;
            }
            else if (page !== null) {
                data.page = page;
            }

            this.provider.list(data).done(function(items) {
                self.render(items);
            }).fail(function() {
                self.render({
                    results: [],
                    count: 0,
                    page: 1,
                    previous: null,
                    next: null
                });
            });

        },

        render: function(items) {

            this.items = items;
            this.item = this.items.results.length > 0 ? this.items.results[0] : null;
            this.page = this.items.page;
            if (!this.searching) {
                Cookies.set('notes-page', this.page);
            }
            else {
                Cookies.remove('notes-page', this.page);
            }

            this.notes.val(this.item !== null ? this.item.text : "");
            this.deleteButton.prop('disabled', this.item === null);
            this.prevButton.prop('disabled', this.items.previous === null);
            this.nextButton.prop('disabled', this.items.next === null);
            this.notes.focus();

        },

        saveItem: function() {

            let self = this;

            let data = this.item !== null ? {id: this.item.id} : {};
            data.text = this.notes.val();
            let action = function(data) {
                 if (self.item !== null) {
                     return self.provider.update(data);
                 }
                 else {
                     return self.provider.create(data)
                 }
            }

            return action(data);

        },

        save: function(page) {

            let self = this;

            $.when(this.saveItem())
                .then(function() {
                    self.loadItems(page ? page : self.item !== null ? self.page : 1);
                });

        },

        new: function() {

            let self = this;

            $.when(this.saveItem())
                .then(function() {
                    $.when(self.provider.create({text: ''}))
                        .then(function() {
                            self.loadItems(1);
                        });
                });

        },

        delete: function() {

            let self = this;

            let data = {id: this.item.id}

            $.when(self.provider.delete(data))
                .then(function() {
                    self.loadItems(self.items.previous !== null ? self.page - 1 : 1);
                });

        },

        prev: function() {

           this.save(this.page - 1)

        },

        next: function() {

            this.save(this.page + 1);

        }

    }

    $.fn.Notes = function(settings) {

        let notes = new NotesApi({
            notes: $(this),
            saveButton: settings.saveButton,
            newButton: settings.newButton,
            deleteButton: settings.deleteButton,
            prevButton: settings.prevButton,
            nextButton: settings.nextButton,
            provider: settings.provider
        });
        notes.init();

        return this;

    };

}( jQuery ));