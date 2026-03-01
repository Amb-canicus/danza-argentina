import os
import json
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
import asyncio
from datetime import date

from scrapers import SCRAPERS_EVENTOS, SCRAPERS_NOTICIAS
from scrapers_convocatorias import SCRAPERS_CONVOCATORIAS
from utils import evento_es_proximo, deduplicar, mezclar, filtrar_recientes
import importlib, frontend

app = FastAPI()

BASE_URL = os.getenv("BASE_URL", "https://danza-argentina.up.railway.app")

# Servir archivos estáticos (og-image, fonts, etc.)
if os.path.isdir("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

eventos = []
noticias = []
convocatorias = []


NOTICIAS_RESPALDO = [
    {"titulo": "El Ballet Estable del Colón celebra 80 años", "descripcion": "La compañía más importante de danza clásica de Argentina cumple ocho décadas.", "tipo": "clásica", "fuente": "Telam", "url": "https://www.telam.com.ar", "fecha": "2026"},
    {"titulo": "Récord de inscriptos en el Festival de Malambo de Laborde", "descripcion": "El certamen folklórico más prestigioso del país recibió inscripciones de todo el país.", "tipo": "folklórica", "fuente": "Infobae", "url": "https://www.infobae.com", "fecha": "2026"},
    {"titulo": "Nueva generación de coreógrafos transforma la danza contemporánea", "descripcion": "Jóvenes artistas egresados del IUNA y el Colón llevan propuestas innovadoras.", "tipo": "contemporánea", "fuente": "La Nación", "url": "https://www.lanacion.com.ar", "fecha": "2026"},
]


# ─────────────────────────────────────────
#  DETECCIÓN DE BOTS / DYNAMIC RENDERING
# ─────────────────────────────────────────

BOT_USER_AGENTS = [
    "googlebot", "bingbot", "slurp", "duckduckbot", "baiduspider",
    "yandexbot", "applebot", "twitterbot", "linkedinbot",
    "whatsapp", "telegrambot", "discordbot", "facebot",
]

def es_bot(request: Request) -> bool:
    ua = request.headers.get("user-agent", "").lower()
    return any(bot in ua for bot in BOT_USER_AGENTS)

def generar_html_bot() -> str:
    """HTML semántico con contenido real para crawlers y redes sociales."""
    schema = {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": "Agenda de Danza en Buenos Aires",
        "numberOfItems": len(eventos),
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": i + 1,
                "item": {
                    "@type": "DanceEvent",
                    "name": ev["titulo"],
                    "description": ev.get("descripcion", ""),
                    "url": ev["url"],
                    "image": ev.get("imagen", ""),
                    "organizer": {"@type": "Organization", "name": ev["fuente"]},
                    "location": {
                        "@type": "Place",
                        "name": ev["fuente"],
                        "address": {
                            "@type": "PostalAddress",
                            "addressLocality": "Buenos Aires",
                            "addressCountry": "AR"
                        }
                    },
                    "eventStatus": "https://schema.org/EventScheduled",
                    "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode"
                }
            } for i, ev in enumerate(eventos[:20])
        ]
    }

    arts_ev = "".join(
        f'<article><h2><a href="{e["url"]}">{e["titulo"]}</a></h2>'
        f'<p>{e.get("descripcion", "")}</p>'
        f'<p>{e["fuente"]} — {e.get("fecha", "")}</p></article>'
        for e in eventos[:20]
    )
    arts_conv = "".join(
        f'<article><h2><a href="{c["url"]}">{c["titulo"]}</a></h2>'
        f'<p>{c.get("descripcion", "")}</p>'
        f'<p>{c.get("subtipo", "")} — {c["fuente"]}</p></article>'
        for c in convocatorias[:15]
    )
    arts_no = "".join(
        f'<article><h2><a href="{n["url"]}">{n["titulo"]}</a></h2>'
        f'<p>{n.get("descripcion", "")}</p>'
        f'<p>{n["fuente"]} — {n.get("fecha", "")}</p></article>'
        for n in noticias[:10]
    )

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>Agenda de Danza en Argentina | Ballet, Folklore y Contemporánea en Buenos Aires</title>
<meta name="description" content="La agenda más completa de danza en Argentina. Eventos de ballet, folklore, tango y contemporánea en Buenos Aires. Convocatorias, audiciones y becas.">
<meta name="robots" content="index, follow">
<link rel="canonical" href="{BASE_URL}/">
<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False)}</script>
</head>
<body>
<h1>Agenda de Danza en Argentina — Ballet, Folklore y Contemporánea en Buenos Aires</h1>
<section><h2>Eventos de Danza en Buenos Aires</h2>{arts_ev}</section>
<section><h2>Audiciones, Becas y Castings de Danza Argentina</h2>{arts_conv}</section>
<section><h2>Noticias de Danza en Argentina</h2>{arts_no}</section>
</body>
</html>"""


# ─────────────────────────────────────────
#  SCRAPING
# ─────────────────────────────────────────

async def scraper_loop():
    """Refresca los datos cada 24 horas en background."""
    while True:
        await asyncio.sleep(24 * 60 * 60)
        print("🔄 Refresco automático cada 24hs...")
        await scrape()

@app.on_event("startup")
async def startup():
    await scrape()
    asyncio.create_task(scraper_loop())

async def scrape():
    global eventos, noticias, convocatorias
    print(f"🩰 Iniciando scraping — {len(SCRAPERS_EVENTOS)} eventos, {len(SCRAPERS_NOTICIAS)} noticias, {len(SCRAPERS_CONVOCATORIAS)} convocatorias...")

    resultados_ev, resultados_no, resultados_conv = await asyncio.gather(
        asyncio.gather(*[s["fn"]() for s in SCRAPERS_EVENTOS],       return_exceptions=True),
        asyncio.gather(*[s["fn"]() for s in SCRAPERS_NOTICIAS],      return_exceptions=True),
        asyncio.gather(*[s["fn"]() for s in SCRAPERS_CONVOCATORIAS], return_exceptions=True),
    )

    for scraper, resultado in zip(SCRAPERS_EVENTOS, resultados_ev):
        estado = f"{len(resultado)} items" if isinstance(resultado, list) else str(resultado)
        print(f"  {'✅' if isinstance(resultado, list) else '❌'} {scraper['nombre']}: {estado}")

    for scraper, resultado in zip(SCRAPERS_NOTICIAS, resultados_no):
        estado = f"{len(resultado)} items" if isinstance(resultado, list) else str(resultado)
        print(f"  {'✅' if isinstance(resultado, list) else '❌'} {scraper['nombre']}: {estado}")

    for scraper, resultado in zip(SCRAPERS_CONVOCATORIAS, resultados_conv):
        estado = f"{len(resultado)} items" if isinstance(resultado, list) else str(resultado)
        print(f"  {'✅' if isinstance(resultado, list) else '❌'} {scraper['nombre']}: {estado}")

    listas_ev = [r for r in resultados_ev if isinstance(r, list)]

    todos_eventos  = mezclar(listas_ev)
    todas_noticias = mezclar([r[:10] for r in resultados_no if isinstance(r, list)])
    todas_conv     = mezclar([r for r in resultados_conv if isinstance(r, list)])

    eventos       = deduplicar(todos_eventos)[:50]
    noticias      = deduplicar(filtrar_recientes(todas_noticias, meses=2))[:50] or NOTICIAS_RESPALDO
    convocatorias = deduplicar(todas_conv)[:50]

    print(f"✅ {len(eventos)} eventos, {len(noticias)} noticias, {len(convocatorias)} convocatorias.")


# ─────────────────────────────────────────
#  API
# ─────────────────────────────────────────

@app.get("/api/eventos")
def get_eventos(tipo: str = ""):
    if tipo:
        return [e for e in eventos if e["tipo"] == tipo]
    return eventos

@app.get("/api/noticias")
def get_noticias(tipo: str = ""):
    if tipo:
        return [n for n in noticias if n["tipo"] == tipo]
    return noticias

@app.get("/api/convocatorias")
def get_convocatorias(subtipo: str = ""):
    if subtipo:
        return [c for c in convocatorias if c.get("subtipo") == subtipo]
    return convocatorias

@app.get("/api/refrescar")
async def refrescar():
    await scrape()
    return {"eventos": len(eventos), "noticias": len(noticias), "convocatorias": len(convocatorias)}


# ─────────────────────────────────────────
#  SEO
# ─────────────────────────────────────────

@app.get("/robots.txt")
def robots_txt():
    content = f"""User-agent: *
