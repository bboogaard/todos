$(document).ready(function(){
    $('ul#todos').checkList({
        saveButton: $('#save'),
        deleteButton: $('#delete'),
        activateButton: $('#activate'),
        searching: todos_vars.searching,
        provider: checkListProviderFactory.create(todos_vars.provider)
    });
});
