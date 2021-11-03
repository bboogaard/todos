from crispy_forms.helper import FormHelper
from crispy_forms.layout import ButtonHolder, Layout, Submit
from django import forms

from todos import models


class TimePicker(forms.TimeInput):

    template_name = 'forms/widgets/timepicker.html'

    class Media:
        css = {
            'all': ('tempus-dominus/tempus-dominus.min.css',)
        }
        js = (
            'tempus-dominus/moment.min.js',
            'tempus-dominus/tempus-dominus.min.js',
        )


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


class SearchForm(forms.Form):

    q = forms.CharField(required=False)


class MonthForm(forms.Form):

    month = forms.IntegerField()

    year = forms.IntegerField()


class EventForm(forms.Form):

    events = forms.CharField(widget=forms.Textarea())

    time = forms.TimeField(widget=TimePicker(
        attrs={'data-toggle': "datetimepicker", "id": "time", "data-target": "#time", "style": "position: relative"}
    ))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'events',
            'time',
            ButtonHolder(
                Submit('submit', 'Save', css_class='button white')
            )
        )


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
        fields = ('file',)
        model = models.PrivateFile

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'file',
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
