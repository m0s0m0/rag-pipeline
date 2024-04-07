import logging
import os
from typing import List
from uuid import UUID

from celery import shared_task, group
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores.faiss import FAISS
from post.constants import FileFormats
from post.models import IngestionLog
from .chroma import chroma_client
from chromadb.utils import embedding_functions
from .ai import CustomEmbeddingFunction
from langchain_openai import OpenAIEmbeddings
import dask
from dask import delayed
from dask.distributed import Client
from langchain_core.documents.base import Document
from .core import DataIngestionFactory
from .chroma import collection

client = Client()

def get_urls_for_batch(batch_id: str) -> List[str]:
    logs = IngestionLog.objects.filter(batch_id=batch_id)
    urls = logs.values_list('url', 'file_format')
    return list(urls)

@delayed
def split_document(document: Document):
    text_splitter = RecursiveCharacterTextSplitter(separators = ["\n\n", "\n", " ", ""], chunk_size = 1600, chunk_overlap= 200)
    return text_splitter.split_documents(documents=[document])
    

@shared_task
def process_url(url: str, file_format: FileFormats):
    ingestion_service = DataIngestionFactory(file_format).get_ingestion_service
    documents = ingestion_service(url).ingest
    logging.error(len(documents))
    delayed_results = dask.compute(*[dask.delayed(split_document)(doc) for doc in documents])
    all_chunks = [item for sublist in delayed_results for item in sublist]
    chunk_ids = [f"chunk_{index}" for index in enumerate(all_chunks)]
    page_contents = [doc.page_content for doc in all_chunks]
    collection.add(documents=page_contents, ids=chunk_ids)
    return len(all_chunks)

@shared_task
def ingest_data(batch_id: str):
    urls = get_urls_for_batch(str(batch_id))
    task_group = group(process_url.s(url, file_format) for url, file_format in urls)
    result_group = task_group()
    

