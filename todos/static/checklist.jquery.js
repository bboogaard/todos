(function( $ ) {

    function CheckListApi(settings) {
        this.list = settings.list;
        this.saveButton = settings.saveButton;
        this.deleteButton = settings.deleteButton;
        this.provider = settings.provider;

        this.items = [];
    }

    CheckListApi.prototype = {

        init: function() {

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

            this.render(true);

        },

        render: function(refresh=false) {

            if (refresh) {
                this.items = this.provider.get();
            }

            this.list.empty();
            if (!this.items.length) {
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

        delete: function(id) {

            this.list.find('#' + id).parent().remove();

        }

    }

    $.fn.checkList = function(settings) {

        let checkList = new CheckListApi({
            list: $(this),
            saveButton: settings.saveButton,
            deleteButton: settings.deleteButton,
            provider: settings.provider
        });
        checkList.init();

        return this;

    };

}( jQuery ));