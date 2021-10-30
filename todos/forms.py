from crispy_forms.helper import FormHelper
from crispy_forms.layout import ButtonHolder, Layout, Submit
from django import forms

from todos import models


class SettingsForm(forms.Form):

    todos_provider = forms.ChoiceField(choices=(
        ('local', 'local'),
        ('remote', 'remote'),
    ), required=False)

    todos_position = forms.ChoiceField(choices=(
        ('top', 'top'),
        ('bottom', 'bottom'),
    ), required=False)

    gallery = forms.TypedChoiceField(coerce=int, choices=(), required=False)

    show_files = forms.BooleanField(required=False)

    show_notes = forms.BooleanField(required=False)

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'events',
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
