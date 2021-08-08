from django.contrib import admin

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

    list_display = ('text_or_empty', 'status', 'position')

    readonly_fields = ('status', 'position')

    search_fields = ('text',)

    def text_or_empty(self, obj):
        return str(obj)


admin.site.register(models.Todo, TodoAdmin)
admin.site.register(models.Gallery)
admin.site.register(models.Wallpaper)
admin.site.register(models.PrivateFile)
admin.site.register(models.Note, NoteAdmin)
