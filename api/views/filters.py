from django_filters.filters import Filter
from django_filters.filterset import FilterSet

from api.data.models import Event
from lib.datetime import day_end, day_start, to_date


class EventDateRangeFilter(Filter):

    def filter(self, qs, value):
        try:
            value = list(filter(None, map(to_date, value.split(','))))
            return qs.filter(datetime__range=(day_start(value[0]), day_end(value[1])))
        except (AttributeError, IndexError):
            return qs


class EventFilterSet(FilterSet):

    date_range = EventDateRangeFilter(field_name='datetime')

    class Meta:
        model = Event
        fields = ['date_range']
