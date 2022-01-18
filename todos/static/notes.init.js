$(document).ready(function(){
    $('[data-widget-type="notes"]').on('init', 'textarea', function() {
        $(this).Notes({
            saveButton: $('#saveNotes'),
            newButton: $('#newNotes'),
            deleteButton: $('#deleteNotes'),
            prevButton: $('#prevNotes'),
            nextButton: $('#nextNotes'),
            provider: notesProviderFactory.create(notes_vars.provider),
            enableMarkdown: $('#enableMarkdown'),
        });
    });
    widgets['notes'].addCallback(function() {
        $('[data-widget-type="notes"] textarea').trigger('init');
    });
    $('[data-widget-type="notes"] textarea').trigger('init');
});