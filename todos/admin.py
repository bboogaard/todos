from django.contrib import admin

from todos import models


class TodoAdmin(admin.ModelAdmin):

    date_hierarchy = 'activate_date'

    list_display = ('description', 'status', 'activate_date')

    list_filter = ('status',)

    search_fields = ('description',)


admin.site.register(models.Todo, TodoAdmin)
admin.site.register(models.Gallery)
admin.site.register(models.Wallpaper)
