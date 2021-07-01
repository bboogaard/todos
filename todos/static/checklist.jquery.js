(function( $ ) {

    function CheckListApi(settings) {
        this.list = settings.list;
        this.saveButton = settings.saveButton;
        this.deleteButton = settings.deleteButton;
        this.activateButton = settings.activateButton;
        this.provider = settings.provider;

        this.items = [];
        this.searching = settings.searching;
    }

    CheckListApi.prototype = {

        init: function() {

            if (!this.searching) {
                this.init_edit_handlers();
            }
            else {
                this.init_search_handlers();
            }

            this.render(true);

        },

        init_edit_handlers: function() {

            let self = this;

            this.saveButton.click(function () {
                self.save();
            });

            this.deleteButton.click(function () {
                self.list.find('input[type="checkbox"]:checked').each(function () {
                    self.delete($(this).attr('id'));
                });
                self.save();
            });

            this.list.on('input', function () {
                if ($(this).html() === '') {
                    $(this).html('<li>Enter item</li>');
                }
            });

        },

        init_search_handlers: function() {

            let self = this;

            this.activateButton.click(function () {
                self.activate();
            });

        },

        render: function(refresh=false) {

            if (refresh) {
                this.items = this.provider.get();
            }

            this.list.empty();
            if (!this.items.length && !this.searching) {
                this.items.push('Enter item');
            }

            let html = this.items.map(function (item, index) {
                return '<li><input type="checkbox" id="item-' + index + '"> ' + item + '</li>';
            }).join("");
            this.list.html(html);

        },

        save: function() {

            this.items = this.list.find('li').map(function () {
                return $(this).text().trim();
            }).get();

            this.provider.save(this.items);
            this.render();

        },

        activate: function() {

            let items = this.list.find('input[type="checkbox"]:checked').map(function () {
                return $(this).parent().text().trim();
            }).get();
            this.provider.activate(this.items);
            this.list.find('input[type="checkbox"]:checked').parent().remove();

        },

        delete: function(id) {

            this.list.find('#' + id).parent().remove();

        }

    }

    $.fn.checkList = function(settings) {

        let checkList = new CheckListApi({
            list: $(this),
            saveButton: settings.saveButton,
            deleteButton: settings.deleteButton,
            activateButton: settings.activateButton,
            provider: settings.provider,
            searching: settings.searching
        });
        checkList.init();

        return this;

    };

}( jQuery ));