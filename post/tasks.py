import logging
import os
from typing import List

from django.core.exceptions import ObjectDoesNotExist

from celery import shared_task, group
from langchain.text_splitter import RecursiveCharacterTextSplitter
from post.constants import FileFormats, ProcessingStatus
from post.models import IngestionLog
import dask
from dask import delayed
from dask.distributed import Client
from langchain_core.documents.base import Document
from .core import DataIngestionFactory
from .chroma import collection

client = Client()

def get_log_ids_for_batch(batch_id: str) -> List[str]:
    logs = IngestionLog.objects.filter(batch_id=batch_id)
    urls = logs.values_list('id', 'file_format')
    return list(urls)

@delayed
def split_document(document: Document):
    text_splitter = RecursiveCharacterTextSplitter(
        separators = ["\n\n", "\n", " ", ""], chunk_size = 1600, chunk_overlap= 200)
    return text_splitter.split_documents(documents=[document])
    

@shared_task
def process_url(log_id: int, file_format: FileFormats):
    try:
        log = IngestionLog.objects.get(id=log_id)
        url = log.url
        log.processing_status = ProcessingStatus.STARTED.value
        log.save()
    except ObjectDoesNotExist:
        return 
    try:
        ingestion_service = DataIngestionFactory(file_format).get_ingestion_service
        documents = ingestion_service(url).ingest
        delayed_results = dask.compute(*[dask.delayed(split_document)(doc) for doc in documents])
        all_chunks = [item for sublist in delayed_results for item in sublist]
        chunk_ids = [f"chunk_{index}" for index in enumerate(all_chunks)]
        page_contents = [doc.page_content for doc in all_chunks]
        collection.add(documents=page_contents, ids=chunk_ids)
        log.processing_status = ProcessingStatus.DONE.value
        log.save()
        return len(page_contents)
    except Exception as e:
        logging.error(str(e))
        log.processing_status = ProcessingStatus.FAILED.value
        log.failure_reason = str(e)
        log.save()

@shared_task
def ingest_data(batch_id: str):
    urls = get_log_ids_for_batch(str(batch_id))
    task_group = group(process_url.s(log_id, file_format) for log_id, file_format in urls)
    result_group = task_group()
    

