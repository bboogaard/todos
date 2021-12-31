import os
from io import BytesIO
from typing import IO, Type
from zipfile import ZipFile

from django.conf import settings
from django.db.models import Model

from todos.models import PrivateFile, PrivateImage
from services.api import FilesApi


class BaseFilesService(FilesApi):

    model: Type[Model]

    file_field: str

    def dump(self) -> IO[bytes]:
        fh = BytesIO()
        files = self.model.objects.all()
        with ZipFile(fh, 'w') as outfile:
            for file in files:
                filename = getattr(file, self.file_field).name
                outfile.write(os.path.join(settings.PRIVATE_STORAGE_ROOT, filename), filename)
        fh.seek(0)
        return fh

    def load(self, file: IO[bytes]):
        with ZipFile(file, 'r') as infile:
            names = infile.namelist()
            for name in names:
                fh = infile.read(name)
                pfile = self.model()
                getattr(pfile, self.file_field).save(name, BytesIO(fh))


class FilesService(BaseFilesService):

    model = PrivateFile

    file_field = 'file'


class ImagesService(BaseFilesService):

    model = PrivateImage

    file_field = 'image'
