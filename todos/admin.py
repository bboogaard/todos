from django.contrib import admin

from todos import models


class TodoAdmin(admin.ModelAdmin):

    actions = ['activate', 'deactivate']

    date_hierarchy = 'activate_date'

    list_display = ('description', 'status', 'activate_date')

    list_filter = ('status',)

    search_fields = ('description',)

    def activate(self, request, queryset):
        for todo in queryset:
            todo.activate()
    activate.short_description = "Activate todo's"

    def deactivate(self, request, queryset):
        for todo in queryset:
            todo.soft_delete()
    deactivate.short_description = "Deactivate todo's"


admin.site.register(models.Todo, TodoAdmin)
admin.site.register(models.Gallery)
admin.site.register(models.Wallpaper)
