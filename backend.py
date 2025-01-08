import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from base.load_env import load_env
from apps.chatbot.routes import router as chatbot_router
from apps.file_management.routes import router as file_management_router
from apps.embedded_chat.routes import router as embedded_chatbot_router
from apps.login.routes import router as login_router
from apps.backoffice.routes import router as backoffice_router

load_env()
openai_api_key = os.getenv("OPENAI_API_KEY")
persist_directory = os.getenv("PERSIST_CHROMADB_FOLDER")
upload_directory = os.getenv("PATH_TO_UPLOAD_FOLDER")

# Instancia de la aplicación FastAPI
app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key="ijdjandsncl as23nff m,")

app.mount("/login_static", StaticFiles(directory="apps/login/static"), name="login_static")
app.mount("/backoffice_static", StaticFiles(directory="apps/backoffice/static"), name="backoffice_static")
app.mount("/files_static", StaticFiles(directory="apps/file_management/static"), name="files_static")
app.mount("/chatbot_static", StaticFiles(directory="apps/chatbot/static"), name="chatbot_static")

# Configuración de plantillas Jinja2, si se modifica aquí, se debe modificar en todos los routes
templates = Jinja2Templates(directory=["shared_templates", "apps/backoffice/templates", "apps/file_management/templates", "apps/chatbot/templates"])

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todas las URL en desarrollo; ajusta para producción
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos (GET, POST, etc.)
    allow_headers=["*"],  # Permite todos los encabezados
)

# Incluir routers
app.include_router(chatbot_router, prefix="/chatbot", tags=["Chatbot"])
app.include_router(file_management_router, prefix="/files", tags=["File Management"])
app.include_router(embedded_chatbot_router, prefix="/embedded_chatbot", tags=["Embedded Chatbot"])
app.include_router(login_router, prefix="/auth", tags=["Login"])
app.include_router(backoffice_router, prefix="/backoffice", tags=["Backoffice"])

