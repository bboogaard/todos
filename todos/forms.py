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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['gallery'].choices = list(models.Gallery.objects.values_list('id', 'name'))
