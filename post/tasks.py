import logging
import os
from celery import shared_task
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores.faiss import FAISS
from .chroma import chroma_client
from chromadb.utils import embedding_functions
from .embedding import CustomEmbeddingFunction



@shared_task
def ingest_data():
    EMBED_MODEL = "all-MiniLM-L6-v2"
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    CHROMA_PATH  = "rag_train"
    loader = PyPDFLoader("https://afeias.com/wp-content/uploads/2023/06/HISTORY-ENGLISH.pdf")
    pages = loader.load()
    documents = [
    "A group of vibrant parrots chatter loudly, sharing stories of their tropical adventures.",
    "The mathematician found solace in numbers, deciphering the hidden patterns of the universe.",
    "The robot, with its intricate circuitry and precise movements, assembles the devices swiftly.",
    "The chef, with a sprinkle of spices and a dash of love, creates culinary masterpieces.",
    "The ancient tree, with its gnarled branches and deep roots, whispers secrets of the past.",
    "The detective, with keen observation and logical reasoning, unravels the intricate web of clues.",
    "The sunset paints the sky with shades of orange, pink, and purple, reflecting on the calm sea.",
    "In the dense forest, the howl of a lone wolf echoes, blending with the symphony of the night.",
    "The dancer, with graceful moves and expressive gestures, tells a story without uttering a word.",
    "In the quantum realm, particles flicker in and out of existence, dancing to the tunes of probability."]
    chunks = text_splitter.split_documents(pages)
    document_ids = list(map(lambda tup: f"id{tup[0]}", enumerate(documents)))
    test_collection = chroma_client.get_or_create_collection(name="sample_collection", embedding_function=CustomEmbeddingFunction())
    print ("test_collection", test_collection)
    test_collection.add(documents=documents, ids=document_ids)







