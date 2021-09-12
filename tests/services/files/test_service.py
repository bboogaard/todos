import os
import shutil
import uuid
from io import BytesIO
from zipfile import ZipFile

from django.conf import settings
from django.core.files.base import ContentFile
from django.test.testcases import TestCase

from todos.models import PrivateFile
from services.factory import FilesServiceFactory
from tests.todos.factories import PrivateFileFactory


class TestFilesService(TestCase):

    def setUp(self):
        super().setUp()
        self.service = FilesServiceFactory.create()
        self.tmp_dir = os.path.join(settings.MEDIA_ROOT, 'tmp')
        os.makedirs(self.tmp_dir, exist_ok=True)

    def tearDown(self):
        super().tearDown()
        shutil.rmtree(self.tmp_dir)

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.filenames = list(map(lambda id: str(id) + '.txt', [uuid.uuid4(), uuid.uuid4()]))
        PrivateFileFactory(file=ContentFile(b'Foo', name=cls.filenames[0]))
        PrivateFileFactory(file=ContentFile(b'Bar', name=cls.filenames[1]))

    def test_dump(self):
        fh = self.service.dump('files.zip')
        with ZipFile(fh, 'r') as infile:
            infile.extractall(self.tmp_dir)
        self.assertTrue(os.path.exists(os.path.join(self.tmp_dir, self.filenames[0])))
        self.assertTrue(os.path.exists(os.path.join(self.tmp_dir, self.filenames[1])))
        with open(os.path.join(self.tmp_dir, self.filenames[0]), 'r') as fh:
            content = fh.read()
            self.assertEqual(content, 'Foo')
        with open(os.path.join(self.tmp_dir, self.filenames[1]), 'r') as fh:
            content = fh.read()
            self.assertEqual(content, 'Bar')

    def test_load(self):
        filenames = list(map(lambda id: str(id) + '.txt', [uuid.uuid4(), uuid.uuid4()]))
        with open(os.path.join(self.tmp_dir, filenames[0]), 'w') as fh:
            fh.write('Foo')
        with open(os.path.join(self.tmp_dir, filenames[1]), 'w') as fh:
            fh.write('Bar')

        fh = BytesIO()
        with ZipFile(fh, 'w') as outfile:
            outfile.write(os.path.join(self.tmp_dir, filenames[0]), filenames[0])
            outfile.write(os.path.join(self.tmp_dir, filenames[1]), filenames[1])
        self.service.load(fh)

        pfile = PrivateFile.objects.get(file=filenames[0])
        self.assertEqual(pfile.file.read(), b'Foo')

        pfile = PrivateFile.objects.get(file=filenames[1])
        self.assertEqual(pfile.file.read(), b'Bar')
