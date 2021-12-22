$(document).ready(function(){
    $('ul#todos').checkList({
        saveButton: $('#save'),
        deleteButton: $('#delete'),
        activateButton: $('#activate'),
        provider: checkListProviderFactory.create(todos_vars.provider)
    });
});
