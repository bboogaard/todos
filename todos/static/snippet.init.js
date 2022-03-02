$(document).ready(function(){
    $('[data-widget-type="snippet"]').on('init', '.snippet-container', function() {
        $(this).Snippet({
            updateUrl: '/snippet/update'
        });
    });
    widgets['snippet'].addCallback(function() {
        $('[data-widget-type="snippet"] .snippet-container').trigger('init');
    });
    $('[data-widget-type="snippet"] .snippet-container').trigger('init');
});