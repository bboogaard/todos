from django import forms
from haystack.forms import ModelSearchForm as HaystackSearchForm

from todos import models


class DateTimePicker(forms.DateTimeInput):

    class Media:
        css = {
            'all': (
                'tempus-dominus/css/font-awesome.css',
                'tempus-dominus/css/tempus-dominus.min.css',
            )
        }
        js = (
            'tempus-dominus/js/moment.min.js',
            'tempus-dominus/js/tempus-dominus.min.js',
        )

    def __init__(self, attrs=None, format=None):
        attrs = attrs or {}
        attrs.update({
            'data-toggle': 'datetimepicker',
            'class': 'datetimepicker-input'
        })
        super().__init__(attrs, format)

    def get_context(self, name, value, attrs):
        id = 'id_{}'.format(name)
        attrs.update({
            'id': id,
            'data-target': '#{}'.format(id),
        })
        return super().get_context(name, value, attrs)


class TimePicker(DateTimePicker):

    template_name = 'forms/widgets/timepicker.html'


class DatePicker(DateTimePicker):

    template_name = 'forms/widgets/datepicker.html'


class SearchForm(HaystackSearchForm):

    def search(self):
        sqs = super().search()
        sqs = sqs.filter(include_in_search=True)
        return sqs


class TodoSearchForm(forms.Form):

    description = forms.CharField()


class NoteSearchForm(forms.Form):

    note_id = forms.IntegerField()


class FileSearchForm(forms.Form):

    file_id = forms.IntegerField()


class ImageSearchForm(forms.Form):

    image_id = forms.IntegerField()


class WidgetForm(forms.ModelForm):

    class Meta:
        fields = ('is_enabled', 'refresh_interval', 'position')
        model = models.Widget


WidgetFormSet = forms.modelformset_factory(models.Widget, WidgetForm, extra=0)
