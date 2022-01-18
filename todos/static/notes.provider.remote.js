function NotesProviderRemote(settings) {
    this.items = settings.items;
    this.types = settings.types;
    this.index = settings.index;
    this.saveUrl = settings.saveUrl;
    this.searching = settings.searching;
}

NotesProviderRemote.prototype = {

    const PREFIX_NOTE_TYPE_PLAIN_TEXT = '[PT]';
    const DB_NOTE_TYPE_PLAIN_TEXT = 'plain_text';
    const PREFIX_NOTE_TYPE_MARKDOWN = '[MD]';
    const DB_NOTE_TYPE_MARKDOWN = 'markdown';

    get: function () {

        return [this.joinTypes(this.items, this.types), this.index];

    },

    save: function (items, index) {

        let data = {
            "items": this.splitTypes(items),
            "types": this.splitTypes(items, true),
            "index": index,
            "searching": this.searching
        }

        $.post(this.saveUrl, data);

    },

    splitTypes: function(items, getType=false) {

        return items.map(function(item) {
            var startPos, noteType;

            let prefix = value.substring(0, 4);
            switch(prefix) {
                case PREFIX_NOTE_TYPE_PLAIN_TEXT:
                    noteType = DB_NOTE_TYPE_PLAIN_TEXT;
                    startPos = 4;
                    break;
                case PREFIX_NOTE_TYPE_MARKDOWN:
                    noteType = DB_NOTE_TYPE_MARKDOWN;
                    startPos = 4;
                    break;
                default:
                    noteType = DB_NOTE_TYPE_PLAIN_TEXT;
                    startPos = 0;
            }
            return getType ? noteType : value.substring(startPos);
        });

    },

    joinTypes: function(items, types) {

        return items.map(function(item, index) {
            var noteType;

            switch(types[index]) {
                case DB_NOTE_TYPE_PLAIN_TEXT:
                    noteType = PREFIX_NOTE_TYPE_PLAIN_TEXT;
                    break;
                case DB_NOTE_TYPE_MARKDOWN:
                    noteType = PREFIX_NOTE_TYPE_MARKDOWN;
                    break;
                default:
                    noteType = PREFIX_NOTE_TYPE_PLAIN_TEXT;
            }
            return noteType + item;
        })

    }

}