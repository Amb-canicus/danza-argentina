"""
test_cards.py
Genera un HTML con las tarjetas reales de la app + imágenes y lo abre en el browser.
Uso: python test_cards.py
"""

import asyncio
import httpx
import webbrowser
import tempfile
from collections import Counter
from bs4 import BeautifulSoup

MUESTRA = 100
API = "http://127.0.0.1:8000"
FUENTES_SIN_IMAGEN = {"Recursos Culturales"}
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "es-AR,es;q=0.9",
}

# Razones posibles: "og:image", "img_tag", "necesita_js", "sin_imagen", "error_http", "url_listado"

async def fetch_og_image(url: str, client: httpx.AsyncClient) -> tuple[str | None, str]:
    try:
        chunks = []
        async with client.stream("GET", url, headers=HEADERS, timeout=8, follow_redirects=True) as r:
            if r.status_code >= 400:
                return (None, "error_http")
            async for chunk in r.aiter_bytes(4096):
                chunks.append(chunk)
                if b"</head>" in b"".join(chunks).lower():
                    break
                if len(chunks) > 20:
                    break

        html = b"".join(chunks).decode("utf-8", errors="ignore")

        if len(html) < 500:
            return (None, "necesita_js")

        soup = BeautifulSoup(html, "html.parser")

        og = soup.find("meta", property="og:image") or soup.find("meta", attrs={"name": "twitter:image"})
        if og and og.get("content"):
            return (og["content"], "og:image")

        for img in soup.find_all("img", src=True):
            src = img["src"]
            if not src or src.startswith("data:"):
                continue
            if any(x in src.lower() for x in ["logo", "icon", "avatar", "pixel", "track"]):
                continue
            if src.startswith("//"):
                src = "https:" + src
            if src.startswith("http"):
                return (src, "img_tag")

        return (None, "sin_imagen")

    except Exception:
        return (None, "error_http")


def marcar_no_aplica(items):
    for item in items:
        item.setdefault("imagen", None)
        item["img_razon"] = "no_aplica"
    return items


async def enriquecer(items, client, url_counts):
    sem = asyncio.Semaphore(25)

    async def fetch_con_sem(item):
        async with sem:
            # Imagen ya provista por el scraper (ej: CC Borges)
            if item.get("imagen"):
                item["img_razon"] = "directo"
                return item
            # Fuentes que no necesitan imagen
            if item.get("fuente") in FUENTES_SIN_IMAGEN:
                item["img_razon"] = "no_aplica"
                return item
            url = item["url"]
            if url_counts[url] >= 2:
                item["imagen"] = None
                item["img_razon"] = "url_listado"
            else:
                img_url, razon = await fetch_og_image(url, client)
                item["imagen"] = img_url
                item["img_razon"] = razon
        return item

    return await asyncio.gather(*[fetch_con_sem(i) for i in items])


BADGE_COLORS = {
    "url_listado": "#e67e22",   # naranja
    "necesita_js": "#c0392b",   # rojo
    "sin_imagen":  "#2980b9",   # azul
    "error_http":  "#555",      # gris
}

def card(item, es_conv=False):
    if item.get("imagen"):
        img_html = f'<img src="{item["imagen"]}" onerror="this.style.display=\'none\';this.nextElementSibling.style.display=\'flex\'" class="card-img"><div class="card-img placeholder" style="display:none"><p class="ph-titulo">{item.get("titulo","")[:80]}</p></div>'
    else:
        razon = item.get("img_razon", "sin_imagen")
        titulo_ph = item.get("titulo", "")[:80]
        badge = ""
        if razon in ("url_listado", "necesita_js"):
            color = BADGE_COLORS.get(razon, "#555")
            badge = f'<span class="ph-badge" style="background:{color}">{razon}</span>'
        img_html = f'<div class="card-img placeholder">{badge}<p class="ph-titulo">{titulo_ph}</p></div>'

    tag = item.get("subtipo", "convocatoria") if es_conv else item.get("tipo", "")
    fecha = item.get("fecha", "")
    return f"""
    <div class="card">
        {img_html}
        <div class="card-body">
            <span class="tag">{tag}</span>
            <h3><a href="{item['url']}" target="_blank">{item['titulo']}</a></h3>
            <p>{item.get('descripcion','')[:180]}</p>
            <div class="meta"><span>{item.get('fuente','')}</span><span>{fecha}</span></div>
        </div>
    </div>"""


