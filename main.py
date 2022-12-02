import json

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import models
from database import SessionLocal, engine


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Create tables if not exist
models.Base.metadata.create_all(bind=engine)
db = SessionLocal()


@app.middleware("http")
async def get_request_path(request: Request, call_next):
    """
    Middleware que intercepta toda request que chega, verifica no banco se já
    existe um endpoint mocado para ela, e retorna os dados mocados caso exista.
    Caso não exista, adiciona uma entrada no banco, para que seja possível
    preencher o restante dos dados na tela de admin.
    """
    exceptions_paths = [
        "/admin",
        "/admin/",
        "/save",
        "/static/css/custom.css",
        "/static/css/bulma.min.css",
        "/favicon.ico",
    ]
    if request.url.path in exceptions_paths:
        response = await call_next(request)
        return response
    else:
        path = (
            db.query(models.Path)
            .filter(
                models.Path.endpoint == request.url.path,
                models.Path.method == request.method,
            )
            .first()
        )
        if path:
            # Retorna as informações mocadas
            response = JSONResponse(
                path.return_body, headers=path.return_header
            )
        else:
            # Registrar o novo endpoint
            path_to_create = models.Path(
                endpoint=request.url.path,
                method=request.method,
                return_body={},
                return_header={},
            )
            db.add(path_to_create)
            db.commit()
            response = await call_next(request)
        db.close()
        return response


@app.get("/admin", response_class=HTMLResponse)
async def load_html(request: Request):
    paths = db.query(models.Path).order_by(models.Path.id.asc())
    payload = []
    db.close()

    for path in paths:
        payload.append(
            {
                "id": path.id,
                "method": path.method,
                "endpoint": path.endpoint,
                "return_body": path.return_body,
                "return_header": path.return_header,
            }
        )

    return templates.TemplateResponse(
        "admin.html", {"request": request, "payload": payload}
    )


@app.post("/admin", response_class=HTMLResponse)
async def load_html(
    request: Request,
    method: str = Form(),
    endpoint: str = Form(),
    # return_header: str = Form(),
    return_body: str = Form(),
):
    # Update data
    db.query(models.Path).filter(models.Path.endpoint == endpoint).update({
        "method": method,
        # "return_header": json.loads(return_header.replace("\'", "\"")),
        "return_body": json.loads(return_body.replace("\'", "\"")),
    })
    db.commit()

    # Load all data and return
    paths = db.query(models.Path).order_by(models.Path.id.asc())
    payload = []
    db.close()

    for path in paths:
        payload.append(
            {
                "id": path.id,
                "method": path.method,
                "endpoint": path.endpoint,
                "return_body": path.return_body,
                "return_header": path.return_header,
            }
        )

    return templates.TemplateResponse(
        "admin.html", {"request": request, "payload": payload}
    )
