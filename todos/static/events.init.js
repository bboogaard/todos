$(document).ready(function(){
    $('[data-event-url]').click(function(event) {
        event.stopPropagation();
        eModal.iframe($(this).data('event-url'), $(this).data('event-title'));
    });
    $('.event .fa.fa-close').click(function(event) {
        event.stopPropagation();
        $(this).parents('form').submit();
    });
})