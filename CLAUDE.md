# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Danza-app** is a FastAPI web scraping and content aggregation service for Argentine dance culture. It scrapes 15+ cultural institutions, aggregates events, news, and job postings (convocatorias), and serves both a REST API and an embedded single-page frontend.

Deployed at: `https://danza-argentina.up.railway.app`

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run the development server
uvicorn main:app --reload

# Run manual scraper debug scripts
python test_sitios.py
python test_convocatorias.py
```

There is no formal test framework, linting config, or build process. The debug scripts print HTML structure to inspect scraper output.

## Architecture

### Data Flow

On startup, FastAPI runs all scrapers in parallel via `asyncio.gather()`. Results are filtered, deduplicated, and stored in global variables (`eventos`, `noticias`, `convocatorias`). The API then serves this in-memory data until a restart or manual refresh (`GET /api/refrescar`).

```
Startup → parallel scrapers → filter/deduplicate → global state → API responses
Client → GET / → HTML (frontend.py) → JS fetches /api/* → renders cards
```

### Key Files

| File | Role |
|---|---|
| `main.py` | FastAPI app, startup event, API routes |
| `frontend.py` | Entire frontend as a Python string (HTML/CSS/JS) |
| `scrapers.py` | Events and news scrapers (9 sources) |
| `scrapers_convocatorias.py` | Job posting scrapers (4 sources) |
| `utils.py` | Keyword filtering, deduplication, text normalization |

Legacy files (`mainOLD.py`, `scrapersOLD.py`, `utilsOLD.py`) can be ignored.

### Scraper Registration Pattern

Scrapers use a decorator that auto-registers them into lists (`SCRAPERS_EVENTOS`, `SCRAPERS_NOTICIAS`, `SCRAPERS_CONVOCATORIAS`):

```python
@evento("Teatro Colón")
async def scrapear_teatro_colon():
    ...
    return items  # list of dicts
```

Each item dict has: `titulo`, `descripcion`, `tipo`, `fuente`, `url`, `fecha`. Convocatorias also include `subtipo` and `es_danza`.

### Content Classification

`utils.py` classifies content by dance discipline using keyword lists:
- `KEYWORDS_CLASICA`: ballet, clásico, Colón, ópera
- `KEYWORDS_FOLK`: folklórica, malambo, zamba, chacarera
- `KEYWORDS_CONTEMP`: contemporánea, moderno, experimental

Default classification falls back to `contemporánea`.

### Scraping Stack

The project uses layered HTTP/browser tools specifically to bypass bot detection:
- `Scrapling` + `curl-cffi`: Handle Cloudflare and bot detection
- `Playwright` / `Patchright`: JavaScript-heavy sites requiring headless browser
- `fetch_async()` in `utils.py`: Wraps synchronous fetching in a `ThreadPoolExecutor`

### Frontend

The entire frontend lives in `frontend.py` as a single HTML string with inline CSS and JavaScript. It features:
- Dark theme (black background, red accent `#ff3c3c`)
- Two views: "Eventos y Prensa" and "Convocatorias"
- Client-side filtering by discipline and convocation subtype
- Responsive 2-column → 1-column grid layout

### API Endpoints

- `GET /` — Serve the frontend HTML
- `GET /api/eventos?tipo=...` — Events filtered by dance type
- `GET /api/noticias?tipo=...` — News filtered by dance type
- `GET /api/convocatorias?subtipo=...` — Job postings filtered by subtype
- `GET /api/refrescar` — Manually re-run all scrapers
- `GET /sitemap.xml` — SEO sitemap

### Data Limits

- Events: max 50
- News: max 25
- Convocations: max 50
- Deduplication: by `title[:40]`
- Fallback data: hardcoded in `main.py` (`EVENTOS_RESPALDO`, `NOTICIAS_RESPALDO`)

## Adding a New Scraper

1. Add a new async function with the appropriate decorator (`@evento`, `@noticia`, or `@convocatoria`) in the relevant scrapers file.
2. Use `fetch_async(url)` from `utils.py` for HTTP requests.
3. Parse with BeautifulSoup and return a list of item dicts.
4. The decorator auto-registers it — no changes needed in `main.py`.
