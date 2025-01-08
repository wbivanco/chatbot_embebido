import os 

from langchain_community.document_loaders import PyPDFLoader, UnstructuredWordDocumentLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

class Utils:
    @staticmethod
    def generate_chunks(documento, chunk_size=3000, chunk_overlap=40):
        """ Divide un documento en fragmentos de texto. """
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        document_chunks = text_splitter.split_documents(documento)

        return document_chunks

    @staticmethod
    def load_chunked_documents(upload_directory, file_types):
        """ Genera una lista de chunks de documentos a partir de los archivos subidos al directorio de uploads y con las 
        extensiones permitidas pasadas como parámetro. """                
        loader_mapping = {
            ".pdf": PyPDFLoader,
            ".docx": UnstructuredWordDocumentLoader,
            ".txt": TextLoader
        }

        documents = []
        for filename in os.listdir(upload_directory):
            file_path = os.path.join(upload_directory, filename)     
            file_extension = os.path.splitext(filename)[1]

            if file_extension in file_types:
                loader_class = loader_mapping.get(file_extension)
                if loader_class:
                    loader = loader_class(file_path)
                    documento = loader.load()
                    
                    for doc in documento:
                        doc.metadata['source'] = filename
                    document_chunks = Utils.generate_chunks(documento)
                    documents.extend(document_chunks)
                else:
                    print(f"No se encontró un cargador para el tipo de archivo: {file_extension}")
            else:
                print(f"Tipo de archivo no soportado: {filename}")

        return documents
    