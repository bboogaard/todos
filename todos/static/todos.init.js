$(document).ready(function(){
    $('[data-widget-type="todos"]').on('init', 'ul', function() {
        $(this).Todos({
            saveButton: $('#save'),
            deleteButton: $('#delete'),
            activateButton: $('#activate'),
            provider: apiProviderFactory.createTodos()
        });
    });
    widgets['todos'].addCallback(function() {
        $('[data-widget-type="todos"] ul').trigger('init');
    });
    $('[data-widget-type="todos"] ul').trigger('init');
});
