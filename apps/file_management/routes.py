import os
from fastapi import APIRouter, HTTPException, UploadFile, File, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from base.load_env import load_env

from apps.chatbot.routes import create_embeddings

router = APIRouter()

load_env()
upload_directory = os.getenv("PATH_TO_UPLOAD_FOLDER")

templates = Jinja2Templates(directory=["shared_templates", "apps/backoffice/templates", "apps/file_management/templates", "apps/chatbot/templates"])

@router.get("/list_files", response_class=HTMLResponse)
async def list_files(request: Request): 
    """ Listar los archivos que formaran parte de la base de conocimiento."""
    if not os.path.exists(upload_directory):
        os.makedirs(upload_directory, exist_ok=True)        
    files = os.listdir(upload_directory)
    message = request.session.pop("message", None)
    return templates.TemplateResponse("admin_files.html", {"request": request, "files": files, "message": message})

@router.post("/delete/")
def delete_file(request: Request, filename: str = Form(...)):  
    """ Eliminar un archivo de la base de conocimiento y actualiza embeddings."""
    file_path = os.path.join(upload_directory, filename)
    
    if os.path.exists(file_path):
        os.remove(file_path)
        create_embeddings()
        request.session["message"] = f"Archivo '{filename}' eliminado exitosamente. Actualización correcta de la base de conocimiento."    
        return RedirectResponse("/files/list_files", status_code=303)
    else:
        raise HTTPException(status_code=404, detail="Archivo no encontrado")

@router.post("/upload/", response_class=HTMLResponse)
async def upload_file(request: Request, file: UploadFile = File(...)):
    """ Sube un archivo a la base de conocimiento y actualiza embeddings."""
    try:
        file_path = os.path.join(upload_directory, file.filename)
        with open(file_path, "wb") as buffer:
            buffer.write(file.file.read())
        create_embeddings()
        request.session["message"] = f"Archivo: '{file.filename}' subido exitosamente. Actualización correcta de la base de conocimiento."
        return RedirectResponse("/files/list_files", status_code=303)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
   