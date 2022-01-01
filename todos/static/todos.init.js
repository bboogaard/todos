$(document).ready(function(){
    $('[data-widget-type="todos"]').on('init', 'ul', function() {
        $(this).checkList({
            saveButton: $('#save'),
            deleteButton: $('#delete'),
            activateButton: $('#activate'),
            provider: checkListProviderFactory.create(todos_vars.provider)
        });
    });
    $('[data-widget-type="todos"] ul').trigger('init');
});
