$(document).ready(function(){
    $('[data-widget-type="files"]').on('init', '.files-container', function() {
        $(this).Files({
            provider: apiProviderFactory.createFiles()
        });
    });
    widgets['files'].addCallback(function() {
        $('[data-widget-type="files"] .files-container').trigger('init');
    });
    $('[data-widget-type="files"] .files-container').trigger('init');
})