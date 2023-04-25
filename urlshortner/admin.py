from django.contrib import admin
from models import Link
# Register your models here.

class ShortLinkAdmin(admin.ModelAdmin):
        list_display = ('id', 'url', )
        search_fields = ('id', 'url', )

admin.site.register(Link, ShortLinkAdmin)
