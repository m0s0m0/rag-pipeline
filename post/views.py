import json
from pydantic import ValidationError
from rest_framework import status

from exceptions.error_codes import ErrorCodes
from exceptions.service_error import ServiceException
from utils.response import SendAsyncResponse
from utils.common import generate_uuid, get_file_url_extension
from .validators import ChatDTO, DataIngestionDTO
from .models import IngestionLog
from .async_queries import create_chat, filter_ingestion_logs
from .tasks import ingest_data
from .core import ChatService


def data_ingestion(request, *args, **kwargs):
    
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
        _ = IngestionLog.objects.bulk_create(logs)

        ingest_data(batch_id)

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
        chat_dto = ChatDTO(**data)
        question = chat_dto.question
        
        
        result = ChatService(question).fetch_answer()
        
        await create_chat(dict(question=question, answer=result["answer"], meta_data=result["meta_data"]))

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

