from django.urls import path
from .views import data_ingestion, chat, ingestion_status

app_name = 'post'

urlpatterns = [
    path("ingest/", data_ingestion, name='post-create'),
    path("chat/", chat, name="chat-answer"),
    path("ingestion-status", ingestion_status, name="ingestion-status" )
]