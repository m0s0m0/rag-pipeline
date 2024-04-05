from rest_framework import serializers
from pydantic import BaseModel
from typing import List

class DataIngestionDTO(BaseModel):
    file_urls: List[str]


class ChatDTO(BaseModel):
    question: str
