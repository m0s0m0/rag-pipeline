import chromadb
from chromadb.config import Settings
from .ai import CustomEmbeddingFunction
from django.conf import settings

CHROMA_HOST = settings.CHROMA_HOST
CHROMA_COLLECTION = settings.CHROMA_COLLECTION

DB_PATH = "rag_train"
chroma_client = chromadb.HttpClient(host=CHROMA_HOST,port=8000, settings=Settings(allow_reset=True, anonymized_telemetry=False))
print('HEARTBEAT:', chroma_client.heartbeat())

collection = chroma_client.get_or_create_collection(
    name=CHROMA_COLLECTION, embedding_function=CustomEmbeddingFunction())