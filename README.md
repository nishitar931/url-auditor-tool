#  Page Pulser — Web Page Audit Tool

**Page Pulser** is a full-stack, lightweight web auditing platform built with **FastAPI** and **BeautifulSoup4**. It accepts any web page URL, inspects its HTTP health and performance, parses critical SEO elements, and calculates content metrics in real-time.

---

##  Features

-  **HTTP & Performance Tracking:** Measures server status codes and fetch response latecy in milliseconds.
-  **SEO & HTML Analysis:** Extracts `<title>` tags, meta descriptions, and evaluates `<h1>` heading counts.
-  **Accessibility Auditing:** Scans all embedded `<img>` tags to identify images missing necessary `alt` text.
-  **Clean Word Count Calculation:** Strips out non-body script, style, navigation, and header/footer elements to compute accurate visible text length.
-  **Resilient Error Handling:** Prevents crashes by safely managing invalid URL structures, connection timeouts, and non-HTML payloads (e.g., direct JSON, PDF, or image files).
-  **Modern Glassmorphic UI:** Features dynamic status badges, smooth entry animations, metric indicators, and real-time state management.

---

## Tech Stack

- **Backend:** Python 3.10+, FastAPI, BeautifulSoup4, Requests, Pydantic
- **Frontend:** Jinja2 Templates, Modern CSS3 (Variables, Flexbox, CSS Grid, Glassmorphism), JavaScript (Fetch API)
- **Testing:** Pytest, FastAPI TestClient, Unittest Mock
- **Deployment:** Render / Cloud Web Services

---

##  Repository Structure

```text
url-auditor-tool/
├── main.py              # FastAPI application server and parsing engine
├── test_main.py         # Pytest test suite (happy path & failure cases)
├── requirements.txt     # Python dependencies
├── README.md            # Project documentation
├── static/              # Static assets and .gitkeep
└── templates/
    └── index.html       # Page Pulser frontend user interface