def stats_table(todos):
    """Genera tabla HTML de stats por fuente."""
    fuentes = {}
    for item in todos:
        f = item.get("fuente", "—")
        if f not in fuentes:
            fuentes[f] = {"con": 0, "sin": 0}
        if item.get("imagen"):
            fuentes[f]["con"] += 1
        else:
            fuentes[f]["sin"] += 1

    filas = ""
    for fuente, s in sorted(fuentes.items()):
        total = s["con"] + s["sin"]
        pct = int(s["con"] / total * 100) if total else 0
        bar = f'<div class="pct-bar" style="width:{pct}%"></div>'
        filas += f"""<tr>
            <td>{fuente}</td>
            <td class="num">{s['con']}</td>
            <td class="num">{s['sin']}</td>
            <td class="num">{total}</td>
            <td class="pct-cell">{bar}<span>{pct}%</span></td>
        </tr>"""

    return f"""
    <table class="stats-table">
        <thead><tr>
            <th>Fuente</th><th>Con img</th><th>Sin img</th><th>Total</th><th>Cobertura</th>
        </tr></thead>
        <tbody>{filas}</tbody>
    </table>"""


def seccion_por_fuente(items, es_conv=False):
    """Agrupa items por fuente y devuelve HTML con una sección por fuente."""
    grupos = {}
    for item in items:
        f = item.get("fuente", "—")
        grupos.setdefault(f, []).append(item)

    html = ""
    for fuente in sorted(grupos.keys()):
        grupo = grupos[fuente]
        con_img = sum(1 for i in grupo if i.get("imagen"))
        cards_html = "".join(card(i, es_conv=es_conv) for i in grupo)
        html += f"""
        <h3 class="fuente-header">{fuente}
            <span>{con_img}/{len(grupo)} con imagen</span>
        </h3>
        <div class="grid">{cards_html}</div>"""
    return html


