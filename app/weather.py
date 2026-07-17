from typing import Any

import httpx

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"


def weather_description(code: int) -> tuple[str, str]:
    """Возвращает русское описание и эмодзи для WMO-кода погоды."""
    codes = {
        0: ("Ясно", "☀️"),
        1: ("Преимущественно ясно", "🌤️"),
        2: ("Переменная облачность", "⛅"),
        3: ("Пасмурно", "☁️"),
        45: ("Туман", "🌫️"),
        48: ("Изморозь и туман", "🌫️"),
        51: ("Слабая морось", "🌦️"),
        53: ("Умеренная морось", "🌦️"),
        55: ("Сильная морось", "🌧️"),
        56: ("Ледяная морось", "🌧️"),
        57: ("Сильная ледяная морось", "🌧️"),
        61: ("Небольшой дождь", "🌦️"),
        63: ("Дождь", "🌧️"),
        65: ("Сильный дождь", "🌧️"),
        66: ("Ледяной дождь", "🌧️"),
        67: ("Сильный ледяной дождь", "🌧️"),
        71: ("Небольшой снег", "🌨️"),
        73: ("Снег", "🌨️"),
        75: ("Сильный снег", "❄️"),
        77: ("Снежные зёрна", "❄️"),
        80: ("Кратковременный дождь", "🌦️"),
        81: ("Ливень", "🌧️"),
        82: ("Сильный ливень", "⛈️"),
        85: ("Снегопад", "🌨️"),
        86: ("Сильный снегопад", "❄️"),
        95: ("Гроза", "⛈️"),
        96: ("Гроза с градом", "⛈️"),
        99: ("Сильная гроза с градом", "⛈️"),
    }
    return codes.get(code, ("Неизвестная погода", "🌡️"))


async def get_weather(city: str) -> dict[str, Any] | None:
    """Ищет город и получает его текущую погоду с прогнозом на 5 дней."""
    timeout = httpx.Timeout(10.0)

    async with httpx.AsyncClient(timeout=timeout) as client:
        geocoding_response = await client.get(
            GEOCODING_URL,
            params={
                "name": city,
                "count": 1,
                "language": "ru",
                "format": "json",
            },
        )
        geocoding_response.raise_for_status()
        locations = geocoding_response.json().get("results", [])

        if not locations:
            return None

        location = locations[0]

        forecast_response = await client.get(
            FORECAST_URL,
            params={
                "latitude": location["latitude"],
                "longitude": location["longitude"],
                "current": (
                    "temperature_2m,apparent_temperature,"
                    "weather_code,wind_speed_10m"
                ),
                "daily": "weather_code,temperature_2m_max,temperature_2m_min",
                "timezone": "auto",
                "forecast_days": 5,
            },
        )
        forecast_response.raise_for_status()
        forecast = forecast_response.json()

    current = forecast["current"]
    current_description, current_icon = weather_description(current["weather_code"])

    days = []
    daily = forecast["daily"]

    for index, date in enumerate(daily["time"]):
        description, icon = weather_description(daily["weather_code"][index])
        days.append(
            {
                "date": date,
                "description": description,
                "icon": icon,
                "temp_max": round(daily["temperature_2m_max"][index]),
                "temp_min": round(daily["temperature_2m_min"][index]),
            }
        )

    place_parts = [location["name"]]
    if location.get("admin1"):
        place_parts.append(location["admin1"])
    if location.get("country"):
        place_parts.append(location["country"])

    return {
        "place_name": ", ".join(place_parts),
        "timezone": forecast.get("timezone", "auto"),
        "current": {
            "temperature": round(current["temperature_2m"]),
            "apparent_temperature": round(current["apparent_temperature"]),
            "wind_speed": round(current["wind_speed_10m"]),
            "description": current_description,
            "icon": current_icon,
        },
        "days": days,
    }
