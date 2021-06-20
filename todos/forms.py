from django import forms


class SettingsForm(forms.Form):

    todos_provider = forms.ChoiceField(choices=(
        ('local', 'local'),
        ('remote', 'remote'),
    ), required=False)
