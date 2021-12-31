$(document).ready(function(){
    $('[data-widget-type="events"]').on('click', '[data-event-url]', function(event) {
        event.stopPropagation();
        let eventTitle = $(this).data('event-title');
        $(document).on('hide.bs.modal', function(event2) {
            let modal = $.trim($(event2.target).find('.modal-title').text());
            if (modal == eventTitle) {
                widgets['events'].load();
            }
        });
        eModal.iframe($(this).data('event-url'), eventTitle);
    });
    $('.event').on('click', '.fa.fa-close', function(event) {
        event.stopPropagation();
        $(this).parents('form').submit();
    });
})