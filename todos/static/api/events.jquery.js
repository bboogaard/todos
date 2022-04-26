(function( $ ) {

    const month_names = [
        'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November',
        'December'
    ]

    function EventsApi(settings) {
        this.container = settings.container;
        this.provider = settings.provider;

        this.year = this.provider.year;
        this.month = this.provider.month;
        this.weeks = [];
        this.events = [];
    }

    EventsApi.prototype = {

        init: function() {

            this.initEditHandlers();

            this.loadItems(this.year, this.month);

        },

        initEditHandlers: function() {

            let self = this;

            this.container.parent().on('click', '#prevButton', function(event) {
                event.preventDefault();
                self.prev();
            });

            this.container.parent().on('click', '#nextButton', function(event) {
                event.preventDefault();
                self.next();
            });

            this.container.on('click', '.day', function(event) {
                event.stopPropagation();
                let form = $(this).parents('[data-widget-type="events"]').find('#event-form');
                let el = this;
                $('#todos-modal').Modal({
                    title: "Create event",
                    form: form,
                    formSetUp: function(form) {
                        form.find('#id_date').val($(el).attr('data-event-date'));
                    },
                    formHandler: function(res) {
                        let data = {};
                        for (var i = 0; i < res.length; i++) {
                            data[res[i]['name']] = res[i]['value'];
                        }
                        $.when(self.provider.create(data))
                        .then(function() {
                            self.loadItems(self.year, self.month);
                        });
                    }
                });
            });

            this.container.on('click', '[data-event-id]', function(event) {
                event.stopPropagation();
                let form = $(this).parents('[data-widget-type="events"]').find('#event-form');
                let el = this;
                $('#todos-modal').Modal({
                    title: "Update event",
                    form: form,
                    formSetUp: function(form) {
                        form.find('#id_description').val($(el).attr('data-event-description'));
                        form.find('#id_date').val($(el).attr('data-event-date'));
                        form.find('#id_time').val($(el).attr('data-event-time'));
                    },
                    formHandler: function(res) {
                        let data = {id: $(el).attr('data-event-id')};
                        for (var i = 0; i < res.length; i++) {
                            data[res[i]['name']] = res[i]['value'];
                        }
                        $.when(self.provider.update(data))
                        .then(function() {
                            self.loadItems(self.year, self.month);
                        });
                    }
                });
            });

            this.container.on('click', '.fa.fa-close', function(event) {
                event.stopPropagation();
                let id = $(this).parents('[data-event-id]').attr('data-event-id');
                let data = {id: id};

                $.when(self.provider.delete(data))
                .then(function() {
                    self.loadItems(self.year, self.month);
                });
            });

        },

        loadItems: function(year, month) {

            let self = this;

            this.year = year;
            this.month = month;

            let data = {
                year: this.year,
                month: this.month
            };

            $.when(this.provider.weeks(data))
            .then(function(items) {
                let weeks = items.weeks;
                let dt_start = weeks[0].dates[0].date;
                let dt_end = weeks[weeks.length - 1].dates[weeks[weeks.length - 1].dates.length - 1].date;
                data = {
                    date_range: [dt_start, dt_end].join(',')
                }
                $.when(self.provider.list(data))
                .then(function(events) {
                    self.render(weeks, events);
                })
            });

        },

        render: function(weeks, events) {

            let self = this;

            this.container.parents('div').find('#monthYear').text(month_names[this.month - 1] + " " + this.year);

            this.weeks = weeks;
            this.events = events;

            let lines = this.weeks.map(function(week) {
                return week.dates.map(function(date, index) {
                    return self.renderDate(week, date, index);
                }).concat('<div class="w-100"></div>').join('')
            });
            let html = lines.join('');
            this.container.html(html);

        },

        renderDate: function(week, date, dayOfWeek) {

            function roundDate(dt) {
                dt.setHours(0, 0, 0, 0);
                return dt;
            }

            let date_class = week.color ? '' : 'text-muted';
            let week_style = week.week_style;

            let current_class = roundDate(new Date(date.date)).getTime() === roundDate(new Date()).getTime() ? 'current' : '';
            let date_style = date.date_style;
            let day = date.date.split('-')[2];
            let events = this.renderEvents(date);
            let week_number = dayOfWeek === 0 ? 'week ' + week.week_number : '';

            let template = '<div class="day col-sm p-2 border border-left-0 border-top-0 text-truncate d-none ' +
            'd-sm-inline-block <%= date_class %> style="<%= week_style %>" data-event-date="<%= event_date %>">' +
            '<h5 class="row align-items-center">' +
            '<span class="date <%= current_class %> col-1" style="<%= date_style %>"><%= day %></span>' +
            '<small class="col d-sm-none text-center text-muted"></small>' +
            '<span class="col-1"></span>' +
            '</h5>' +
            '<%- events %>' +
            '<small><%= week_number %></small></div>';

            let context = {
                date_class: date_class,
                week_style: week_style,
                event_date: date.date,
                current_class: current_class,
                date_style: date_style,
                day: day,
                events: events,
                week_number: week_number
            }

            return ejs.render(template, context);

        },

        renderEvents: function(date) {

            let [year, month, day] = date.date.split('-');
            month = parseInt(month, 10);
            day = parseInt(day, 10);

            let template = '<a class="event d-block p-1 pl-2 pr-2 mb-1 rounded text-truncate small bg-info text-white" ' +
            'data-event-id="<%= event_id %>" data-event-time="<%= event_time %>" data-event-date="<%= event_date %>" ' +
            'data-event-description="<%= event_description %>">' +
            '<%= event_time %><br><%= event_description %><i class="fa fa-close" style="cursor: hand"></i></a>';

            let events = this.events.filter(function(event) {
                return event.event_date[0] === day && event.event_date[1] === month;
            }).map(function(event) {
                let context = {
                    event_id: event.id,
                    event_date: event.datetime.split('T')[0],
                    event_time: event.datetime.split('T')[1].substr(0, 5),
                    event_description: event.description
                }
                return ejs.render(template, context);
            });

            return events.join('');

        },

        prev: function() {

            let year = this.month > 1 ? this.year : this.year - 1;
            let month = this.month > 1 ? this.month - 1 : 12;

            this.loadItems(year, month);

        },

        next: function() {

            let year = this.month < 12 ? this.year : this.year + 1;
            let month = this.month < 12 ? this.month + 1 : 1;

            this.loadItems(year, month);

        }

    }

    $.fn.Events = function(settings) {

        let events = new EventsApi({
            container: $(this),
            provider: settings.provider
        });
        events.init();

        return this;

    };

}( jQuery ));