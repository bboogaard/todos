from django import forms

from todos import models


class SettingsForm(forms.Form):

    todos_provider = forms.ChoiceField(choices=(
        ('local', 'local'),
        ('remote', 'remote'),
    ), required=False)

    gallery = forms.TypedChoiceField(coerce=int, choices=(
        (id, name)
        for id, name in models.Gallery.objects.values_list('id', 'name')
    ), required=False)
