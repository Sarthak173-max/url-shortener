import sqlite3, random, string
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, HttpUrl

app = FastAPI()
db = sqlite3.connect("links.db", check_same_thread=False)
db.execute("CREATE TABLE IF NOT EXISTS links "
           "(code TEXT PRIMARY KEY, url TEXT, clicks INTEGER DEFAULT 0)")

class LinkIn(BaseModel):
    url: HttpUrl          # refuses things that aren't real links

def make_code(n=6):
    return "".join(random.choices(string.ascii_letters + string.digits, k=n))

@app.post("/shorten")
def shorten(link: LinkIn):
    code = make_code()
    db.execute("INSERT INTO links (code, url) VALUES (?, ?)", (code, str(link.url)))
    db.commit()
    return {"short_url": f"http://127.0.0.1:8000/{code}"}

@app.get("/stats/{code}")
def stats(code: str):
    row = db.execute("SELECT url, clicks FROM links WHERE code=?", (code,)).fetchone()
    if not row:
        raise HTTPException(404, "Link not found")
    return {"url": row[0], "clicks": row[1]}

@app.get("/{code}")
def go(code: str):
    row = db.execute("SELECT url FROM links WHERE code=?", (code,)).fetchone()
    if not row:
        raise HTTPException(404, "Link not found")
    db.execute("UPDATE links SET clicks = clicks + 1 WHERE code=?", (code,))
    db.commit()
    return RedirectResponse(row[0])
