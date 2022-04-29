$(document).ready(function(){
    $('[data-widget-type="snippet"]').on('init', 'textarea', function() {
        $(this).Snippet({
            saveButton: $('#saveSnippet'),
            newButton: $('#newSnippet'),
            deleteButton: $('#deleteSnippet'),
            prevButton: $('#prevSnippet'),
            nextButton: $('#nextSnippet'),
            provider: apiProviderFactory.createSnippets()
        });
    });
    widgets['snippet'].addCallback(function() {
        $('[data-widget-type="snippet"] textarea').trigger('init');
    });
    $('[data-widget-type="snippet"] textarea').trigger('init');
});