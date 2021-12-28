function ChecklistProviderLocal(settings) {
    this.storageName = settings.storageName;
    this.searching = settings.searching;
}

ChecklistProviderLocal.prototype = {

    get: function () {

        let raw = localStorage.getItem(this.storageName);
        return raw ? raw.split('\n') : [];

    },

    save: function (items) {

        let data = items.join('\n');
        localStorage.setItem(this.storageName, data);

    },

    activate: function (items) {}

}