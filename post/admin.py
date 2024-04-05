from django.contrib import admin

from .models import IngestionLog, Chat

admin.site.register(IngestionLog)
admin.site.register(Chat)
# Register your models here.
