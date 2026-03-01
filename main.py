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

BASE_URL = os.getenv("BASE_URL", "https://guilty-sheila-kathryn-danzig-0b1aa800.koyeb.app")

# Servir archivos estáticos (og-image, fonts, etc.)
if os.path.isdir("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

eventos = []
noticias = []
convocatorias = []


BASE_BORGES = "https://centroculturalborges.gob.ar"
# Hardcodeados porque Cloudflare bloquea la IP de Koyeb. Actualizar cada ~4 semanas.
# Última actualización: 2026-03-01
EVENTOS_BORGES_RESPALDO = [
    {"titulo": "QUE XOU DA XUXA É ESSE?", "descripcion": "En 1991 Leticia Mazur se presentó para ser Paquita de Xuxa, justo antes de la paranoia colectiva sobre mensajes satánicos en sus canciones. (+18)", "tipo": "contemporánea", "fuente": "CC Borges", "url": f"{BASE_BORGES}/disciplinas?d=danza", "fecha": "2026-03-01", "imagen": f"{BASE_BORGES}/uploads/1655c89e-9453-40ba-8577-70500ec5b305.jpg"},
    {"titulo": "Mi joven vida tiene un final", "descripcion": "Pablo Rotemberg dice ser Norma Desmond, mítica protagonista de Sunset Boulevard, la película dirigida por Billy Wilder en 1950.", "tipo": "contemporánea", "fuente": "CC Borges", "url": f"{BASE_BORGES}/disciplinas?d=danza", "fecha": "2026-03-05", "imagen": f"{BASE_BORGES}/uploads/c74eb6e3-4d10-496d-a5d5-f90e58e1e475.jpg"},
    {"titulo": "LA MAYOR", "descripcion": "Una aventura híbrida entre la vibración sensorial de las palabras, y el extravío delirante de la literatura.", "tipo": "contemporánea", "fuente": "CC Borges", "url": f"{BASE_BORGES}/disciplinas?d=danza", "fecha": "2026-03-07", "imagen": f"{BASE_BORGES}/uploads/f05e91da-bea0-4e13-ae3f-a555c80b35cc.jpg"},
    {"titulo": "EXPERIMENTA#03. DANZA + ARTES VISUALES", "descripcion": "Una nueva edición del ciclo que propone el encuentro entre un/a coreógrafo/a y un/a artista visual para crear una obra en cruce donde el tiempo y el espacio se vuelven materia viva.", "tipo": "contemporánea", "fuente": "CC Borges", "url": f"{BASE_BORGES}/disciplinas?d=danza", "fecha": "2026-04-03", "imagen": f"{BASE_BORGES}/uploads/8bd841cc-c202-4694-b289-655fd067fd63.jpg"},
    {"titulo": "EXPERIMENTA#03. Cruza koi", "descripcion": "Un apareo de dudas entre perra y pez koi, al ritmo de un salto de agua. Interferencias, inquietudes y obviedades jadeantes a contracorriente.", "tipo": "contemporánea", "fuente": "CC Borges", "url": f"{BASE_BORGES}/disciplinas?d=danza", "fecha": "2026-04-03", "imagen": f"{BASE_BORGES}/uploads/37773da7-30d6-4136-b2a5-1bfd011b4da2.jpg"},
    {"titulo": "EXPERIMENTA#03. MUEVE MONTAÑAS", "descripcion": "Un monólogo-performance donde escultura y texto se funden en una montaña de relatos y materiales.", "tipo": "contemporánea", "fuente": "CC Borges", "url": f"{BASE_BORGES}/disciplinas?d=danza", "fecha": "2026-04-10", "imagen": f"{BASE_BORGES}/uploads/274fd1ab-c7d6-41a8-83b5-f2d670e719fa.jpg"},
    {"titulo": "Experimenta#03. Instalación Eléctrica #1", "descripcion": "La sala se convierte en un organismo bio-electromecánico donde luz, sonido y cuerpo generan un cortocircuito poético en tiempo real.", "tipo": "contemporánea", "fuente": "CC Borges", "url": f"{BASE_BORGES}/disciplinas?d=danza", "fecha": "2026-04-17", "imagen": f"{BASE_BORGES}/uploads/ba92b293-d832-4749-ac13-783489996583.jpg"},
    {"titulo": "Experimenta#03. Formas breves", "descripcion": "Un campo de investigación entre escultura y danza, donde cuerpo y materia se conciben como sistemas relacionales en constante negociación.", "tipo": "contemporánea", "fuente": "CC Borges", "url": f"{BASE_BORGES}/disciplinas?d=danza", "fecha": "2026-04-24", "imagen": f"{BASE_BORGES}/uploads/4723e5f0-fb55-40a2-9d08-7ebdfa332498.jpg"},
]

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
    # Scraping en background para no bloquear el startup (evita OOM en servidores con poca RAM)
    asyncio.create_task(scrape())
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

    # Agregar eventos hardcodeados de CC Borges filtrando los ya vencidos
    hoy = date.today()
    borges_vigentes = [
        e for e in EVENTOS_BORGES_RESPALDO
        if date.fromisoformat(e["fecha"]) >= hoy
    ]
    if borges_vigentes:
        listas_ev.append(borges_vigentes)
        print(f"  ✅ CC Borges (respaldo): {len(borges_vigentes)} items")

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