def render(eventos, noticias, convocatorias):
    todos = list(eventos) + list(noticias) + list(convocatorias)
    total = len(todos)
    total_img = sum(1 for i in todos if i.get("imagen"))

    tabla = stats_table(todos)
    e_html = seccion_por_fuente(eventos)
    n_html = seccion_por_fuente(noticias)
    c_html = seccion_por_fuente(convocatorias, es_conv=True)

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>Test cards — Danza Argentina</title>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;700&family=Playfair+Display:ital,wght@0,900;1,900&display=swap" rel="stylesheet">
<style>
:root {{ --bg:#050505; --card:#111; --accent:#ff3c3c; --border:rgba(255,255,255,0.08); --text:#fff; --dim:#888; }}
* {{ box-sizing:border-box; margin:0; padding:0 }}
body {{ background:var(--bg); color:var(--text); font-family:'Plus Jakarta Sans',sans-serif; padding:2rem; }}
h1 {{ font-family:'Playfair Display',serif; font-style:italic; color:var(--accent); font-size:2rem; margin-bottom:.3rem }}
.sub {{ color:var(--dim); font-size:.85rem; margin-bottom:2rem }}
h2 {{ font-family:'Playfair Display',serif; font-size:1.4rem; border-bottom:1px solid var(--accent);
      padding-bottom:.6rem; margin:2.5rem 0 1rem; display:flex; justify-content:space-between }}
h2 span {{ font-size:.75rem; color:var(--accent); font-family:'Plus Jakarta Sans',sans-serif; font-style:normal }}
h3.fuente-header {{ font-size:.95rem; color:var(--dim); border-bottom:1px solid var(--border);
      padding-bottom:.4rem; margin:1.5rem 0 .8rem; display:flex; justify-content:space-between }}
h3.fuente-header span {{ font-size:.75rem; color:#555 }}
.grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(280px,1fr)); gap:16px }}
.card {{ background:var(--card); border-radius:10px; overflow:hidden; border:1px solid var(--border);
         transition:transform .2s; display:flex; flex-direction:column }}
.card:hover {{ transform:translateY(-3px) }}
.card-img {{ width:100%; height:180px; object-fit:cover; display:block; background:#1a1a1a }}
.placeholder {{ width:100%; height:180px; background:linear-gradient(160deg,#0c0c0c 0%,#150404 100%);
                border-left:2px solid rgba(255,60,60,.4);
                display:flex; flex-direction:column; justify-content:flex-end;
                padding:1rem; position:relative; overflow:hidden; box-sizing:border-box }}
.placeholder::before {{ content:''; position:absolute; bottom:-30px; right:-30px;
                         width:120px; height:120px; border-radius:50%;
                         border:1px solid rgba(255,60,60,.07) }}
.ph-titulo {{ font-family:'Playfair Display',serif; font-style:italic;
              color:rgba(255,255,255,.18); font-size:1.05rem; line-height:1.35; margin:0;
              overflow:hidden; display:-webkit-box; -webkit-line-clamp:3; -webkit-box-orient:vertical }}
.ph-badge {{ position:absolute; top:.55rem; right:.55rem; font-size:.5rem; font-weight:700;
             padding:.1rem .35rem; border-radius:3px; color:rgba(255,255,255,.5);
             text-transform:lowercase; letter-spacing:.4px }}
.card-body {{ padding:1rem; flex:1; display:flex; flex-direction:column; gap:.4rem }}
.tag {{ font-size:.6rem; font-weight:700; text-transform:uppercase; color:var(--accent); letter-spacing:1px }}
.card-body h3 {{ font-size:1rem; line-height:1.35 }}
.card-body h3 a {{ color:var(--text); text-decoration:none }}
.card-body h3 a:hover {{ color:var(--accent) }}
.card-body p {{ color:var(--dim); font-size:.8rem; line-height:1.5; flex:1 }}
.meta {{ display:flex; justify-content:space-between; font-size:.68rem; color:#444;
         margin-top:auto; padding-top:.5rem; border-top:1px solid var(--border) }}
/* Stats table */
.stats-table {{ width:100%; border-collapse:collapse; font-size:.82rem; margin-bottom:2.5rem;
                background:var(--card); border-radius:10px; overflow:hidden; border:1px solid var(--border) }}
.stats-table th {{ background:#1a1a1a; color:var(--dim); font-weight:600; padding:.55rem 1rem;
                   text-align:left; font-size:.72rem; text-transform:uppercase; letter-spacing:.5px }}
.stats-table td {{ padding:.5rem 1rem; border-top:1px solid var(--border); vertical-align:middle }}
.stats-table tr:hover td {{ background:#151515 }}
.num {{ text-align:center; color:var(--dim) }}
.pct-cell {{ display:flex; align-items:center; gap:.5rem; width:160px }}
.pct-bar {{ height:6px; background:var(--accent); border-radius:3px; min-width:2px }}
.pct-cell span {{ font-size:.72rem; color:var(--dim); white-space:nowrap }}
</style>
</head>
<body>
  <h1>Danza Argentina</h1>
  <p class="sub">{total_img}/{total} ítems con imagen &nbsp;·&nbsp;
     Eventos {sum(1 for i in eventos if i.get('imagen'))}/{len(eventos)} &nbsp;·&nbsp;
     Noticias {sum(1 for i in noticias if i.get('imagen'))}/{len(noticias)} &nbsp;·&nbsp;
     Convocatorias {sum(1 for i in convocatorias if i.get('imagen'))}/{len(convocatorias)}</p>

  {tabla}

  <h2>Eventos <span>{len(eventos)} ítems</span></h2>
  {e_html}

  <h2>Noticias <span>{len(noticias)} ítems</span></h2>
  {n_html}

  <h2>Convocatorias <span>{len(convocatorias)} ítems</span></h2>
  {c_html}
</body>
</html>"""


async def main():
    print("📥 Obteniendo datos de la API...")
    async with httpx.AsyncClient(timeout=30) as local:
        ev_r, no_r, co_r = await asyncio.gather(
            local.get(f"{API}/api/eventos"),
            local.get(f"{API}/api/noticias"),
            local.get(f"{API}/api/convocatorias"),
        )
    eventos       = ev_r.json()[:MUESTRA]
    noticias      = no_r.json()[:MUESTRA]
    convocatorias = co_r.json()[:MUESTRA]
    print(f"   {len(eventos)} eventos, {len(noticias)} noticias, {len(convocatorias)} convocatorias")

    # Convocatorias no necesitan imágenes → marcar directamente sin fetchear
    convocatorias = marcar_no_aplica(convocatorias)

    # url_counts solo para eventos+noticias que realmente se van a fetchear
    # (excluye FUENTES_SIN_IMAGEN y los que ya tienen imagen del scraper)
    items_a_fetchear = [
        i for i in list(eventos) + list(noticias)
        if not i.get("imagen") and i.get("fuente") not in FUENTES_SIN_IMAGEN
    ]
    url_counts = Counter(i["url"] for i in items_a_fetchear)
    dup_count = sum(1 for c in url_counts.values() if c >= 2)
    if dup_count:
        print(f"   ⚠️  {dup_count} URLs duplicadas en eventos/noticias → url_listado")

    print("🔍 Buscando imágenes (25 conexiones paralelas)...")
    limits = httpx.Limits(max_connections=25, max_keepalive_connections=10)
    async with httpx.AsyncClient(limits=limits) as client:
        eventos, noticias = await asyncio.gather(
            enriquecer(eventos, client, url_counts),
            enriquecer(noticias, client, url_counts),
        )

    todos = list(eventos) + list(noticias) + list(convocatorias)
    total = len(todos)
    con = sum(1 for i in todos if i.get("imagen"))

    # Resumen por razón
    razones = Counter(i.get("img_razon", "?") for i in todos if not i.get("imagen"))
    print(f"✅ {con}/{total} ítems con imagen")
    if razones:
        print("   Sin imagen por razón:")
        for r, c in razones.most_common():
            print(f"     {r}: {c}")

    html = render(eventos, noticias, convocatorias)
    tmp = tempfile.NamedTemporaryFile(suffix=".html", delete=False, mode="w", encoding="utf-8")
    tmp.write(html)
    tmp.close()
    print(f"🌐 Abriendo en el browser...")
    webbrowser.open(f"file://{tmp.name}")


if __name__ == "__main__":
    asyncio.run(main())
