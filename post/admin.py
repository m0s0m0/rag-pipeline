from django.contrib import admin

from .models import IngestionLog, Chat

class IngestionLogAdmin(admin.ModelAdmin):
    list_display = ("batch_id", "url", "processing_status",)
    list_filter = ("batch_id", "processing_status",)

admin.site.register(IngestionLog, IngestionLogAdmin)
admin.site.register(Chat)
# Register your models here.
