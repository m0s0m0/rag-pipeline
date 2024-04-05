import logging
import json
import random
from langchain import hub
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.vectorstores.faiss import FAISS
from langchain.chains import create_retrieval_chain
from pydantic import ValidationError
from rest_framework import status

from django.conf import settings

from exceptions.error_codes import ErrorCodes
from exceptions.service_error import ServiceException
from utils.response import SendAsyncResponse
from utils.common import generate_uuid, get_file_url_extension
from .validators import ChatDTO, DataIngestionDTO
from .chroma import chroma_client
from .embedding import CustomEmbeddingFunction
from .models import IngestionLog
from .async_queries import create_chat, ingestion_log_bulk_create, filter_ingestion_logs
from .tasks import ingest_data


async def data_ingestion(request, *args, **kwargs):
    
    try:
        if request.method != 'POST':
            raise ServiceException(
                status.HTTP_405_METHOD_NOT_ALLOWED,
                ErrorCodes.METHOD_NOT_ALLOWED,
                message='Method not allowed')
        data =json.loads(request.body)
        ingestion_dto = DataIngestionDTO(**data)
        file_urls = ingestion_dto.file_urls
        batch_id = generate_uuid()
        logs = [IngestionLog(batch_id=batch_id, file_format=get_file_url_extension(url), url=url) for url in file_urls]
        ingested_logs = await ingestion_log_bulk_create(logs)

        ingest_data.delay()

        return SendAsyncResponse(
                status.HTTP_200_OK, {"batch_id": batch_id}, 'data ingestion started')

    except ValidationError as e:
        return SendAsyncResponse(status.HTTP_400_BAD_REQUEST, None,
             'Request data Not valid', ErrorCodes.REQUEST_VALIDATION_FAILED.value)

    except ServiceException as e:
        return SendAsyncResponse(
            e.status_code, None,
            error_code=e.error_code, message=e.message)

    except Exception as e:
        return SendAsyncResponse(
            status.HTTP_500_INTERNAL_SERVER_ERROR, None,
            error_code=500, message=str(e))
    

async def ingestion_status(request, *args, **kwargs):
    try:
        logs_info = []
        if request.method != 'GET':
            raise ServiceException(
                status.HTTP_405_METHOD_NOT_ALLOWED,
                ErrorCodes.METHOD_NOT_ALLOWED,
                message='Method not allowed')
        batch_id = request.GET.get('batch_id')
        logs_info = await filter_ingestion_logs(batch_id)

        return SendAsyncResponse(
                status.HTTP_200_OK, logs_info, 'ingestion logs fetched successfully')


    except ServiceException as e:
        return SendAsyncResponse(
            e.status_code, None,
            error_code=e.error_code, message=e.message)

    except Exception as e:
        return SendAsyncResponse(
            status.HTTP_500_INTERNAL_SERVER_ERROR, None,
            error_code=500, message=str(e)) 
    

async def chat(request, *args, **kwargs):
    try:
        if request.method != 'POST':
            raise ServiceException(
                status.HTTP_405_METHOD_NOT_ALLOWED,
                ErrorCodes.METHOD_NOT_ALLOWED,
                message='Method not allowed')
        data = data=json.loads(request.body)
        chat_dto = ChatDTO.model_validate(data)

        question = chat_dto.question
        retrieval_qa_chat_prompt = hub.pull("langchain-ai/retrieval-qa-chat")
        llm = ChatOpenAI()
        test_collection = chroma_client.get_or_create_collection(name="sample_collection", embedding_function=CustomEmbeddingFunction())
        result = test_collection.query(query_texts=[question], n_results=5, include=["documents", 'distances',])
        ids = result.get('ids')[0]
        # Extract the first (and only) list inside 'documents'
        documents = result.get('documents')[0]
        # Extract the first (and only) list inside 'documents'
        distances = result.get('distances')[0]

        result = []
            
        for id_, document, distance in zip(ids, documents, distances):
            print(f"ID: {id_}, Document: {document}, Similarity: {1 - distance}")
            result.append({'id': id_, "document": document, "similarity": 1-distance})

        await create_chat(dict(question=question, answer=result[0]['document'], meta_data=result))

        return SendAsyncResponse(
            status.HTTP_200_OK, result, 'Answer  Fetched Successfully')
    
    except ValidationError as e:
        return SendAsyncResponse(status.HTTP_400_BAD_REQUEST,
            ErrorCodes.REQUEST_VALIDATION_FAILED.value, 'Data Not valid')

    except ServiceException as e:
        return SendAsyncResponse(
            e.status_code, None,
            error_code=e.error_code, message=e.message)

    except Exception as e:
        return SendAsyncResponse(
            status.HTTP_500_INTERNAL_SERVER_ERROR, None,
            error_code=500, message=str(e))

