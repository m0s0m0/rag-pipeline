from django.db import models
import uuid

from post.constants import FileFormats, ProcessingStatus, get_choices


class IngestionLog(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    batch_id = models.CharField(max_length=40, null=True, blank=True, db_index=True)
    url = models.CharField(max_length=200, null=True, blank=True)
    file_format = models.CharField(max_length=5, choices=get_choices(FileFormats))
    processing_status = models.CharField(max_length=12, choices=get_choices(ProcessingStatus), default=ProcessingStatus.PENDING.value)
    failure_reason = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.uuid}__{self.url}"

    @property
    def ingest_response(self):
        return {
            'uid': self.uuid,
            'batch_id': self.batch_id,
            'processing_status': self.processing_status,
            'url': self.url
        }
    
class Chat(models.Model):
    question = models.TextField(null=False)
    answer = models.TextField(null=True)
    meta_data = models.JSONField(null=True)

    def __str__(self):
        return f"{self.id}"
