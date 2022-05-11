from django.contrib import admin

from api.data import models as data_models


class ItemAdmin(admin.ModelAdmin):

    date_hierarchy = 'activate_date'

    list_filter = ('status',)


class TodoAdmin(ItemAdmin, admin.ModelAdmin):

    actions = ['activate', 'deactivate']

    list_display = ('description', 'status', 'activate_date')

    search_fields = ('description',)

    def activate(self, request, queryset):
        for item in queryset:
            item.activate()
    activate.short_description = "Activate items"

    def deactivate(self, request, queryset):
        for item in queryset:
            item.soft_delete()
    deactivate.short_description = "Deactivate items"


class NoteAdmin(ItemAdmin, admin.ModelAdmin):

    list_display = ('text_or_empty', 'status')

    ordering = ('-activate_date',)

    readonly_fields = ('status',)

    search_fields = ('text',)

    def text_or_empty(self, obj):
        return str(obj)


admin.site.register(data_models.Todo, TodoAdmin)
admin.site.register(data_models.Gallery)
admin.site.register(data_models.Wallpaper)
admin.site.register(data_models.PrivateFile)
admin.site.register(data_models.PrivateImage)
admin.site.register(data_models.Note, NoteAdmin)
admin.site.register(data_models.Widget)
admin.site.register(data_models.Event)
admin.site.register(data_models.CodeSnippet)
