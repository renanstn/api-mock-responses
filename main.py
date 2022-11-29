from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.middleware("http")
async def get_request_path(request: Request, call_next):
    if request.url.path.endswith("/html"):
        response = await call_next(request)
        return response
    else:
        if request.url.path == "/batata":
            response = JSONResponse({"message": "customizada"})
        else:
            response = await call_next(request)
        return response


@app.get("/")
async def ping():
    return {"message": "pong"}

@app.get("/html", response_class=HTMLResponse)
async def load_html(request: Request):
    return templates.TemplateResponse("test.html", {"request": request})
