import os
from fastapi import APIRouter

router = APIRouter()

# Ruta de la API para servir el archivo HTML
@router.get("/show_chatbot/")
async def show_embedded_chatbot():
    from fastapi.responses import FileResponse

    ruta_html = os.path.join("apps/embedded_chat/embedded_chat_page.html") 
    return FileResponse(ruta_html, media_type="text/html")