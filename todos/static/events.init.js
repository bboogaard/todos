$(document).ready(function(){
    $('[data-widget-type="events"]').on('click', '[data-event-url]', function(event) {
        event.stopPropagation();
        $('#todos-modal').Modal({
            title: $(this).data('event-title'),
            url: $(this).data('event-url'),
            onClose: function() {
                widgets['events'].load();
            }
        });
    });
    $('.event').on('click', '.fa.fa-close', function(event) {
        event.stopPropagation();
        $(this).parents('form').submit();
    });
})