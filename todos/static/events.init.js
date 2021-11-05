$(document).ready(function(){
    $('[data-event-url]').click(function(event) {
        event.stopPropagation();
        eModal.iframe($(this).data('event-url'), $(this).data('event-title'));
    });
})