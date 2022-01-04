$(document).ready(function(){
    $('[data-widget-type="dates"]').on('init', 'div', function() {
        $(this).HistoricalDates({
            dates: JSON.parse(document.getElementById('date-vars').textContent).dates
        });
    });
    widgets['dates'].addCallback(function() {
        $('[data-widget-type="dates"] div').trigger('init');
    });
    $('[data-widget-type="dates"] div').trigger('init');
});
