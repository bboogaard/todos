from django.contrib import admin

from api.data import models as data_models
from todos import models


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


class HistoricalDateAdmin(admin.ModelAdmin):

    list_display = ('date', 'event')


admin.site.register(data_models.Todo, TodoAdmin)
admin.site.register(models.Gallery)
admin.site.register(models.Wallpaper)
admin.site.register(models.PrivateFile)
admin.site.register(models.PrivateImage)
admin.site.register(data_models.Note, NoteAdmin)
admin.site.register(models.Widget)
admin.site.register(models.Event)
admin.site.register(models.HistoricalDate, HistoricalDateAdmin)
admin.site.register(data_models.CodeSnippet)
