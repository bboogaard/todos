$(document).ready(function(){
    $('[data-widget-type="events"]').on('click', '[data-event-url]', function(event) {
        event.stopPropagation();
        $('#todos-modal').FullModal({
            title: $(this).data('event-title'),
            url: $(this).data('event-url'),
            onClose: function() {
                widgets['events'].load();
            }
        });
    });
    /*$('[data-widget-type="events"]').on('click', '[data-event-type="hist_date"]', function(event) {
        event.stopPropagation();
        $('#todos-modal').Modal({
            title: $(this).data('event-title'),
            content: $(this).data('event-content')
        });
    });*/
    $('[data-widget-type="events"]').on('click', '.event .fa.fa-close', function(event) {
        event.stopPropagation();
        $(this).parents('form').submit();
    });
})