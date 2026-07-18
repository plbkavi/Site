import os
from typing import Any

import httpx

OMDB_URL = "https://www.omdbapi.com/"


async def get_movie_details(
    client: httpx.AsyncClient,
    api_key: str,
    imdb_id: str,
) -> dict[str, Any] | None:
    """Получает полную информацию об одном фильме или сериале."""
    response = await client.get(
        OMDB_URL,
        params={
            "apikey": api_key,
            "i": imdb_id,
            "plot": "short",
        },
    )
    response.raise_for_status()
    data = response.json()

    if data.get("Response") != "True":
        return None

    poster = data.get("Poster", "N/A")
    if poster == "N/A":
        poster = None

    return {
        "imdb_id": data.get("imdbID", imdb_id),
        "title": data.get("Title", "Без названия"),
        "year": data.get("Year", "—"),
        "type": data.get("Type", "movie"),
        "poster": poster,
        "rating": data.get("imdbRating", "—"),
        "genres": data.get("Genre", "Не указаны"),
        "plot": data.get("Plot", "Описание пока недоступно."),
    }


async def search_media(query: str) -> tuple[list[dict[str, Any]], str | None]:
    """Ищет фильмы и сериалы в OMDb и возвращает подробные карточки."""
    api_key = os.getenv("OMDB_API_KEY")

    if not api_key:
        return [], "На сервере не настроен ключ OMDb."

    timeout = httpx.Timeout(12.0)

    async with httpx.AsyncClient(timeout=timeout) as client:
        search_response = await client.get(
            OMDB_URL,
            params={
                "apikey": api_key,
                "s": query,
                "type": "movie",
            },
        )
        search_response.raise_for_status()
        movie_data = search_response.json()

        series_response = await client.get(
            OMDB_URL,
            params={
                "apikey": api_key,
                "s": query,
                "type": "series",
            },
        )
        series_response.raise_for_status()
        series_data = series_response.json()

        search_items = []
        if movie_data.get("Response") == "True":
            search_items.extend(movie_data.get("Search", []))
        if series_data.get("Response") == "True":
            search_items.extend(series_data.get("Search", []))

        unique_items = {}
        for item in search_items:
            unique_items[item["imdbID"]] = item

        details = []
        for item in list(unique_items.values())[:6]:
            result = await get_movie_details(client, api_key, item["imdbID"])
            if result:
                details.append(result)

    if not details:
        return [], f"По запросу «{query}» фильмы и сериалы не найдены."

    return details, None
