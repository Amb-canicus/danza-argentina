"""
test_imagenes.py
Verifica qué fuentes exponen imágenes scrapeables.
Corre en http://127.0.0.1:8001
"""

import asyncio
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup
from scrapling.fetchers import StealthyFetcher
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn

executor = ThreadPoolExecutor(max_workers=6)

FUENTES = [
    # (nombre, url, categoría, selectores de contenedores donde buscar img)
    ("Teatro Colón",          "https://teatrocolon.org.ar/categoria-produccion/ballet/",                          "evento",        ["article", ".produccion", ".post"]),
    ("Teatro San Martín",     "https://complejoteatral.gob.ar/ver/danza",                                         "evento",        ["article", ".show", ".card"]),
    ("Palacio Libertad",      "https://palaciolibertad.gob.ar/agenda/",                                           "evento",        ["article", ".card"]),
    ("CC Borges",             "https://centroculturalborges.gob.ar/disciplinas?d=danza",                          "evento",        ["article", ".card", "li"]),
    ("Usina del Arte",        "https://usinadelarte.ar/actividades/",                                             "evento",        ["article", ".card", ".actividad"]),
    ("CC Recoleta",           "http://centroculturalrecoleta.org/agenda",                                         "evento",        ["article", "li"]),
    ("BA Ciudad",             "https://buenosaires.gob.ar/descubrir/agenda-2026",                                 "evento",        ["article", ".card"]),
    ("CIAD",                  "https://www.laciad.info/todos-los-eventos.html",                                   "evento",        ["article", ".card", "figure"]),
    ("Alternativa Teatral",   "http://www.alternativateatral.com/buscar.asp?objetivo=obras&texto=danza",          "evento",        ["li", "article"]),
    ("Balletín Dance",        "https://balletindance.com/",                                                       "noticia",       ["article", ".post", "figure"]),
    ("Perfil",                "https://noticias.perfil.com/seccion/danza",                                        "noticia",       ["article", ".nota", ".story"]),
    ("Clarín",                "https://www.clarin.com/espectaculos/teatro/",                                      "noticia",       ["article", ".story"]),
    ("Recursos Culturales",   "https://www.recursosculturales.com/tag/danza/",                                    "convocatoria",  ["article"]),
    ("Alt Teatral Castings",  "http://www.alternativateatral.com/convocatorias.php?pais=1&clasificacion=14",      "convocatoria",  ["li", "article"]),
]

COLORES = {"evento": "#2a6496", "noticia": "#4a7c3f", "convocatoria": "#7c4a3f"}


def fetch_sync(url):
    return StealthyFetcher.fetch(url, headless=True, network_idle=True)

async def fetch_async(url):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, fetch_sync, url)


def extraer_imagen(soup, url_base, selectores):
    """Intenta extraer la URL de imagen por múltiples estrategias."""

    # 1. og:image (la más confiable)
    og = soup.find("meta", property="og:image") or soup.find("meta", attrs={"name": "og:image"})
    if og and og.get("content"):
        return og["content"], "og:image"

    # 2. Primer img dentro de los contenedores típicos de tarjetas
    for sel in selectores:
        for container in soup.select(sel)[:5]:
            img = container.find("img")
            if img:
                src = img.get("src") or img.get("data-src") or img.get("data-lazy-src") or img.get("srcset", "").split(" ")[0]
                if src and len(src) > 4 and not src.startswith("data:"):
                    if src.startswith("//"):
                        src = "https:" + src
                    elif src.startswith("/"):
                        from urllib.parse import urlparse
                        p = urlparse(url_base)
                        src = f"{p.scheme}://{p.netloc}{src}"
                    return src, f"img en {sel}"

    # 3. Cualquier img en la página
    for img in soup.find_all("img")[:10]:
        src = img.get("src") or img.get("data-src") or img.get("data-lazy-src")
        if src and len(src) > 4 and not src.startswith("data:") and not "logo" in src.lower() and not "icon" in src.lower():
            if src.startswith("//"):
                src = "https:" + src
            elif src.startswith("/"):
                from urllib.parse import urlparse
                p = urlparse(url_base)
                src = f"{p.scheme}://{p.netloc}{src}"
            return src, "img genérico"

    return None, None


