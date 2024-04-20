
from typing import List
from asgiref.sync import sync_to_async
from rest_framework import status

from django.db import (
    OperationalError,
    DatabaseError,
    DataError,
    InternalError,
    IntegrityError,
    transaction)

from decorators.retry import async_retry_and_timeout
from exceptions.service_error import ServiceException
from exceptions.error_codes import ErrorCodes
from .models import IngestionLog, Chat


@async_retry_and_timeout(retries=1, wait_time=2000, timeout=4)
@sync_to_async
def filter_ingestion_logs(batch_id: str) -> List[IngestionLog]:
    """
    Asynchronously filter logs based on batch_id.
    
    """
    try:
        with transaction.atomic():
            logs = IngestionLog.objects.filter(batch_id=batch_id)
            logs_info = [log.ingest_response for log in logs]
            return logs_info

    except (OperationalError, DatabaseError, InternalError):
        raise ServiceException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, ErrorCodes.INTERNAL_SERVER_ERROR, 'Unabe to query DB')
    

@async_retry_and_timeout(retries=1, wait_time=2000, timeout=4)
@sync_to_async
def create_chat(chat_data: dict) -> Chat:
    """
    Asynchronously create  a CHat object based on its.
    
    """
    try:
        with transaction.atomic():
            post = Chat.objects.create(**chat_data)
            return post

    except IntegrityError:
        raise ServiceException(status.HTTP_409_CONFLICT, ErrorCodes.RESOURCE_DUPLICATION_ATTEMPTED, f'Attempting Duplicate Post ID{post_data}')

    except (OperationalError, DatabaseError, InternalError):
        raise ServiceException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, ErrorCodes.INTERNAL_SERVER_ERROR, 'Unable to query DB')
    

@async_retry_and_timeout(retries=1, wait_time=2000, timeout=4)
@sync_to_async
def ingestion_log_bulk_create(ingest_logs: list) -> List[IngestionLog]:
    """
    Asynchronously creates bulk ingestion.
    """
    try:
        with transaction.atomic():
            logs = IngestionLog.objects.bulk_create(ingest_logs, ignore_conflicts=True)
            return logs

    except IntegrityError:
        raise ServiceException(status.HTTP_409_CONFLICT, ErrorCodes.RESOURCE_DUPLICATION_ATTEMPTED, f'Attempting Duplicate Post ID{post_data}')

    except (OperationalError, DatabaseError, InternalError):
        raise ServiceException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, ErrorCodes.INTERNAL_SERVER_ERROR, 'Unable to query DB')