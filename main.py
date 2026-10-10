import sqlite3, random, string
from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse, FileResponse
from pydantic import BaseModel, HttpUrl
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

app = FastAPI()
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

db = sqlite3.connect("links.db", check_same_thread=False)
db.execute("CREATE TABLE IF NOT EXISTS links "
           "(code TEXT PRIMARY KEY, url TEXT, clicks INTEGER DEFAULT 0, expires_at TEXT)")

class LinkIn(BaseModel):
    url: HttpUrl
    custom_code: Optional[str] = None
    expires_in_days: Optional[int] = None

def now():
    # current UTC time, in the same format we stored before
    return datetime.now(timezone.utc).replace(tzinfo=None)

def make_code(n=6):
    return "".join(random.choices(string.ascii_letters + string.digits, k=n))

def code_exists(code):
    return db.execute("SELECT 1 FROM links WHERE code=?", (code,)).fetchone() is not None

@app.get("/")
def home():
    return FileResponse("index.html")

@app.post("/shorten")
@limiter.limit("10/minute")
def shorten(request: Request, link: LinkIn):
    if link.custom_code:
        code = link.custom_code
        if code in ("shorten", "stats", "docs", "openapi.json"):
            raise HTTPException(400, "That nickname is reserved")
        if code_exists(code):
            raise HTTPException(409, "That nickname is already taken")
    else:
        code = make_code()
        while code_exists(code):
            code = make_code()

    expires_at = None
    if link.expires_in_days:
        expires_at = (now() + timedelta(days=link.expires_in_days)).isoformat()

    db.execute("INSERT INTO links (code, url, expires_at) VALUES (?, ?, ?)",
               (code, str(link.url), expires_at))
    db.commit()
    return {"short_url": f"http://127.0.0.1:8000/{code}", "expires_at": expires_at}

@app.get("/stats/{code}")
def stats(code: str):
    row = db.execute("SELECT url, clicks, expires_at FROM links WHERE code=?", (code,)).fetchone()
    if not row:
        raise HTTPException(404, "Link not found")
    return {"url": row[0], "clicks": row[1], "expires_at": row[2]}

@app.get("/{code}")
def go(code: str):
    row = db.execute("SELECT url, expires_at FROM links WHERE code=?", (code,)).fetchone()
    if not row:
        raise HTTPException(404, "Link not found")
    if row[1] and now() > datetime.fromisoformat(row[1]):
        raise HTTPException(410, "This link has expired")
    db.execute("UPDATE links SET clicks = clicks + 1 WHERE code=?", (code,))
    db.commit()
    return RedirectResponse(row[0])