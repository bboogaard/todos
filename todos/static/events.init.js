$(document).ready(function(){
    $('[data-widget-type="events"]').on('init', '.container-fluid .row.border', function() {
        $(this).Events({
            provider: apiProviderFactory.createEvents()
        });
    });
    widgets['events'].addCallback(function() {
        $('[data-widget-type="events"] .container-fluid .row.border').trigger('init');
    });
    $('[data-widget-type="events"] .container-fluid .row.border').trigger('init');
})