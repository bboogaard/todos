$(document).ready(function(){
    $('[data-widget-type="files"]').on('click', 'small a', function(event) {
        event.preventDefault();
        $.post($(this).attr('href'))
        .done(function() {
            widgets['files'].load();
        });
    });
})