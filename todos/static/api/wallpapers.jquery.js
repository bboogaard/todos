(function( $ ) {

    function WallpapersApi(settings) {
        this.container = settings.container;
        this.createButton = settings.createButton;
        this.deleteButton = settings.deleteButton;
        this.wallpaperForm = settings.wallpaperForm;

        this.provider = settings.provider;
    }

    WallpapersApi.prototype = {

        init: function() {

            this.initEditHandlers();

            this.loadItems();

        },

        initEditHandlers: function() {

            let self = this;

            this.createButton.click(function(event) {
                event.preventDefault();
                let form = self.wallpaperForm;
                $('#todos-modal').Modal({
                    title: "Add wallpaper",
                    form: form,
                    formAction: 'add-wallpaper',
                    formHandler: function(form) {
                        let res = form.serializeArray();
                        let data = {};
                        for (var i = 0; i < res.length; i++) {
                            data[res[i]['name']] = res[i]['value'];
                        }
                        data['image'] = form.find('#id_image').get(0).files[0];
                        let upload = new UploadApi({
                            url: self.provider.urls['create'],
                            responseHandler: function() {
                                self.loadItems();
                            }
                        });
                        upload.uploadFile(data);
                    }
                });
            });

            this.container.on('click', '[data-id]', function(event) {
                event.preventDefault();
                let el = $(this);
                let form = self.wallpaperForm;
                $('#todos-modal').Modal({
                    title: "Update wallpaper",
                    form: form,
                    formAction: 'update-wallpaper',
                    formSetUp: function(form) {
                        form.find('#div_id_image').remove();
                        form.find('#div_id_image_current img').attr('src', el.attr('data-image'));
                        form.find('#div_id_image_current').show();
                        form.find('#id_gallery').val(el.attr('data-gallery'));
                        form.find('#id_position').val(el.attr('data-position'));
                    },
                    formHandler: function(form) {
                        let res = form.serializeArray();
                        let data = {id: el.attr('data-id')};
                        for (var i = 0; i < res.length; i++) {
                            data[res[i]['name']] = res[i]['value'];
                        }
                        $.when(self.provider.update(data))
                        .then(function() {
                            self.loadItems();
                        });
                    }
                });
            });

            this.deleteButton.click(function(event) {
                event.preventDefault();
                let ids = self.container.find('input[name="wallpaper"]:checked').map(function(i, el) {
                    return $(el).val();
                }).get();
                let data = {id: ids};
                $.when(self.provider.delete(data))
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

            let template = '<tr><td><input type="checkbox" name="wallpaper" value="<%= wallpaper_id %>"></td>' +
                           '<td><%= wallpaper_gallery %></td>' +
                           '<td>' +
                           '    <a href="" data-id="<%= wallpaper_id %>" data-gallery="<%= gallery_id %>" ' +
                           '    data-position="<%= position %>" data-image="<%= image %>">' +
                           '        <img src="<%= wallpaper_image %>" width="100">' +
                           '    </a>' +
                           '</td>' +
                           '</tr>';
            let context = {
                wallpaper_id: item.id,
                gallery_id: item.gallery.id,
                wallpaper_gallery: item.gallery.name,
                wallpaper_image: item.image,
                position: item.position,
                image: item.image
            }

            return ejs.render(template, context);

        }

    }

    $.fn.Wallpapers = function(settings) {

        let wallpapers = new WallpapersApi({
            container: $(this),
            createButton: settings.createButton,
            deleteButton: settings.deleteButton,
            wallpaperForm: settings.wallpaperForm,
            provider: settings.provider
        });
        wallpapers.init();

        return this;

    };

}( jQuery ));