async def testear_fuente(nombre, url, categoria, selectores):
    try:
        page = await fetch_async(url)
        soup = BeautifulSoup(page.html_content, "html.parser")
        total_imgs = len(soup.find_all("img"))
        img_url, metodo = extraer_imagen(soup, url, selectores)
        return {
            "nombre": nombre,
            "url": url,
            "categoria": categoria,
            "ok": img_url is not None,
            "img_url": img_url,
            "metodo": metodo,
            "total_imgs": total_imgs,
            "error": None,
        }
    except Exception as e:
        return {
            "nombre": nombre,
            "url": url,
            "categoria": categoria,
            "ok": False,
            "img_url": None,
            "metodo": None,
            "total_imgs": 0,
            "error": str(e)[:120],
        }


def render_html(resultados):
    con_img  = sum(1 for r in resultados if r["ok"])
    sin_img  = len(resultados) - con_img

    tarjetas = ""
    for r in resultados:
        color = COLORES.get(r["categoria"], "#555")
        estado_color = "#2ecc71" if r["ok"] else "#e74c3c"
        estado_texto = f"✅ {r['metodo']}" if r["ok"] else ("❌ Error" if r["error"] else "❌ Sin imagen")
        preview = f'<img src="{r["img_url"]}" onerror="this.style.display=\'none\'" style="width:100%;height:160px;object-fit:cover;border-radius:6px;margin-bottom:12px;">' if r["img_url"] else '<div style="width:100%;height:160px;background:#1a1a1a;border-radius:6px;margin-bottom:12px;display:flex;align-items:center;justify-content:center;color:#444;font-size:2rem;">🖼</div>'
        error_txt = f'<p style="color:#e74c3c;font-size:0.72rem;margin-top:6px">{r["error"]}</p>' if r["error"] else ""
        tarjetas += f"""
        <div style="background:#111;border-radius:10px;padding:16px;border:1px solid #222;">
            {preview}
            <div style="font-size:0.6rem;text-transform:uppercase;letter-spacing:2px;color:{color};margin-bottom:4px;">{r["categoria"]}</div>
            <div style="font-weight:700;font-size:0.95rem;margin-bottom:6px;">{r["nombre"]}</div>
            <div style="font-size:0.75rem;color:{estado_color};margin-bottom:4px;">{estado_texto}</div>
            <div style="font-size:0.7rem;color:#555;">{r["total_imgs"]} imgs en página</div>
            {error_txt}
            <a href="{r["url"]}" target="_blank" style="font-size:0.65rem;color:#555;word-break:break-all;">{r["url"][:60]}…</a>
        </div>"""

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>Test de imágenes — Danza-app</title>
<style>
  * {{ box-sizing:border-box; margin:0; padding:0 }}
  body {{ background:#050505; color:#fff; font-family: sans-serif; padding: 2rem; }}
  h1 {{ font-size:1.6rem; margin-bottom:0.4rem; }}
  .resumen {{ color:#888; font-size:0.9rem; margin-bottom:2rem; }}
  .resumen span {{ color:#2ecc71; font-weight:700; }}
  .resumen span.mal {{ color:#e74c3c; }}
  .grid {{ display:grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap:16px; }}
</style>
</head>
<body>
  <h1>🖼 Test de imágenes</h1>
  <p class="resumen">
    <span>{con_img}</span> fuentes con imagen &nbsp;·&nbsp;
    <span class="mal">{sin_img}</span> sin imagen &nbsp;·&nbsp;
    {len(resultados)} fuentes en total
  </p>
  <div class="grid">{tarjetas}</div>
</body>
</html>"""


app = FastAPI()
resultados_cache = []

@app.on_event("startup")
async def startup():
    global resultados_cache
    print("🔍 Testeando imágenes en todas las fuentes...")
    tareas = [testear_fuente(n, u, c, s) for n, u, c, s in FUENTES]
    resultados_cache = list(await asyncio.gather(*tareas))
    con = sum(1 for r in resultados_cache if r["ok"])
    print(f"✅ {con}/{len(resultados_cache)} fuentes tienen imágenes.")

@app.get("/", response_class=HTMLResponse)
def index():
    return render_html(resultados_cache)

@app.get("/refrescar", response_class=HTMLResponse)
async def refrescar():
    await startup()
    return render_html(resultados_cache)

if __name__ == "__main__":
    uvicorn.run("test_imagenes:app", host="127.0.0.1", port=8001, reload=False)
