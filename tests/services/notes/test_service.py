from Crypto.Cipher import AES
from django.core.cache import cache
from django.core.files.base import ContentFile
from django.test.testcases import TestCase

from services.factory import ItemServiceFactory
from todos.models import Note
from tests.todos.factories import NoteFactory


class TestNoteService(TestCase):

    def setUp(self):
        super().setUp()
        self.service = ItemServiceFactory.notes()

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        NoteFactory(text='Pay bills', position=0)
        NoteFactory(text='Take out trash', position=1)
        NoteFactory(text='Dentist', status=Note.INACTIVE_STATUS, position=2)

    def test_all(self):
        result = self.service.all()
        expected = ['Pay bills', 'Take out trash', 'Dentist']
        self.assertEqual(result, expected)

    def test_get_active(self):
        result = self.service.get_active()
        expected = ['Pay bills', 'Take out trash']
        self.assertEqual(result, expected)

    def test_search(self):
        result = self.service.search('Dent')
        expected = ['Dentist']
        self.assertEqual(result, expected)

    def test_save_new(self):
        self.service.save(['Pay bills', 'Take out trash', 'Call mom'], index=1)
        result = list(Note.objects.order_by('text').values_list('text', flat=True))
        expected = ['Call mom', 'Dentist', 'Pay bills', 'Take out trash']
        self.assertEqual(result, expected)

        result = self.service.get_index()
        expected = 1
        self.assertEqual(result, expected)

    def test_save_activate(self):
        NoteFactory(text='Done', status=Note.INACTIVE_STATUS)
        self.service.save(['Pay bills', 'Take out trash', 'Done'])
        note = Note.objects.get(text='Done')
        self.assertTrue(note.is_active)

    def test_save_deactivate(self):
        self.service.save(['Pay bills'])
        note = Note.objects.get(text='Take out trash')
        self.assertFalse(note.is_active)

    def test_activate(self):
        self.service.activate(['Dentist'])
        note = Note.objects.get(text='Dentist')
        self.assertTrue(note.is_active)

    def test_dump(self):
        fh = self.service.dump('todos.txt')
        result = fh.read()
        expected = b'Pay bills\n----------\nTake out trash'
        self.assertEqual(result, expected)

    def test_load(self):
        self.service.load(ContentFile(b'Doctor\n----------\nJob interview'))
        result = list(Note.objects.order_by('text').values_list('text', flat=True))
        expected = ['Dentist', 'Doctor', 'Job interview', 'Pay bills', 'Take out trash']
        self.assertEqual(result, expected)

    def test_encrypt_round_trip(self):
        cache.set('notes-index', 0)
        self.service.encrypt('foo')
        self.service.decrypt('foo')
        note = Note.objects.get(position=0)
        self.assertEqual(note.text, 'Pay bills')

    def test_encrypt_round_trip_with_error(self):
        cache.set('notes-index', 0)
        self.service.encrypt('foo')
        with self.assertRaises(ValueError):
            self.service.decrypt('bar')
