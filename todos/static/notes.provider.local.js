function NotesProviderLocal(settings) {
    this.storageName = settings.storageName;
    this.searching = settings.searching;
}

NotesProviderLocal.prototype = {

    get: function () {

        let raw = localStorage.getItem(this.storageName);
        let items = raw ? raw.split('|') : ['0'];
        let index = parseInt(items.splice(items.length - 1, 1)[0]);
        return [items, index];

    },

    save: function (items, index) {

        let payload = items.slice();
        payload.push(index);
        let data = payload.join('|');
        localStorage.setItem(this.storageName, data);

    }

}