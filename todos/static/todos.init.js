$(document).ready(function(){
    $('[data-widget-type="todos"]').on('init', 'ul', function() {
        $(this).Todos({
            saveButton: $('#save'),
            deleteButton: $('#delete'),
            activateButton: $('#activate'),
            exportButton: $('#exportTodos'),
            exportForm: $('#todo-export-form'),
            importButton: $('#importTodos'),
            fileField: $('#importTodosInput'),
            provider: apiProviderFactory.createTodos()
        });
    });
    widgets['todos'].addCallback(function() {
        $('[data-widget-type="todos"] ul').trigger('init');
    });
    $('[data-widget-type="todos"] ul').trigger('init');
});
