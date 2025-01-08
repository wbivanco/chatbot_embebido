from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory=["shared_templates", "apps/backoffice/templates", "apps/file_management/templates", "apps/chatbot/templates"])

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def backoffice_home(request: Request):
    """ Renderiza la página principal del backoffice."""
    return templates.TemplateResponse("index.html", {"request": request})

@router.get("/logout")
async def logout(request: Request):
    """ Cierra la sesión del usuario y redirige a la página de inicio de sesión."""
    request.session.pop("username", None)
    return RedirectResponse("/auth/login")
