from django import forms


class TodoSearchForm(forms.Form):

    description = forms.CharField()


class NoteSearchForm(forms.Form):

    note_id = forms.IntegerField()


class FileSearchForm(forms.Form):

    file_id = forms.IntegerField()


class ImageSearchForm(forms.Form):

    image_id = forms.IntegerField()
