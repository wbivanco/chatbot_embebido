
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_chroma import Chroma

from .utils import Utils

class EmbeddingsWrapper:
    """ Clase que envuelve un modelo de embeddings para que pueda ser utilizado por Chroma. 
    Coorrige error en el método embed_query. """
    def __init__(self, model):
        self.model = model

    def embed_documents(self, documents):
        """Usar el modelo original para obtener los embeddings de los documentos"""
        return self.model.embed_documents(documents)
    
    def embed_query(self, query):
        """Reutilizar el método embed_documents para queries"""
        return self.model.embed_documents([query])[0]  # Envolver la query en una lista y devolver el embedding

class EmbeddingsManager:
    def __init__(self, embedding_provider, api_key, persist_directory) -> None:
        """ Inicializa el directorio de persistencia y el modelo de embeddings. """
        self.persist_directory = persist_directory
        self.embeddings_provider = embedding_provider
        self.embeddings_model = self.initialice_embedding_model(api_key)
    
    def initialice_embedding_model(self, api_key):
        """ Define e inicializa el modelo a utilizar en la generación de embeddings. """        
        try:
            if self.embeddings_provider == "openai":
                embeddings_model = OpenAIEmbeddings(api_key=api_key)
        except Exception as e:
            print(f"Error al cargar el tipo de modelo de Embedding: {e}")
            embeddings_model = None 

        return embeddings_model

    def save_embeddings(self, upload_directory, file_types):
        """ Guarda los embeddings generados en una BD vectorial. """ 
        document_chunks = Utils.load_chunked_documents(upload_directory, file_types)
        embeddings_model = EmbeddingsWrapper(self.embeddings_model)
        
        Chroma.from_documents(
            documents=document_chunks, 
            embedding=embeddings_model, 
            persist_directory=self.persist_directory
        ) 

    def get_embeddings(self):
        """ Obtiene los embeddings generados. """              
        embeddings_model_wrapper = EmbeddingsWrapper(self.embeddings_model)  

        stored_embeddings = Chroma(
            embedding_function=embeddings_model_wrapper, 
            persist_directory=self.persist_directory
        )

        return stored_embeddings
