import os
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
import chromadb.utils.embedding_functions as embedding_functions



class CustomEmbeddingFunction:
    def __init__(self):
        self.embedding_func = None

    def __call__(self, input):
        if self.embedding_func is None:
            EMBED_MODEL = "all-MiniLM-L6-v2"
            self.embedding_func = SentenceTransformerEmbeddingFunction(model_name=EMBED_MODEL)
            #self.embedding_func= embedding_functions.OpenAIEmbeddingFunction(api_key=os.environ.get('OPENAI_API_KEY'))
            
        return self.embedding_func(input)

