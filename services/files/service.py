import os
from io import BytesIO
from typing import IO
from zipfile import ZipFile

from django.conf import settings

from todos.models import PrivateFile
from services.api import FilesApi


class FilesService(FilesApi):

    def dump(self, filename: str) -> IO[bytes]:
        fh = BytesIO()
        files = PrivateFile.objects.all()
        with ZipFile(fh, 'w') as outfile:
            for file in files:
                outfile.write(os.path.join(settings.PRIVATE_STORAGE_ROOT, file.file.name), file.file.name)
        return fh

    def load(self, file: IO[bytes]):
        with ZipFile(file, 'r') as infile:
            names = infile.namelist()
            for name in names:
                fh = infile.read(name)
                pfile = PrivateFile()
                pfile.file.save(name, BytesIO(fh))
