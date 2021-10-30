$(document).ready(function(){
    $('[data-event-url]').click(function(event) {
        eModal.iframe($(this).data('event-url'), "Create events");
    });
})