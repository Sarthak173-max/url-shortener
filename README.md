# Link Shortener

A fast URL shortener built with FastAPI. Turn long links into short ones, track clicks, set expiry dates, and protect the service with rate limiting.

**Live demo:** https://url-shortener-laog.onrender.com
**API docs:** https://url-shortener-laog.onrender.com/docs

> The demo runs on a free plan, so the first visit after idle time may take about a minute to wake up.

## Features

- Shorten any valid link into a 6-character code
- Custom nicknames (for example `/mybook`) with duplicate checking
- Optional link expiry (returns `410 Gone` after the date)
- Click counter and stats endpoint
- Rate limiting: 10 new links per minute per user (`429` when exceeded)
- Input validation, so invalid links are rejected
- Simple web page for non-technical users
- Automated tests with pytest

## Tech Stack

Python, FastAPI, SQLite, Pydantic, SlowAPI, Pytest, HTML/CSS/JavaScript, Git, Render

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/shorten` | Create a short link |
| GET | `/{code}` | Redirect to the original link |
| GET | `/stats/{code}` | View click count and expiry |
| GET | `/` | Web page |

Example request:

```json
POST /shorten
{
  "url": "https://www.wikipedia.org",
  "custom_code": "wiki",
  "expires_in_days": 7
}
```

## Run Locally

```bash
git clone https://github.com/Sarthak173-max/url-shortener.git
cd url-shortener
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Open http://127.0.0.1:8000

## Run Tests

```bash
python -m pytest
```

## What I Learned

- Designing a REST API with validation and proper status codes (200, 409, 410, 422, 429)
- Working with a database, unique constraints, and expiry logic
- Rate limiting to protect a public service
- Writing automated tests and deploying a live app

## Future Improvements

- Switch to PostgreSQL for permanent storage
- Click analytics by device and country
- Redis caching
- Docker and CI with GitHub Actions