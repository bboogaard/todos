function NotesProviderRemote(settings) {
    this.items = settings.items;
    this.index = settings.index;
    this.saveUrl = settings.saveUrl;
    this.searching = settings.searching;
}

NotesProviderRemote.prototype = {

    get: function () {

        return [this.items, this.index];

    },

    save: function (items, index) {

        let data = {
            "items": items,
            "index": index,
            "searching": this.searching
        }

        $.post(this.saveUrl, data);

    }

}