Allow: /
Disallow: /api/

Sitemap: {BASE_URL}/sitemap.xml
"""
    return Response(content=content, media_type="text/plain")

@app.get("/favicon.svg")
def favicon_svg():
    svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">
  <rect width="32" height="32" fill="#050505"/>
  <text x="50%" y="55%" font-family="serif" font-size="14" font-weight="bold"
        fill="#ff3c3c" text-anchor="middle" dominant-baseline="middle"
        font-style="italic">DA</text>
</svg>"""
    return Response(content=svg, media_type="image/svg+xml")

@app.get("/sitemap.xml")
def sitemap():
    hoy = date.today().isoformat()
    urls = [
        (f"{BASE_URL}/",              "1.0", "daily"),
        (f"{BASE_URL}/eventos",       "0.9", "daily"),
        (f"{BASE_URL}/tango",         "0.8", "daily"),
        (f"{BASE_URL}/convocatorias", "0.8", "daily"),
        (f"{BASE_URL}/prensa",        "0.7", "weekly"),
    ]
    tags = "".join(f"""
  <url>
    <loc>{loc}</loc>
    <lastmod>{hoy}</lastmod>
    <changefreq>{freq}</changefreq>
    <priority>{prio}</priority>
  </url>""" for loc, prio, freq in urls)
    content = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{tags}
</urlset>"""
    return Response(content=content, media_type="application/xml")


# ─────────────────────────────────────────
#  FRONTEND
# ─────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    if es_bot(request):
        return HTMLResponse(content=generar_html_bot())
    importlib.reload(frontend)
    html = frontend.HTML.replace("__BASE_URL__", BASE_URL)
    return HTMLResponse(content=html)
