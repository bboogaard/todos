$(document).ready(function(){
    $('[data-widget-type="images"]').on('init', '.images-container', function() {
        $(this).Images({
            provider: apiProviderFactory.createImages()
        });
    });
    widgets['images'].addCallback(function() {
        $('[data-widget-type="images"] .images-container').trigger('init');
    });
    $('[data-widget-type="images"] .images-container').trigger('init');
})