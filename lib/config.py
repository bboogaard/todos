from django import forms

from api.data.models import Gallery


class GalleryChoiceField(forms.ChoiceField):

    def __init__(self, *args, **kwargs):
        kwargs['choices'] = [
            (gallery.pk, str(gallery))
            for gallery in Gallery.objects.all()
        ]
        super().__init__(*args, **kwargs)
