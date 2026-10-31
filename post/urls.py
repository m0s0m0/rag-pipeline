from django.urls import path
from .views import data_ingestion, chat, ingestion_status, agentic_chat

app_name = 'post'

urlpatterns = [
    path("ingest/", data_ingestion, name='post-create'),
    path("chat/", chat, name="chat-answer"),
    path("agentic-chat/", agentic_chat, name="agentic-chat-answer"),
    path("ingestion-status", ingestion_status, name="ingestion-status" )
]