import os
from fastapi import APIRouter, HTTPException, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from base.load_env import load_env
from ia.llm.manage_llm import LlmManager
from ia.embeddings.manage_embeddings import EmbeddingsManager

router = APIRouter()

templates = Jinja2Templates(directory=["shared_templates", "apps/backoffice/templates", "apps/file_management/templates", "apps/chatbot/templates"])

class Message(BaseModel):
    user_message: str
    history: list = []

class Message_without_memory(BaseModel):
    user_message: str

load_env()

api_key = os.getenv("OPENAI_API_KEY")
persist_directory = os.getenv("PERSIST_CHROMADB_FOLDER")
upload_directory = os.getenv("PATH_TO_UPLOAD_FOLDER")
file_types = os.getenv("FILES_TYPES")       

def create_embeddings():
    """
    Genera embeddings a partir de los archivos en un directorio dado.

    Args:
        upload_directory (str): Ruta al directorio de uploads.
        file_types (str): Tipos de archivo permitidos.
        api_key (str): API key para el gestor de embeddings.
        persist_directory (str): Ruta al directorio donde se guardan los embeddings.

    Returns:
        dict: Estado del proceso.
    """

    # Verificar que existan archivos en el directorio de uploads, para que no de error el generador de embeddings
    if not os.listdir(upload_directory):
        raise HTTPException(status_code=400, detail="No hay archivos en el directorio de uploads")

    try:
        manager = EmbeddingsManager("openai", api_key, persist_directory)
        manager.save_embeddings(upload_directory, file_types)
        return {"status": "Embeddings generados correctamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/generate_embeddings/")
def generate_embeddings():        
    """ Endpoint creado por las dudas en un futuro se desee crear los embiddings a través de una ruta. """
    try:
        result = create_embeddings()
        return result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_class=HTMLResponse)
async def get_chat_page(request: Request):
    """
    Renderiza la página del chatbot al acceder por primera vez.
    """
    return templates.TemplateResponse("chat.html", {"request": request, "bot_response": None, "sources": None})

@router.post("/", response_class=HTMLResponse)
#async def chat_with_bot(request: Request, user_message: str = Form(...), history: list = Form([])):
async def chat_with_bot(request: Request, user_message: str = Form(...)):
    """
    Procesa el mensaje del usuario y devuelve la respuesta del chatbot junto con la página actualizada.
    """
    try:
        session_history = request.session.get("history", [])

        llm_manager = LlmManager("openai")
        llm = llm_manager.initialice_llm_model(api_key=api_key, model_name="gpt-3.5-turbo")
        manager = EmbeddingsManager("openai", api_key, persist_directory)
        stored_embeddings = manager.get_embeddings()
        QA_chain = llm_manager.initialice_retriever(llm, stored_embeddings)

        # Obtener la respuesta del chatbot
        bot_response, sources = llm_manager.get_response_retriever(QA_chain, user_message, session_history)
        
        # Actualizar historial
        session_history.append({"user": user_message, "assistant": bot_response})
        request.session["history"] = session_history

        #print("Historial actualizado:", history)

        # Renderizar la página con los datos actualizados
        return templates.TemplateResponse("chat.html", {
            "request": request,
            "bot_response": bot_response,
            "sources": sources,
            "history": session_history,
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/embeded", response_model=dict)
async def chat_with_bot_embeded(request: Request, user_message: str = Form(...)):
    """
    Procesa el mensaje del usuario y devuelve la respuesta del chatbot embebido. Esta función es casi igual a la chat_with_bot,
    solo difiere en la respuesta para que funciones correctamente.
    """
    try:
        # Obtener el historial actual de la sesión, si existe
        session_history = request.session.get("history", [])
        
        # Inicializar LLM y otros componentes necesarios
        llm_manager = LlmManager("openai")
        llm = llm_manager.initialice_llm_model(api_key=api_key, model_name="gpt-3.5-turbo")
        manager = EmbeddingsManager("openai", api_key, persist_directory)
        stored_embeddings = manager.get_embeddings()
        QA_chain = llm_manager.initialice_retriever(llm, stored_embeddings)
        
        # Obtener la respuesta del chatbot
        bot_response, sources = llm_manager.get_response_retriever(QA_chain, user_message, session_history)
        
        # Actualizar historial de la sesión
        session_history.append({"user": user_message, "assistant": bot_response})
        request.session["history"] = session_history
        
        # Preparar respuesta
        return {
            "bot_response": bot_response,
            "sources": sources,
            "history": session_history,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))