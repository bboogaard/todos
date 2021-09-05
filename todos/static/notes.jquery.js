(function( $ ) {

    function NotesApi(settings) {
        this.notes = settings.notes;
        this.saveButton = settings.saveButton;
        this.newButton = settings.newButton;
        this.deleteButton = settings.deleteButton;
        this.prevButton = settings.prevButton;
        this.nextButton = settings.nextButton;
        this.provider = settings.provider;

        this.items = [];
        this.index = 0;
    }

    NotesApi.prototype = {

        init: function() {

            this.init_edit_handlers();

            this.render(true);

        },

        init_edit_handlers: function() {

            let self = this;

            this.saveButton.click(function () {
                self.save(self.notes.val());
            });

            this.newButton.click(function () {
                self.new();
            });

            this.deleteButton.click(function () {
                self.delete();
            });

            this.prevButton.click(function () {
                self.prev();
            });

            this.nextButton.click(function () {
                self.next();
            });

        },

        render: function(refresh=false) {

            if (refresh) {
                [this.items, this.index] = this.provider.get();
            }

            if (!this.items.length) {
                this.items.push('');
            }

            this.notes.val(this.items[this.index]);
            this.prevButton.prop('disabled', this.index === 0);
            this.nextButton.prop('disabled', this.index === this.items.length - 1);
            this.notes.focus();

        },

        save: function(value='') {

            if (value) {
                this.items[this.index] = value;
            }
            this.provider.save(this.items, this.index);
            this.render();

        },

        new: function() {

            this.items.push('');
            this.index = this.items.length - 1;
            this.save();

        },

        delete: function() {

            this.items.splice(this.index, 1);
            this.index = this.index - (this.index > 0 ? 1 : 0);
            this.save();

        },

        prev: function() {

            this.index -= 1;
            this.save();

        },

        next: function() {

            this.index += 1;
            this.save();

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