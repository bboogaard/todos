from io import BytesIO

from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.http.response import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views import generic, View
from private_storage.storage import private_storage

from services.api import Api
from services.factory import FilesServiceFactory, ItemServiceFactory
from todos import forms, models
from todos.settings import cache_settings


class AccessMixin(View):

    redirect_to_login = True

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            if self.redirect_to_login:
                return redirect(reverse('admin:login') + '?next=/')
            raise PermissionDenied()

        return super().dispatch(request, *args, **kwargs)


class IndexView(AccessMixin, generic.TemplateView):

    template_name = 'index.html'

    def get(self, request, *args, **kwargs):
        form = self.get_form(request.GET or None)
        if form.is_valid():
            items = ItemServiceFactory.todos().search(form.cleaned_data['q'])
            searching = True
        else:
            items = ItemServiceFactory.todos().get_active()
            searching = False
        context = self.get_context_data(
            form=form,
            searching=searching,
            todo_vars={
                'items': items,
                'saveUrl': reverse('todos:todos_save.json'),
                'activateUrl': reverse('todos:todos_activate.json')
            },
            note_vars={
                'items': ItemServiceFactory.notes().get_active(),
                'index': ItemServiceFactory.notes().get_index(),
                'saveUrl': reverse('todos:notes_save.json')
            },
        )
        return self.render_to_response(context)

    def get_form(self, data=None):
        return forms.SearchForm(data)


class TodosSaveJson(AccessMixin, View):

    @transaction.atomic()
    def post(self, request, *args, **kwargs):
        items = request.POST.getlist('items', [])
        ItemServiceFactory.todos().save(items)
        return JsonResponse(data={})


class TodosActivateJson(AccessMixin, View):

    @transaction.atomic()
    def post(self, request, *args, **kwargs):
        items = request.POST.getlist('items', [])
        ItemServiceFactory.todos().activate(items)
        return JsonResponse(data={})


class TodosExportView(AccessMixin, View):

    def get(self, request, *args, **kwargs):
        fh = ItemServiceFactory.todos().dump('todos.txt')
        response = HttpResponse(fh.read(), content_type='text/plain')
        response['Content-disposition'] = 'attachment'
        return response


class NotesSaveJson(AccessMixin, View):

    @transaction.atomic()
    def post(self, request, *args, **kwargs):
        items = request.POST.getlist('items', [])
        try:
            index = int(request.POST.get('index', '0'))
        except (TypeError, ValueError):
            index = 0
        ItemServiceFactory.notes().save(items, index=index)
        return JsonResponse(data={})


class NotesExportView(AccessMixin, View):

    def get(self, request, *args, **kwargs):
        fh = ItemServiceFactory.notes().dump('notes.txt')
        response = HttpResponse(fh.read(), content_type='text/plain')
        response['Content-disposition'] = 'attachment'
        return response


class SettingsSave(AccessMixin, View):

    @transaction.atomic()
    def post(self, request, *args, **kwargs):
        form = forms.SettingsForm(request.POST or None)
        if form.is_valid():
            cache_settings.save(**form.cleaned_data)

        return redirect(reverse('todos:index'))


class WallpaperListView(AccessMixin, generic.TemplateView):

    template_name = 'wallpapers/wallpaper_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'wallpapers': models.Wallpaper.objects.order_by('gallery', 'position')
        })
        return context


class WallpaperEditMixin(generic.TemplateView):

    def get(self, request, *args, **kwargs):
        form = self.get_form()
        context = self.get_context_data(form=form)
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        form = self.get_form(request.POST or None, files=request.FILES or None)
        if form.is_valid():
            form.save()
            return redirect(reverse('todos:wallpaper_list'))

        context = self.get_context_data(form=form)
        return self.render_to_response(context)

    def get_form(self, data=None, files=None, **kwargs):
        return forms.WallpaperForm(data, files=files, **kwargs)


class WallpaperCreateView(AccessMixin, WallpaperEditMixin):

    template_name = 'wallpapers/wallpaper_create.html'


