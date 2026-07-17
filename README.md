# Media Hub

Личный веб-сервис на Python, FastAPI и Jinja2.

## Первый этап

- Главная страница
- Поиск города
- Текущая погода
- Прогноз на 5 дней
- Данные Open-Meteo

## Локальный запуск

```bash
source .venv/bin/activate
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Затем на VPS:

```bash
curl http://127.0.0.1:8000/health
```
