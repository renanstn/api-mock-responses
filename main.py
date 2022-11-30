from fastapi import FastAPI, Request
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
    if request.url.path.endswith("/html"):
        response = await call_next(request)
        return response
    else:
        path = (
            db.query(models.Path)
            .filter(models.Path.endpoint == request.url.path)
            .first()
        )
        if path:
            # TODO carregar header e body do banco e retornar
            response = JSONResponse({"message": "customizada"})
        else:
            # Registrar o novo endpoint
            path_to_create = models.Path(
                endpoint=request.url.path,
                return_body={},
                return_header={},
            )
            db.add(path_to_create)
            db.commit()
            response = await call_next(request)
        db.close()
        return response


@app.get("/")
async def ping():
    return {"message": "pong"}


@app.get("/html", response_class=HTMLResponse)
async def load_html(request: Request):
    return templates.TemplateResponse("test.html", {"request": request})
