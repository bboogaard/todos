import datetime

import pytz
from crispy_forms.helper import FormHelper
from crispy_forms.layout import ButtonHolder, Layout, Submit
from django import forms
from django.conf import settings
from haystack.forms import ModelSearchForm as HaystackSearchForm

from todos import models


class TimePicker(forms.TimeInput):

    template_name = 'forms/widgets/timepicker.html'

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


class SettingsForm(forms.Form):

    todos_provider = forms.ChoiceField(choices=(
        ('local', 'local'),
        ('remote', 'remote'),
    ), required=False)

    gallery = forms.TypedChoiceField(coerce=int, choices=(), required=False)

    notes_provider = forms.ChoiceField(choices=(
        ('local', 'local'),
        ('remote', 'remote'),
    ), required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['gallery'].choices = list(models.Gallery.objects.values_list('id', 'name'))


class SearchForm(HaystackSearchForm):

    def search(self):
        sqs = super().search()
        sqs = sqs.filter(include_in_search=True)
        return sqs


class TodoSearchForm(forms.Form):

    description = forms.CharField()


class NoteSearchForm(forms.Form):

    note_id = forms.CharField()


class FileSearchForm(forms.Form):

    file_id = forms.IntegerField()


class ImageSearchForm(forms.Form):

    image_id = forms.IntegerField()


class MonthForm(forms.Form):

    month = forms.IntegerField()

    year = forms.IntegerField()


class EventForm(forms.ModelForm):

    time = forms.TimeField(widget=TimePicker(), input_formats=['%H:%M'])

    class Meta:
        model = models.Event
        fields = ('description',)

    def __init__(self, *args, **kwargs):
        self.date = kwargs.pop('date')
        super().__init__(*args, **kwargs)
        self.initial['time'] = self.instance.datetime_localized.time() if self.instance.datetime else None
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'description',
            'time',
            ButtonHolder(
                Submit('submit', 'Save', css_class='button white')
            )
        )

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.datetime = pytz.timezone(settings.TIME_ZONE).localize(datetime.datetime.combine(
            self.date, self.cleaned_data['time']
        ))
        instance.save()
        return instance


class MonthForm(forms.Form):

    month = forms.IntegerField()

    year = forms.IntegerField()


class EventForm(forms.ModelForm):

    time = forms.TimeField(widget=TimePicker(), input_formats=['%H:%M'])

    class Meta:
        model = models.Event
        fields = ('description',)

    def __init__(self, *args, **kwargs):
        self.date = kwargs.pop('date')
        super().__init__(*args, **kwargs)
        self.initial['time'] = self.instance.datetime_localized.time() if self.instance.datetime else None
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'description',
            'time',
            ButtonHolder(
                Submit('submit', 'Save', css_class='button white')
            )
        )

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.datetime = pytz.timezone(settings.TIME_ZONE).localize(datetime.datetime.combine(
            self.date, self.cleaned_data['time']
        ))
        instance.save()
        return instance


class WallpaperForm(forms.ModelForm):

    class Meta:
        fields = '__all__'
        model = models.Wallpaper

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'gallery',
            'image',
            'position',
            ButtonHolder(
                Submit('submit', 'Submit', css_class='button white')
            )
        )


class FileForm(forms.ModelForm):

    class Meta:
        fields = ('file', 'tags')
        model = models.PrivateFile

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'file',
            'tags',
            ButtonHolder(
                Submit('submit', 'Save', css_class='button white')
            )
        )


class ImageForm(forms.ModelForm):

    class Meta:
        fields = ('image', 'tags')
        model = models.PrivateImage

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'image',
            'tags',
            ButtonHolder(
                Submit('submit', 'Save', css_class='button white')
            )
        )


class ImportForm(forms.Form):

    file = forms.FileField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'file',
            ButtonHolder(
                Submit('submit', 'Import', css_class='button white')
            )
        )
