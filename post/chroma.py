import chromadb
from chromadb.config import Settings
DB_PATH = "rag_train"
chroma_client = chromadb.HttpClient(host="chromaDB",port=8000, settings=Settings(allow_reset=True, anonymized_telemetry=False))
print('HEARTBEAT:', chroma_client.heartbeat())