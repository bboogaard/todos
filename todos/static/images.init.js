$(document).ready(function(){
    $('[data-carousel-url]').click(function(event) {
        event.preventDefault();
        eModal.iframe($(this).data('carousel-url'), 'Images');
    });
})