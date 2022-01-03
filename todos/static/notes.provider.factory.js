function NotesProviderFactory(json_vars) {
    this.items = json_vars.items;
    this.index = json_vars.index;
    this.saveUrl = json_vars.saveUrl;
    this.searching = json_vars.searching;
}

NotesProviderFactory.prototype = {

    create_provider: function (type) {
        switch (type) {
            case "local":
                return new NotesProviderLocal({
                    storageName: 'notes',
                    searching: false
                })
            case "remote":
                return new NotesProviderRemote({
                    items: this.items,
                    index: this.index,
                    saveUrl: this.saveUrl,
                    searching: this.searching
                });
        }

    }

}

var notesProviderFactory = {

    create: function(type) {
        return new NotesProviderFactory(JSON.parse(document.getElementById('note-vars').textContent)).create_provider(type);
    }

}