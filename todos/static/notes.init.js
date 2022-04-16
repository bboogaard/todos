$(document).ready(function(){
    $('[data-widget-type="notes"]').on('init', 'textarea', function() {
        $(this).Notes({
            saveButton: $('#saveNotes'),
            newButton: $('#newNotes'),
            deleteButton: $('#deleteNotes'),
            prevButton: $('#prevNotes'),
            nextButton: $('#nextNotes'),
            provider: apiProviderFactory.create_notes()
        });
    });
    widgets['notes'].addCallback(function() {
        $('[data-widget-type="notes"] textarea').trigger('init');
    });
    $('[data-widget-type="notes"] textarea').trigger('init');
});