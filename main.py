import os
import re
import time
from urllib.parse import urlparse

from bs4 import BeautifulSoup
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import requests

app = FastAPI(
    title="URL Auditor API",
    description="Task 1: Web page auditing tool",
    version="1.0.0",
)

# Safely create the static directory if it does not exist on the host server
if not os.path.exists("static"):
    os.makedirs("static", exist_ok=True)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


class AuditRequest(BaseModel):
    url: str


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Serves the frontend URL audit interface."""
    return templates.TemplateResponse(
        request=request, name="index.html", context={"title": "URL Audit Tool"}
    )


@app.post("/api/audit")
async def audit_url(payload: AuditRequest):
    """Fetches target page, measures metrics, parses HTML SEO elements,"""
    """and handles edge cases cleanly."""
    target_url = payload.url.strip()

    # 1. Normalize and Validate URL Scheme
    if not target_url.startswith(("http://", "https://")):
        target_url = "https://" + target_url

    parsed_url = urlparse(target_url)
    if not parsed_url.netloc:
        return JSONResponse(
            status_code=400,
            content={
                "error": "Invalid URL structure. Please provide a valid web address."
            },
        )

    # 2. Fetch the Webpage with Safety Settings
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36 AuditBot/1.0"
        )
    }

    start_time = time.time()
    try:
        response = requests.get(
            target_url, headers=headers, timeout=10, allow_redirects=True
        )
        response_time_ms = round((time.time() - start_time) * 1000)
    except requests.exceptions.Timeout:
        return JSONResponse(
            status_code=504,
            content={
                "error": "Request timed out after 10 seconds. The server took too long to respond."
            },
        )
    except requests.exceptions.ConnectionError:
        return JSONResponse(
            status_code=523,
            content={
                "error": "Could not connect to the server. Check the URL or server availability."
            },
        )
    except requests.exceptions.RequestException as e:
        return JSONResponse(
            status_code=400,
            content={"error": f"Failed to retrieve URL: {type(e).__name__}"},
        )

    # 3. Validate Content Type (Ensure response is HTML)
    content_type = response.headers.get("Content-Type", "").lower()
    if "text/html" not in content_type:
        return JSONResponse(
            status_code=415,
            content={
                "error": f"Non-HTML response detected ({content_type.split(';')[0] or 'unknown'}). Auditing only supports HTML pages."
            },
        )

    # 4. Parse Document & Extract Audit Metrics
    try:
        soup = BeautifulSoup(response.text, "html.parser")

        # Page Title
        title_tag = soup.find("title")
        page_title = (
            title_tag.string.strip()
            if title_tag and title_tag.string
            else "N/A (Missing <title> tag)"
        )

        # Meta Description
        meta_desc_tag = soup.find(
            "meta", attrs={"name": re.compile(r"^description$", re.I)}
        )
        meta_description = (
            meta_desc_tag.get("content", "").strip()
            if meta_desc_tag and meta_desc_tag.get("content")
            else "N/A (Missing meta description)"
        )

        # H1 Tag Count
        h1_count = len(soup.find_all("h1"))

        # Images Missing Alt Text
        images = soup.find_all("img")
        images_missing_alt = sum(
            1 for img in images if not img.get("alt") or not img.get("alt").strip()
        )

        # Approximate Word Count
        for element in soup(
            ["script", "style", "noscript", "header", "footer", "nav"]
        ):
            element.extract()
        visible_text = soup.get_text(separator=" ")
        words = re.findall(r"\w+", visible_text)
        word_count = len(words)

        return {
            "url": response.url,
            "status_code": response.status_code,
            "response_time_ms": response_time_ms,
            "page_title": page_title,
            "meta_description": meta_description,
            "h1_count": h1_count,
            "total_images": len(images),
            "images_missing_alt": images_missing_alt,
            "word_count": word_count,
        }

    except Exception as parse_error:
        return JSONResponse(
            status_code=500,
            content={
                "error": f"Failed to parse HTML document structure: {str(parse_error)}"
            },
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)