class WallpaperUpdateView(AccessMixin, WallpaperEditMixin):

    template_name = 'wallpapers/wallpaper_update.html'

    def dispatch(self, request, pk, *args, **kwargs):
        self.object = get_object_or_404(models.Wallpaper, pk=pk)
        return super().dispatch(request, *args, **kwargs)

    def get_form(self, data=None, files=None, **kwargs):
        kwargs['instance'] = self.object
        return super().get_form(data, files, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['wallpaper'] = self.object
        return context


class WallpaperDeleteView(AccessMixin, View):

    def post(self, request, *args, **kwargs):
        wallpaper_ids = request.POST.getlist('wallpaper', [])
        models.Wallpaper.objects.filter(pk__in=wallpaper_ids).delete()
        return redirect(reverse('todos:wallpaper_list'))


class FileListView(AccessMixin, generic.TemplateView):

    template_name = 'files/file_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'files': models.PrivateFile.objects.all()
        })
        return context


class FileCreateView(AccessMixin, generic.TemplateView):

    template_name = 'files/file_create.html'

    def get(self, request, *args, **kwargs):
        form = self.get_form()
        context = self.get_context_data(form=form)
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        form = self.get_form(request.POST or None, files=request.FILES or None)
        if form.is_valid():
            form.save()
            return redirect(reverse('todos:file_list'))

        context = self.get_context_data(form=form)
        return self.render_to_response(context)

    def get_form(self, data=None, files=None, **kwargs):
        return forms.FileForm(data, files=files, **kwargs)


class FileDeleteView(AccessMixin, View):

    def post(self, request, *args, **kwargs):
        file_ids = request.POST.getlist('file', [])
        qs = models.PrivateFile.objects.filter(pk__in=file_ids)
        file_names = [file.file.name for file in qs]
        qs.delete()
        for file in file_names:
            private_storage.delete(file)
        return redirect(reverse('todos:file_list'))


class FileExportView(AccessMixin, View):

    def get(self, request, *args, **kwargs):
        fh = FilesServiceFactory.create().dump('files.zip')
        response = HttpResponse(fh.read(), content_type='application/zip')
        response['Content-disposition'] = 'attachment'
        return response


class ImportView(AccessMixin, generic.TemplateView):

    message: str

    title: str

    template_name = 'import.html'

    def get(self, request, *args, **kwargs):
        form = self.get_form()
        context = self.get_context_data(form=form)
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        form = self.get_form(request.POST or None, files=request.FILES or None)
        if form.is_valid():
            self.get_service().load(BytesIO(form.files['file'].read()))
            messages.add_message(request, messages.SUCCESS, self.message)
            return redirect(request.path)

        context = self.get_context_data(form=form)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.title
        return context

    def get_form(self, data=None, files=None, **kwargs):
        return forms.ImportForm(data, files=files, **kwargs)

    def get_service(self):
        raise NotImplementedError()


class TodosImportView(ImportView):

    message = "Todo's imported"

    title = "Import todo's"

    def get_service(self):
        return ItemServiceFactory.todos()


class NotesImportView(ImportView):

    message = "Notes imported"

    title = "Import notes"

    def get_service(self):
        return ItemServiceFactory.notes()


class FileImportView(ImportView):

    message = "Files imported"

    title = "Import files"

    def get_service(self):
        return FilesServiceFactory.create()


class NoteEncryptionView(AccessMixin, generic.TemplateView):

    title: str

    button_text: str

    template_name = 'notes/encrypt.html'

    form_class = None

    def get(self, request, *args, **kwargs):
        form = self.get_form()
        context = self.get_context_data(form=form)
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        form = self.get_form(request.POST or None)
        if form.is_valid():
            self.perform_action(form.cleaned_data['key'])
            return redirect(request.path)

        context = self.get_context_data(form=form)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.title
        return context

    def get_form(self, data=None, **kwargs):
        return forms.NoteEncryptForm(data, button_text=self.button_text, **kwargs)

    def perform_action(self, key: str):
        raise NotImplementedError()

    def get_service(self):
        return ItemServiceFactory.notes()


class NoteEncryptView(NoteEncryptionView):

    title = 'Encrypt note'

    button_text = 'Encrypt'

    def perform_action(self, key: str):
        try:
            self.get_service().encrypt(key)
            messages.add_message(self.request, messages.SUCCESS, 'Note encrypted')
        except ValueError as exc:
            messages.add_message(self.request, messages.ERROR, str(exc))


class NoteDecryptView(NoteEncryptionView):

    title = 'Decrypt note'

    button_text = 'Decrypt'

    def perform_action(self, key: str):
        try:
            self.get_service().decrypt(key)
            messages.add_message(self.request, messages.SUCCESS, 'Note decrypted')
        except ValueError as exc:
            messages.add_message(self.request, messages.ERROR, str(exc))
