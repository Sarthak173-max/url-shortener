from fastapi.testclient import TestClient
from main import app, limiter

client = TestClient(app)

def setup_function():
    limiter.reset()          # clear the rate-limit counter before each test

def test_home_page_loads():
    r = client.get("/")
    assert r.status_code == 200

def test_shorten_and_redirect():
    r = client.post("/shorten", json={"url": "https://example.com"})
    assert r.status_code == 200
    code = r.json()["short_url"].split("/")[-1]
    r2 = client.get(f"/{code}", follow_redirects=False)
    assert r2.status_code in (302, 307)

def test_bad_link_rejected():
    r = client.post("/shorten", json={"url": "not a link"})
    assert r.status_code == 422

def test_custom_code_taken():
    client.post("/shorten", json={"url": "https://example.com", "custom_code": "testdup"})
    r = client.post("/shorten", json={"url": "https://example.com", "custom_code": "testdup"})
    assert r.status_code == 409

def test_expired_link():
    client.post("/shorten", json={"url": "https://example.com",
                                  "custom_code": "testold", "expires_in_days": -1})
    r = client.get("/testold", follow_redirects=False)
    assert r.status_code == 410

def test_rate_limit():
    codes = [client.post("/shorten", json={"url": "https://example.com"}).status_code
             for _ in range(12)]
    assert 429 in codes