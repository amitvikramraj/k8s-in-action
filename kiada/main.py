import socket
from pathlib import Path

from fastapi import APIRouter, FastAPI, Request, status
from fastapi.responses import HTMLResponse, PlainTextResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

VERSION = "0.1.0"

THIS_DIR = Path(__file__).parent
STATIC_DIR = THIS_DIR / "static"
TEMPLATES_DIR = THIS_DIR / "templates"

ROUTER = APIRouter()

templates = Jinja2Templates(directory=TEMPLATES_DIR)


def get_info(request: Request) -> dict[str, str]:
    return {
        "version": VERSION,
        "hostname": socket.gethostname(),
        "clientIP": request.client.host,
    }



# this function guesses if the client that sent the request is a full-fledged
# graphical web browser and not a text-based tool such as curl
# graphical browsers typically send accept: text/html,application/xhtml+xml,...
# curl sends accept: */*
@ROUTER.get("/")
def root(request: Request):
    accept_header = request.headers.get("accept", "")
    if accept_header.startswith("*/*"):
        return RedirectResponse(url="/text")

    if accept_header.startswith("text/html"):
        return templates.TemplateResponse(
            request=request,
            name="redirect.html",
            context={
                "delay": 2,
                "target": "/html",
                "message": "Redirecting to the html version...",
            },
        )


@ROUTER.get("/html", response_class=HTMLResponse)
def serve_html_file(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context=get_info(request=request),
        media_type="text/html"
    )


@ROUTER.get("/text", response_class=PlainTextResponse)
def serve_text_file(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.txt",
        context=get_info(request=request),
        media_type="text/plain"
    )


async def custom_404_handler(request: Request, exc):
    return PlainTextResponse(
        content=f"'{request.url}' Not Found",
        status_code=status.HTTP_404_NOT_FOUND,
    )


exception_handlers = {404: custom_404_handler}

app = FastAPI(exception_handlers=exception_handlers)

app.mount(path="/static", app=StaticFiles(directory=STATIC_DIR), name="static")
app.include_router(router=ROUTER)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app=app, host="0.0.0.0", port=8080)
