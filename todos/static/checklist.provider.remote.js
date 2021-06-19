function ChecklistProviderRemote(settings) {
    this.items = settings.items;
    this.saveUrl = settings.saveUrl;
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

    }

}