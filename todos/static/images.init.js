$(document).ready(function(){
    $('[data-widget-type="images"]').on('click', '[data-carousel-url]', function(event) {
        event.preventDefault();
        $('#todos-modal').Modal({
          title: 'Images',
          url: $(this).data('carousel-url')
        });
    });
})