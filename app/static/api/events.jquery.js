(function( $ ) {

    const month_names = [
        'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November',
        'December'
    ]

    function EventsApi(settings) {
        this.container = settings.container;
        this.toggleMode = settings.toggleMode;
        this.exportButton = settings.exportButton;
        this.exportForm = settings.exportForm;
        this.importButton = settings.importButton;
        this.fileField = settings.fileField;
        this.provider = settings.provider;

        this.year = this.provider.year;
        this.month = this.provider.month;
        this.week = this.provider.week;
        this.mode = this.provider.mode;
        this.weeks = [];
        this.days = [];
        this.slots = [];
        this.events = [];
    }

    EventsApi.prototype = {

        init: function() {

            let self = this;

            this.initEditHandlers();

            $.when(this.provider.slots())
            .then(function(items) {
                self.slots = items.slots;
                self.loadItems(self.year, self.month, self.week);
            });

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

            this.container.on('click', '.day, .slot', function(event) {
                event.stopPropagation();
                let form = $(this).parents('[data-widget-type="events"]').find('#event-form');
                let el = this;
                $('#todos-modal').Modal({
                    title: "Create event",
                    form: form,
                    formSetUp: function(form) {
                        form.find('#id_date').val($(el).attr('data-event-date'));
                        if ($(el).hasClass('slot')) {
                            form.find('#id_time').val($(el).attr('data-event-time'));
                        }
                    },
                    formHandler: function(form) {
                        let res = form.serializeArray();
                        let data = {};
                        for (var i = 0; i < res.length; i++) {
                            data[res[i]['name']] = res[i]['value'];
                        }
                        $.when(self.provider.create(data))
                        .then(function() {
                            self.loadItems(self.year, self.month, self.week);
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
                    formHandler: function(form) {
                        let res = form.serializeArray();
                        let data = {id: $(el).attr('data-event-id')};
                        for (var i = 0; i < res.length; i++) {
                            data[res[i]['name']] = res[i]['value'];
                        }
                        $.when(self.provider.update(data))
                        .then(function() {
                            self.loadItems(self.year, self.month, self.week);
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
                    self.loadItems(self.year, self.month, self.week);
                });
            });

            this.exportButton.click(function(event) {
                event.preventDefault();
                let form = self.exportForm;
                $('#todos-modal').Modal({
                    title: "Export events",
                    form: form
                });
            });

            this.importButton.click(function(event) {
                event.preventDefault();
                self.fileField.trigger('click');
            });

            $(this.fileField).change(function() {
                let el = $(this);
                let upload = new UploadApi({
                    url: self.provider.importUrl,
                    responseHandler: function() {
                        el.val('');
                        self.loadItems(self.year, self.month, self.week);
                    }
                });
                upload.uploadFile({
                    file: el.get(0).files[0]
                });
            });

            this.toggleMode.click(function() {
                self.mode = $(this).val();
                self.loadItems(self.year, self.month, self.week);
            });

        },

        loadItems: function(year, month, week) {

            this.year = year;
            this.month = month;
            this.week = week;

            switch (this.mode) {
                case "day":
                    this.loadDayItems();
                    break;
                default:
                    this.loadWeekItems();
            }

        },

        loadWeekItems: function() {

            let self = this;

            function currentWeek(weeks) {

                let result = null;

                let now = self.roundTime(new Date());
                for (let i = 0; i < weeks.length; i++) {
                    for (let ii = 0; ii < weeks[i].dates.length; ii++) {
                        let dt = self.roundTime(new Date(weeks[i].dates[ii].date));
                        if (now.getTime() === dt.getTime()) {
                            result = weeks[i].week_number;
                            break;
                        }
                    }
                }
                return result;

            }

            let data = {
                year: this.year,
                month: this.month
            };

            $.when(this.provider.weeks(data))
            .then(function(items) {
                let weeks = items.weeks;
                self.week = currentWeek(weeks) ? currentWeek(weeks) : weeks[0].week_number;
                let dt_start = weeks[0].dates[0].date;
                let dt_end = weeks[weeks.length - 1].dates[weeks[weeks.length - 1].dates.length - 1].date;
                data = {
                    date_range: [dt_start, dt_end].join(',')
                }
                $.when(self.provider.list(data))
                .then(function(events) {
                    self.renderWeeks(weeks, events);
                })
            });

        },

        renderWeeks: function(weeks, events) {

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

            let date_class = week.color ? '' : 'text-muted';
            let week_style = week.week_style;

            let current_class = this.roundTime(new Date(date.date)).getTime() === this.roundTime(new Date()).getTime() ? 'current' : '';
            let date_style = date.date_style;
            let day = date.date.split('-')[2];
            let events = this.renderWeekEvents(date);
            let week_number = dayOfWeek === 0 ? 'week ' + week.week_number : '';

            let template = '<div class="day col-sm p-2 border border-left-0 border-top-0 text-truncate d-none ' +
            'd-sm-inline-block <%= date_class %>" style="<%= week_style %>" data-event-date="<%= event_date %>">' +
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

        renderWeekEvents: function(date) {

            let [year, month, day] = date.date.split('-');
            month = parseInt(month, 10);
            day = parseInt(day, 10);

            let template = '<a class="event d-block p-1 pl-2 pr-2 mb-1 rounded text-truncate small bg-info text-white" ' +
            'data-event-id="<%= event_id %>" data-event-time="<%= event_time %>" data-event-date="<%= event_date %>" ' +
            'data-event-description="<%= event_description %>">' +
            '<%= event_time %><br><%= event_description %><br><i class="fa fa-close" style="cursor: hand"></i></a>';

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

        loadDayItems: function() {

            let self = this;

            let data = {
                year: this.year,
                week: this.week
            };

            $.when(this.provider.days(data))
            .then(function(items) {
                let days = items.days;
                let dt_start = days[0].date;
                let dt_end = days[days.length - 1].date;
                data = {
                    date_range: [dt_start, dt_end].join(',')
                }
                $.when(self.provider.list(data))
                .then(function(events) {
                    self.renderDays(days, events);
                })
            });

        },

        renderDays: function(days, events) {

            let self = this;

            this.container.parents('div').find('#monthYear').text("Week " + this.week + " " + this.year);

            this.days = days;
            this.events = events;

            let lines = self.slots.map(function(slot, index) {
                return self.days.map(function(day) {
                    return self.renderSlot(day, slot, index);
                }).concat('<div class="w-100"></div>').join('')
            });
            let html = lines.join('');
            this.container.html(html);

        },

        combineTime: function (dt, tm) {

            dt = new Date(dt);
            let [hour, minutes, seconds] = tm.split(':');
            seconds = seconds !== undefined ? seconds : '00';
            dt.setHours(parseInt(hour, 10), parseInt(minutes, 10), parseInt(seconds, 10), 0);
            return dt;

        },

        roundTime: function(dt) {

            dt.setHours(0, 0, 0, 0);
            return dt;

        },

        renderSlot: function(day, slot, slotOfDay) {

            let current_class = this.roundTime(new Date(day.date)).getTime() === this.roundTime(new Date()).getTime() ? 'current' : '';
            let dayStr = slotOfDay === 0 ? day.date.split('-')[2] : '';
            let events = this.renderDayEvents(day, slot);

            let template = '<div class="slot col-sm p-2 border border-left-0 border-top-0 text-truncate d-none ' +
            'd-sm-inline-block text-muted" data-event-date="<%= event_date %>" data-event-time="<%= event_time %>">' +
            '<h5 class="row align-items-center">' +
            '<span class="date <%= current_class %> col-1"><%= day %></span>' +
            '<small class="col d-sm-none text-center text-muted"></small>' +
            '<span class="col-1"></span>' +
            '</h5>' +
            '<small><%= event_time %></small>' +
            '<%- events %>' +
            '</div>';

            let context = {
                event_date: day.date,
                event_time: slot.start_time,
                current_class: current_class,
                day: dayStr,
                events: events
            }

            return ejs.render(template, context);

        },

        renderDayEvents: function(day, slot) {

            let self = this;

            let startTime = this.combineTime(day.date, slot.start_time);
            let endTime = this.combineTime(day.date, slot.end_time);

            let [year, month, dayStr] = day.date.split('-');
            month = parseInt(month, 10);
            day = parseInt(dayStr, 10);

            let template = '<a class="event d-block p-1 pl-2 pr-2 mb-1 rounded text-truncate small bg-info text-white" ' +
            'data-event-id="<%= event_id %>" data-event-time="<%= event_time %>" data-event-date="<%= event_date %>" ' +
            'data-event-description="<%= event_description %>">' +
            '<%= event_time %><br><%= event_description %><br><i class="fa fa-close" style="cursor: hand"></i></a>';

            let events = this.events.filter(function(event) {
                let eventTime = self.combineTime(event.datetime.split('T')[0], event.datetime.split('T')[1].substr(0, 5));
                return event.event_date[0] === day && event.event_date[1] === month && eventTime.getTime() >= startTime.getTime() && eventTime.getTime() < endTime.getTime();
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

            switch (this.mode) {
                case 'day':
                    this.prevWeek();
                    break;
                default:
                    this.prevMonth();
            }

        },

        next: function() {

            switch (this.mode) {
                case 'day':
                    this.nextWeek();
                    break;
                default:
                    this.nextMonth();
            }

        },

        prevWeek: function() {

            let self = this;

            let data = {
                year: this.year,
                week: this.week
            }
            $.when(this.provider.prevWeek(data))
                .then(function (items) {
                    self.year = items.year;
                    self.week = items.week;
                    self.month = items.month;
                    self.loadDayItems();
                });

        },

        nextWeek: function() {

            let self = this;

            let data = {
                year: this.year,
                week: this.week
            }
            $.when(this.provider.nextWeek(data))
                .then(function (items) {
                    self.year = items.year;
                    self.week = items.week;
                    self.month = items.month;
                    self.loadDayItems();
                });

        },

        prevMonth: function() {

            this.year = this.month > 1 ? this.year : this.year - 1;
            this.month = this.month > 1 ? this.month - 1 : 12;

            this.loadWeekItems();

        },

        nextMonth: function() {

            this.year = this.month < 12 ? this.year : this.year + 1;
            this.month = this.month < 12 ? this.month + 1 : 1;

            this.loadWeekItems();

        },

    }

    $.fn.Events = function(settings) {

        let events = new EventsApi({
            container: $(this),
            toggleMode: settings.toggleMode,
            exportButton: settings.exportButton,
            exportForm: settings.exportForm,
            importButton: settings.importButton,
            fileField: settings.fileField,
            provider: settings.provider
        });
        events.init();

        return this;

    };

}( jQuery ));