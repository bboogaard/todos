(function( $ ) {

    function FilesApi(settings) {
        this.container = settings.container;
        this.provider = settings.provider;
        this.exportButton = settings.exportButton;
        this.exportForm = settings.exportForm;
        this.importButton = settings.importButton;
        this.fileField = settings.fileField;

        this.items = {};
        this.searchQuery = settings.provider.searchQuery;
        this.searching = this.searchQuery !== null;
    }

    FilesApi.prototype = {

        init: function() {

            this.initEditHandlers();

            this.loadItems();

        },

        initEditHandlers: function() {

            let self = this;

            this.container.on('click', 'a[data-id]', function(event) {
                event.preventDefault();
                self.delete($(this).attr('data-id'));
            });

            this.exportButton.click(function(event) {
                event.preventDefault();
                let form = self.exportForm;
                $('#todos-modal').Modal({
                    title: "Export files",
                    form: form,
                    formAction: 'export-files'
                });
            });

            this.importButton.click(function(event) {
                event.preventDefault();
                self.fileField.trigger('click');
            });

            $(this.fileField).change(function() {
                let el = $(this);
                let upload = new UploadApi({
                    url: self.provider.importUrl,
                    responseHandler: function() {
                        el.val('');
                        self.loadItems();
                    }
                });
                upload.uploadFile({
                    file: el.get(0).files[0]
                });
            });

        },

        loadItems: function() {

            let self = this;

            let data = {};
            if (this.searchQuery !== null) {
                data.id = this.searchQuery;
            }

            this.provider.list(data).done(function(items) {
                self.render(items);
            }).fail(function() {
                self.render([]);
            });

        },

        render: function(items) {

            this.items = items;
            let lines = this.items.map(function(item) {
                return '<a href="' + item.url + '" target="_blank">' + item.name + '</a>&nbsp;' +
                '<small><a href="" data-id="' + item.id + '">delete</a></small><br>';
            });
            let html = lines.length ? lines.join('') : 'No files uploaded yet';
            this.container.html(html);

        },

        delete: function(id) {

            let self = this;

            let data = {id: id};

            $.when(this.provider.delete(data))
            .then(function() {
                self.loadItems()
            });
        }

    }

    $.fn.Files = function(settings) {

        let files = new FilesApi({
            container: $(this),
            exportButton: settings.exportButton,
            exportForm: settings.exportForm,
            importButton: settings.importButton,
            fileField: settings.fileField,
            provider: settings.provider
        });
        files.init();

        return this;

    };

}( jQuery ));