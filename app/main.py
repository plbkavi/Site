from pathlib import Path

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.weather import get_weather

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")

app = FastAPI(title="Media Hub")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

templates = Jinja2Templates(directory=BASE_DIR / "app" / "templates")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"page_title": "Media Hub"},
    )


@app.get("/weather", response_class=HTMLResponse)
async def weather(
    request: Request,
    city: str = Query(default="", max_length=100),
):
    city = city.strip()
    weather_data = None
    error = None

    if city:
        try:
            weather_data = await get_weather(city)
            if weather_data is None:
                error = f"Город «{city}» не найден. Проверьте написание и попробуйте снова."
        except httpx.HTTPError:
            error = (
                "Не удалось получить данные Open-Meteo. "
                "Проверьте подключение VPS к интернету и повторите попытку."
            )

    return templates.TemplateResponse(
        request=request,
        name="weather.html",
        context={
            "page_title": "Погода",
            "city": city,
            "weather": weather_data,
            "error": error,
        },
    )


@app.get("/health")
async def health():
    return {"status": "ok"}
