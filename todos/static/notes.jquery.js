(function( $ ) {

    const PREFIX_NOTE_TYPE_PLAIN_TEXT = '[PT]';
    const PREFIX_NOTE_TYPE_MARKDOWN = '[MD]';

    function NotesApi(settings) {
        this.notes = settings.notes;
        this.saveButton = settings.saveButton;
        this.newButton = settings.newButton;
        this.deleteButton = settings.deleteButton;
        this.prevButton = settings.prevButton;
        this.nextButton = settings.nextButton;
        this.provider = settings.provider;
        this.enableMarkdown = settings.enableMarkdown;

        this.items = [];
        this.index = 0;
        this.searching = settings.provider.searching;
        this.easyMDE = null;
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

            this.enableMarkdown.on('click init', function() {
                self.toggleMarkdown($(this).prop('checked'));
            });

        },

        render: function(refresh=false) {

            if (refresh) {
                [this.items, this.index] = this.provider.get();
            }

            if (!this.items.length) {
                this.items.push(PREFIX_NOTE_TYPE_PLAIN_TEXT);
            }

            this.notes.val(this.renderItem(this.items[this.index]));
            this.prevButton.prop('disabled', this.index === 0);
            this.nextButton.prop('disabled', this.index === this.items.length - 1);
            this.notes.focus();

        },

        save: function(value='') {

            if (value) {
                this.items[this.index] = this.saveItem(value);
            }
            this.provider.save(this.items, this.index);
            this.render();

        },

        new: function() {

            this.items.push(PREFIX_NOTE_TYPE_PLAIN_TEXT);
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

        },

        renderItem: function(value) {

            var startPos;

            let prefix = value.substring(0, 4);
            switch(prefix) {
                case PREFIX_NOTE_TYPE_PLAIN_TEXT:
                    this.enableMarkdown.prop('checked', false).trigger('init');
                    startPos = 4;
                    break;
                case PREFIX_NOTE_TYPE_MARKDOWN:
                    this.enableMarkdown.prop('checked', true).trigger('init');
                    startPos = 4;
                    break;
                default:
                    this.enableMarkdown.prop('checked', false).trigger('init');
                    startPos = 0;
            }
            return value.substring(startPos);

        },

        saveItem: function(value) {

            let prefix = this.enableMarkdown.prop('checked') ? PREFIX_NOTE_TYPE_MARKDOWN : PREFIX_NOTE_TYPE_PLAIN_TEXT;
            return prefix + value;

        },

        toggleMarkdown: function(enabled) {

            if (enabled) {
                this.easyMDE = new EasyMDE({element: this.notes[0], maxHeight: "200px"});
            }
            else if (this.easyMDE) {
                this.easyMDE.toTextArea();
                this.easyMDE = null;
            }

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
            provider: settings.provider,
            enableMarkdown: settings.enableMarkdown
        });
        notes.init();

        return this;

    };

}( jQuery ));