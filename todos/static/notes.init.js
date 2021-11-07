$(document).ready(function(){
    $('#notes').Notes({
        saveButton: $('#saveNotes'),
        newButton: $('#newNotes'),
        deleteButton: $('#deleteNotes'),
        prevButton: $('#prevNotes'),
        nextButton: $('#nextNotes'),
        provider: notesProviderFactory.create(notes_vars.provider)
    });
});