function ChecklistProviderFactory(json_vars) {
    this.items = json_vars.items;
    this.saveUrl = json_vars.saveUrl;
}

ChecklistProviderFactory.prototype = {

    create: function (type) {
        switch (type) {
            case "local":
                return new ChecklistProviderLocal({
                    storageName: 'todos-list'
                })
            case "remote":
                return new ChecklistProviderRemote({
                    items: this.items,
                    saveUrl: this.saveUrl
                })
        }

    }

}

const checkListProviderFactory = new ChecklistProviderFactory(JSON.parse(document.getElementById('json-vars').textContent));