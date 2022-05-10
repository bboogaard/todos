(function( $ ) {

    function WidgetsApi(settings) {
        this.container = settings.container;
        this.saveButton = settings.saveButton;
        this.checkAllButton = settings.checkAllButton;
        this.provider = settings.provider;
    }

    WidgetsApi.prototype = {

        init: function() {

            this.initEditHandlers();

            this.loadItems();

        },

        initEditHandlers: function() {

            let self = this;

            this.checkAllButton.click(function(event) {
                self.container.find('input[name="is_enabled"]').prop('checked', $(this).prop('checked'));
            });

            this.saveButton.click(function(event) {
                event.preventDefault();
                if (!$(this).parents('form').get(0).reportValidity()) {
                    return;
                }
                let data = self.container.find('tr').map(function(i, el) {
                    let refreshInterval = $(el).find('input[name="refresh_interval"]');
                    return {
                        id: $(el).find('input[name="is_enabled"]').val(),
                        is_enabled: $(el).find('input[name="is_enabled"]').prop('checked'),
                        position: $(el).find('input[name="position"]').val(),
                        refresh_interval: refreshInterval.val() !== '' ? refreshInterval.val() : null,
                    }
                }).get();
                $.when(self.provider.update(data))
                .then(function() {
                    self.loadItems();
                });
            });

        },

        loadItems: function () {

            let self = this;

            this.provider.list()
                .done(function(items) {
                    self.render(items);
                });

        },

        render: function(items) {

            let self = this;

            this.container.empty();

            let html = items.map(function (item) {
                return self.renderItem(item);
            }).join("");
            this.container.html(html);

        },

        renderItem: function(item) {

            let template = '<tr><td><input type="checkbox" name="is_enabled" value="<%= widget_id %>"<%= checked %>>' +
                           '&nbsp;&nbsp;<span class="modal-label"><%= widget_name %></span></td>' +
                           '<td><input type="number" class="form-control" name="refresh_interval" value="<%= refresh_interval %>"></td>' +
                           '<td><input type="number" class="form-control" name="position" value="<%= position %>" required=""></td>' +
                           '</tr>';
            let context = {
                widget_id: item.id,
                widget_name: item.title,
                position: item.position,
                refresh_interval: item.refresh_interval,
                checked: item.is_enabled ? ' checked' : ''
            }

            return ejs.render(template, context);

        }

    }

    $.fn.Widgets = function(settings) {

        let widgets = new WidgetsApi({
            container: $(this),
            saveButton: settings.saveButton,
            checkAllButton: settings.checkAllButton,
            provider: settings.provider
        });
        widgets.init();

        return this;

    };

}( jQuery ));