import logging
import os
from exceptions.service_error import ServiceException
from post.constants import FileFormats, ProcessingStatus
from abc import ABC, abstractmethod
from exceptions.error_codes import ErrorCodes
from rest_framework import status
from langchain_community.document_loaders import PyPDFLoader
from .chroma import collection
from openai import OpenAI

class ChatService(object):
    
    def __init__(self, question) -> None:
        self.question = question

    
    def process_answer_from_db(self) -> dict:
        result = collection.query(query_texts=[self.question], n_results=5, include=["documents", 'distances',"embeddings"])
        if not result:
            return {}
        ids = result.get('ids')[0]
        documents = result.get('documents')[0]
        distances = result.get('distances')[0]
        context=  "\n".join(str(item) for item in result['documents'][0])
        
        response = []
        for id_, document, distance in zip(ids, documents, distances):
            print(f"ID: {id_}, Document: {document}, Similarity: {1 - distance}")
            response.append({'id': id_, "document": document, "similarity": 1-distance})
       

        return {"db_answer": response[0]["document"], "context": context, "meta_data": response, "chunk_id": response[0]["id"]}


    def process_answer_from_openai(self, context=None):
        context = "Indian constituion"
        prompt=f"""{context}```Based on the data in ```, answer {self.question}"""
        messages = [
            {"role": "system", "content": "You are an indian constitution teacher"},
            {"role": "user", "content": prompt}
]
        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0)
        response_message = response.choices[0].message.content
        return {"answer" :response_message}


    def fetch_answer(self):
        db_response = self.process_answer_from_db()
        context = db_response.get("context")
        llm_response = self.process_answer_from_openai(context)
        response = {**db_response, **llm_response}
        return response


class DataIngestionService(ABC):

    
    @abstractmethod
    def ingest(self):
        pass


class PdfIngestion(DataIngestionService):

    def __init__(self, url: str):
        self.url = url
        
    @property
    def ingest(self):
        try:
            loader = PyPDFLoader(self.url)
            documents = loader.load()
            return documents
        except Exception as e:
            logging.error(str(e))
            return 

class DataIngestionFactory(object):
    INGESTION_FACTORY = {
        "PDF": PdfIngestion,
    }

    def __init__(self, file_format: FileFormats) -> None:
        self.file_format = file_format
    
    @property
    def get_ingestion_service(self):
        try:
            service = self.INGESTION_FACTORY[self.file_format]
            return service
        except KeyError as e:
            raise ServiceException(status.HTTP_501_NOT_IMPLEMENTED, ErrorCodes.NOT_IMPLEMENTED, 'Ingestion for file format not implemented')