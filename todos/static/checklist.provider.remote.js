function ChecklistProviderRemote(settings) {
    this.items = settings.items;
    this.saveUrl = settings.saveUrl;
    this.activateUrl = settings.activateUrl;
    this.searching = settings.searching;
}

ChecklistProviderRemote.prototype = {

    get: function () {

        return this.items;

    },

    save: function (items) {

        let data = {
            "items": items
        }

        $.post(this.saveUrl, data);

    },

    activate: function (items) {

        let data = {
            "items": items
        }

        $.post(this.activateUrl, data);

    }

}