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
        this.search_query = settings.provider.search_query;
        this.searching = this.search_query !== null;
    }

    NotesApi.prototype = {

        init: function() {

            this.init_edit_handlers();

            let page = Cookies.get('notes-page');
            this.load_items(page !== undefined ? parseInt(page, 10) : null);

        },

        init_edit_handlers: function() {

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

        load_items: function(page=null) {

            let self = this;

            let data = {};
            if (page !== null) {
                data.page = page;
            }
            if (this.search_query !== null) {
                data.id = this.search_query;
            }

            this.provider.list(data).done(function(items) {
                self.render(items);
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

        save: function(page) {

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

            $.when(action(data))
            .then(function(res) {
                self.load_items(page ? page : self.item !== null ? self.page : 1);
            });

        },

        new: function() {

            let self = this;

            $.when(this.provider.create({text: ''}))
            .then(function(res) {
                self.save(1);
            });

        },

        delete: function() {

            let self = this;

            let data = {id: this.item.id}

            $.when(self.provider.delete(data))
                .then(function() {
                    self.load_items(self.items.previous !== null ? self.page - 1 : 1);
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