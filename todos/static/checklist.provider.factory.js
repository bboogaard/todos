function ChecklistProviderFactory(json_vars) {
    this.items = json_vars.items;
    this.saveUrl = json_vars.saveUrl;
    this.activateUrl = json_vars.activateUrl;
    this.searching = json_vars.searching;
}

ChecklistProviderFactory.prototype = {

    create_provider: function (type) {
        switch (type) {
            case "local":
                return new ChecklistProviderLocal({
                    storageName: 'todos-list',
                    searching: false
                })
            case "remote":
                return new ChecklistProviderRemote({
                    items: this.items,
                    saveUrl: this.saveUrl,
                    activateUrl: this.activateUrl,
                    searching: this.searching
                })
        }

    }

}

var checkListProviderFactory = {

    create: function(type) {
        return new ChecklistProviderFactory(JSON.parse(document.getElementById('todo-vars').textContent)).create_provider(type);
    }

}