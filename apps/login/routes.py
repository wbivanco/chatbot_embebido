import bcrypt

from random import randint

from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="apps/login/templates")

router = APIRouter()

# Encriptar las contraseñas
users = {
    "user1": bcrypt.hashpw("pass1".encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
    "user2": bcrypt.hashpw("pass2".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
}

@router.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    # Generar dos números aleatorios para el captcha
    num1, num2 = randint(1, 10), randint(1, 10)
    captcha_answer = num1 + num2
    # Almacenar la respuesta correcta en la sesión
    request.session["captcha_answer"] = captcha_answer
    captcha_question = f"{num1} + {num2} = ?"
    return templates.TemplateResponse("login.html", {"request": request, "captcha_question": captcha_question})

@router.post("/login", response_class=HTMLResponse)
async def login_post(
    request: Request, 
    username: str = Form(...), 
    password: str = Form(...), 
    captcha: str = Form(...)
):
    # Verificar la respuesta del captcha
    correct_answer = request.session.get("captcha_answer")
    if correct_answer is None or int(captcha) != correct_answer:
        num1, num2 = randint(1, 10), randint(1, 10)
        captcha_answer = num1 + num2
        request.session["captcha_answer"] = captcha_answer
        captcha_question = f"{num1} + {num2} = ?"

        return templates.TemplateResponse("login.html", {
            "request": request, 
            "error": "Captcha incorrecto. Inténtalo de nuevo.",
            "captcha_question": captcha_question 
        })

    # Verificar las credenciales
    if username in users and bcrypt.checkpw(password.encode('utf-8'), users[username].encode('utf-8')):
        request.session["username"] = username
        return RedirectResponse("/backoffice", status_code=303)
    
    num1, num2 = randint(1, 10), randint(1, 10)
    captcha_answer = num1 + num2
    request.session["captcha_answer"] = captcha_answer
    captcha_question = f"{num1} + {num2} = ?" 
    return templates.TemplateResponse("login.html", {
        "request": request, 
        "error": "Credenciales inválidas.",
        "captcha_question": captcha_question 
    })

""" DEJO ESTE CODIGO POR LAS DUDAS, ENVIA A LA PAGINA DE INICIO LUEGO DEL LOGIN"""  
# @router.get("/", response_class=HTMLResponse)
# async def index(request: Request):
#     if "username" in request.session:
#         return templates.TemplateResponse("index.html", {"request": request})
#     return RedirectResponse("/auth/login")
