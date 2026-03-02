from bs4 import BeautifulSoup
import asyncio
import httpx
import os
import re
from datetime import datetime, timedelta
from patchright.async_api import async_playwright
from utils import detectar_tipo, es_de_danza, limpiar

HTTP_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'es-AR,es;q=0.9',
}

# ─────────────────────────────────────────
#  REGISTRO GLOBAL DE SCRAPERS
#  Cada scraper se registra acá con su nombre y categoría.
#  main.py itera esta lista automáticamente.
#  Para agregar uno nuevo: solo agregarlo acá y escribir la función.
# ─────────────────────────────────────────

SCRAPERS_EVENTOS = []   # scrapers que devuelven eventos
SCRAPERS_NOTICIAS = []  # scrapers que devuelven noticias

def evento(nombre):
    """Decorador para registrar un scraper como fuente de eventos"""
    def decorator(fn):
        SCRAPERS_EVENTOS.append({"nombre": nombre, "fn": fn})
        return fn
    return decorator

def noticia(nombre):
    """Decorador para registrar un scraper como fuente de noticias"""
    def decorator(fn):
        SCRAPERS_NOTICIAS.append({"nombre": nombre, "fn": fn})
        return fn
    return decorator


# ─────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────

class _Page:
    """Envuelve la respuesta httpx para que los scrapers usen page.html_content igual que con Scrapling."""
    def __init__(self, text): self.html_content = text

async def fetch_simple(url, timeout=30):
    """Fetch liviano con httpx — para sitios que no usan bot-protection ni JS dinámico."""
    async with httpx.AsyncClient(headers=HTTP_HEADERS, follow_redirects=True, timeout=timeout) as client:
        r = await client.get(url)
        return _Page(r.text)

CHROMIUM_ARGS = [
    "--no-sandbox",
    "--disable-dev-shm-usage",
    "--single-process",        # corre todo en un proceso, ~100MB en vez de ~350MB
    "--disable-gpu",
    "--no-zygote",
    "--disable-extensions",
    "--disable-background-networking",
    "--disable-default-apps",
    "--mute-audio",
]

async def fetch_stealth(url, wait_selector=None):
    """Fetch con browser headless — para sitios con contenido JS-rendered (CIAD, CC Borges).
    Optimizado para contenedores con 512MB RAM."""
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(args=CHROMIUM_ARGS)
            page = await browser.new_page()
            await page.goto(url, wait_until="domcontentloaded", timeout=40000)
            if wait_selector:
                try:
                    await page.wait_for_selector(wait_selector, timeout=20000)
                except Exception:
                    pass  # si el selector no aparece, usar lo que hay
            content = await page.content()
            await browser.close()
            return _Page(content)
    except Exception as e:
        print(f"fetch_stealth error ({url}): {e}")
        return _Page("")

def _imagen(item):
    """Extrae la mejor URL de imagen disponible: picture/srcset → amp-img → img."""
    source = item.select_one('picture source[srcset]')
    if source:
        url = source['srcset'].split(',')[0].strip().split(' ')[0]
        if url.startswith('http'):
            return url
    amp = item.select_one('amp-img[src]')
    if amp:
        url = amp.get('src', '')
        if url.startswith('http'):
            return url
    img = item.select_one('img')
    if img:
        url = (img.get('data-src') or img.get('data-lazy-src')
               or img.get('data-td-src-property') or img.get('src') or '')
        if url and not url.startswith('data:') and '.svg' not in url:
            if url.startswith('//'): url = 'https:' + url
            if url.startswith('http'): return url
    return None


def extraer_item(item, fuente, url_base, tipo_forzado=None):
    """Helper genérico para extraer título, descripción, link y fecha de un tag"""
    texto = limpiar(item.get_text(separator=' '))
    if len(texto) < 20:
        return None
    titulo_tag = item.select_one('h1,h2,h3,h4,a')
    titulo = limpiar(titulo_tag.get_text()) if titulo_tag else texto[:80]
    link_tag = item.select_one('a[href]')
    link = link_tag['href'] if link_tag else url_base
    if link.startswith('/'):
        link = url_base.rstrip('/') + '/' + link.lstrip('/')
    elif not link.startswith('http'):
        link = url_base.rstrip('/') + '/' + link.lstrip('/')
    fecha_tag = item.select_one('time, .fecha, .date')
    fecha = limpiar(fecha_tag.get_text()) if fecha_tag else ''
    fecha_iso = (fecha_tag.get('datetime') or '') if fecha_tag else ''
    if len(titulo) < 5:
        return None
    return {
        "titulo": titulo[:120],
        "descripcion": texto[:300],
        "tipo": tipo_forzado if tipo_forzado else detectar_tipo(texto),
        "fuente": fuente,
        "url": link,
        "fecha": fecha,
        "fecha_iso": fecha_iso,
    }


# ─────────────────────────────────────────
#  SCRAPERS DE EVENTOS
# ─────────────────────────────────────────

async def _ciad_imagen(url):
    """Fetch página de evento CIAD y extrae la primera imagen del evento."""
    try:
        async with httpx.AsyncClient(headers=HTTP_HEADERS, follow_redirects=True, timeout=10) as c:
            r = await c.get(url)
            soup = BeautifulSoup(r.text, 'html.parser')
            for img in soup.find_all('img'):
                w = int(img.get('width', 0) or 0)
                h = int(img.get('height', 0) or 0)
                src = img.get('src', '')
                # foto de evento: dimensiones razonables, sin logos CIAD ni barras decorativas
                if w >= 200 and h >= 100 and w < 1000 and 'Ciad' not in src and 'barra' not in src:
                    if src.startswith('../../'):
                        src = 'https://www.laciad.info/' + src[6:]
                    elif src.startswith('/'):
                        src = 'https://www.laciad.info' + src
                    if src.startswith('http'):
                        return src
    except Exception:
        pass
    return None


@evento("CIAD")
async def scrapear_ciad():
    encontrados = []
    try:
        page = await fetch_stealth('https://www.laciad.info/todos-los-eventos.html', wait_selector='a[href^="Local/"]')
        soup = BeautifulSoup(page.html_content, 'html.parser')
        BASE = 'https://www.laciad.info/'
        GENERICOS = {'webinfo', 'más info', 'website link', 'website', 'reglamento',
                     'ciaddanza info', 'información', 'más\ninfo', 'info'}
        vistos = set()
        for a in soup.select('a[href]'):
            href = a.get('href', '')
            if not href.startswith('Local/') or href in vistos:
                continue
            vistos.add(href)
            titulo = limpiar(a.get_text(separator=' '))
            if titulo.lower().strip() in GENERICOS or len(titulo) < 5:
                import os as _os
                partes = href.split('/')
                nombre = _os.path.splitext(partes[-1])[0]
                mes = partes[-2].capitalize() if len(partes) > 2 else ''
                titulo = nombre.replace('-', ' ').replace('_', ' ').title()
                if mes and mes.lower() not in nombre.lower():
                    titulo = f"{titulo} — {mes}"
            if len(titulo) < 3:
                continue
            anos = re.findall(r'\b(20\d\d)\b', titulo)
            if anos and all(int(a) < 2026 for a in anos):
                continue
            encontrados.append({
                "titulo": titulo[:120], "descripcion": titulo[:300],
                "tipo": detectar_tipo(titulo), "fuente": "CIAD",
                "url": BASE + href, "fecha": ""
            })
        # Fetch imágenes en paralelo desde las páginas de detalle
        imagenes = await asyncio.gather(*[_ciad_imagen(e['url']) for e in encontrados], return_exceptions=True)
        for item, img in zip(encontrados, imagenes):
            if img and not isinstance(img, Exception):
                item['imagen'] = img
    except Exception as e:
        print(f"CIAD error: {e}")
    return encontrados


@evento("BA Ciudad")
async def scrapear_bsas_cultura():
    """Usa la API JSON de buenosaires.gob.ar filtrando field_tipo_de_evento=='Danza'."""
    encontrados = []
    try:
        async with httpx.AsyncClient(headers=HTTP_HEADERS, follow_redirects=True, timeout=20) as client:
            pages = await asyncio.gather(*[
                client.get(f'https://buenosaires.gob.ar/api/v1/eventos?categoria=danza&page={p}')
                for p in range(6)
            ], return_exceptions=True)
            all_items = []
            for resp in pages:
                if isinstance(resp, Exception):
                    continue
                try:
                    all_items.extend(resp.json().get('content', []))
                except Exception:
                    pass
            for item in all_items:
                    if item.get('field_tipo_de_evento') != 'Danza':
                        continue
                    titulo = limpiar(item.get('title', ''))
                    if len(titulo) < 5:
                        continue
                    body = BeautifulSoup(item.get('body', ''), 'html.parser').get_text().strip()
                    # URL: construir desde slug del view_node
                    vn = item.get('view_node', '')
                    slug = vn.split('/')[-1] if vn else ''
                    url = (f'https://buenosaires.gob.ar/descubrir/{slug}'
                           if slug else 'https://buenosaires.gob.ar')
                    # Imagen: en field_image['media_image'] como HTML
                    imagen = None
                    img_raw = item.get('field_image')
                    if isinstance(img_raw, dict):
                        img_html = img_raw.get('media_image', '')
                        img_tag = BeautifulSoup(img_html, 'html.parser').find('img', src=True)
                        if img_tag:
                            src = img_tag['src']
                            if src.startswith('/'):
                                src = 'https://buenosaires.gob.ar' + src
                            if src.startswith('http'):
                                imagen = src
                    # Fecha: timestamp unix
                    fecha = ''
                    ts = str(item.get('field_fecha_del_evento', '')).strip()
                    if ts.isdigit():
                        from datetime import datetime as _dt
                        fecha = _dt.fromtimestamp(int(ts)).strftime('%d/%m/%Y')
                    result = {
                        "titulo": titulo[:120],
                        "descripcion": limpiar(body)[:300],
                        "tipo": detectar_tipo(titulo + ' ' + body),
                        "fuente": "BA Ciudad",
                        "url": url,
                        "fecha": fecha,
                    }
                    if imagen:
                        result["imagen"] = imagen
                    encontrados.append(result)
    except Exception as e:
        print(f"BA Ciudad error: {e}")
    return encontrados


@evento("Palacio Libertad")
async def scrapear_palacio_libertad():
    encontrados = []
    try:
        page = await fetch_simple('https://palaciolibertad.gob.ar/agenda/')
        soup = BeautifulSoup(page.html_content, 'html.parser')
        vistos = set()
        for art in soup.select('article.mec-event-article'):
            h3 = art.find('h3')
            if not h3:
                continue
            titulo = limpiar(h3.get_text())
            if len(titulo) < 5 or titulo in vistos:
                continue
            texto = limpiar(art.get_text(separator=' '))
            # Palacio Libertad usa etiqueta de categoría explícita ("Danza") en el artículo.
            # Usamos regex para evitar falsos positivos de "Música académica" (clásic)
            # o "música experimental" (experimental).
            if not re.search(r'\bdanza\b', texto.lower()) and not re.search(r'\bballet\b', texto.lower()):
                continue
            vistos.add(titulo)
            link_tag = art.find('a', href=True)
            link = link_tag['href'] if link_tag else 'https://palaciolibertad.gob.ar'
            if link.startswith('/'):
                link = 'https://palaciolibertad.gob.ar' + link
            fecha_el = art.select_one('[class*="date"]')
            fecha = limpiar(fecha_el.get_text()) if fecha_el else ''
            encontrados.append({
                "titulo": titulo[:120],
                "descripcion": texto[:300],
                "tipo": detectar_tipo(titulo + ' ' + texto),
                "fuente": "Palacio Libertad",
                "url": link,
                "fecha": fecha,
            })
    except Exception as e:
        print(f"Palacio Libertad error: {e}")
    return encontrados


@evento("Alternativa Teatral")
async def scrapear_alternativa_teatral():
    encontrados = []
    try:
        page = await fetch_simple('http://www.alternativateatral.com/buscar.asp?objetivo=obras&texto=danza')
        soup = BeautifulSoup(page.html_content, 'html.parser')
        for item in soup.select('li')[:50]:
            texto = limpiar(item.get_text(separator=' '))
            if len(texto) < 20:
                continue
            # solo obras en cartelera en 2026
            if '2026' not in texto:
                continue
            titulo_tag = item.select_one('a')
            titulo = limpiar(titulo_tag.get_text()) if titulo_tag else texto[:80]
            link_tag = item.select_one('a[href]')
            link = link_tag['href'] if link_tag else 'https://www.alternativateatral.com'
            if not link.startswith('http'):
                link = 'https://www.alternativateatral.com/' + link.lstrip('/')
            img_tag = item.find('img', src=True)
            imagen = None
            if img_tag:
                src = img_tag['src']
                if src.startswith('//'):
                    src = 'https:' + src
                # pedir versión más grande (300x225 en vez de 100x75)
                imagen = src.replace('100x75', 'resumen')
            if len(titulo) > 5 and es_de_danza(titulo + ' ' + texto):
                item_dict = {
                    "titulo": titulo[:120],
                    "descripcion": texto[:300],
                    "tipo": detectar_tipo(texto),
                    "fuente": "Alternativa Teatral",
                    "url": link,
                    "fecha": "2026",
                }
                if imagen:
                    item_dict["imagen"] = imagen
                encontrados.append(item_dict)
    except Exception as e:
        print(f"Alt Teatral error: {e}")
    return encontrados


@evento("Teatro Colón")
async def scrapear_teatro_colon():
    encontrados = []
    try:
        page = await fetch_simple('https://teatrocolon.org.ar/categoria-produccion/ballet/')
        soup = BeautifulSoup(page.html_content, 'html.parser')
        for card in soup.select('article.event-card'):
            link_tag = card.select_one('a[href]')
            if not link_tag:
                continue
            link = link_tag.get('href', '')
            if not link.startswith('http'):
                link = 'https://teatrocolon.org.ar' + link
            # El atributo title del <a> a veces está vacío; fallback al slug de la URL
            titulo = link_tag.get('title', '').strip()
            if not titulo:
                slug = link.rstrip('/').split('/')[-1]
                titulo = slug.replace('-', ' ').title()
            if len(titulo) < 5:
                continue
            img_tag = card.select_one('img[src]')
            imagen = img_tag['src'] if img_tag else None
            resultado = {
                "titulo": titulo[:120],
                "descripcion": titulo[:300],
                "tipo": "clásica",
                "fuente": "Teatro Colón",
                "url": link,
                "fecha": "",
                "es_danza": True,
            }
            if imagen:
                resultado["imagen"] = imagen
            encontrados.append(resultado)
    except Exception as e:
        print(f"Teatro Colón error: {e}")
    return encontrados


# Teatro San Martín: /ver/danza devuelve 404. Cubierto por CTBA Agenda.
# @evento("Teatro San Martín")
# async def scrapear_teatro_san_martin(): ...


@evento("CC Borges")
async def scrapear_cc_borges():
    """cloudscraper para pasar el challenge de Cloudflare y llamar la API interna."""
    import cloudscraper
    from concurrent.futures import ThreadPoolExecutor
    encontrados = []
    BASE = 'https://centroculturalborges.gob.ar'
    API = f'{BASE}/api/public/eventos-destacados?disciplina=danza'
    try:
        def fetch_cf():
            scraper = cloudscraper.create_scraper()
            r = scraper.get(API, timeout=30)
            print(f"CC Borges status={r.status_code}")
            return r.json() if r.status_code == 200 else []

        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor(max_workers=1) as pool:
            items = await loop.run_in_executor(pool, fetch_cf)

        if not isinstance(items, list):
            items = []
        print(f"CC Borges: {len(items)} items")
        for item in items:
            titulo = limpiar(item.get('titulo', ''))
            if len(titulo) < 5:
                continue
            desc = limpiar(item.get('descripcion', ''))
            fecha = item.get('fechaSiguienteRepeticion', '') or item.get('fechaDisplay', '')
            imagen_path = item.get('imagenUrl', '')
            imagen = (BASE + imagen_path) if imagen_path and imagen_path.startswith('/') else None
            encontrados.append({
                "titulo": titulo[:120],
                "descripcion": desc[:300],
                "tipo": detectar_tipo(titulo + ' ' + desc),
                "fuente": "CC Borges",
                "url": f'{BASE}/disciplinas?d=danza',
                "fecha": fecha,
                "es_danza": True,
                **({"imagen": imagen} if imagen else {}),
            })
    except Exception as e:
        print(f"CC Borges error: {e}")
    return encontrados


@evento("Usina del Arte")
async def scrapear_usina():
    encontrados = []
    try:
        page = await fetch_simple('https://usinadelarte.ar/actividades/')
        soup = BeautifulSoup(page.html_content, 'html.parser')
        for item in soup.select('.actividad'):
            texto = limpiar(item.get_text(separator=' '))
            if not es_de_danza(texto) or len(texto) < 30:
                continue
            resultado = extraer_item(item, "Usina del Arte", "https://usinadelarte.ar")
            if resultado:
                encontrados.append(resultado)
    except Exception as e:
        print(f"Usina del Arte error: {e}")
    return encontrados


@evento("CC Recoleta")
async def scrapear_cc_recoleta():
    encontrados = []
    try:
        page = await fetch_simple('http://centroculturalrecoleta.org/agenda')
        soup = BeautifulSoup(page.html_content, 'html.parser')
        for item in soup.select('div.box-info.event-info'):
            texto = limpiar(item.get_text(separator=' '))
            # El texto empieza con el hashtag de categoría explícita, ej: "#Danza Título"
            # Solo pasamos eventos donde la categoría es exactamente danza
            if not re.search(r'#Danza\b', item.get_text()):
                continue
            # El título está después del tag de categoría
            lineas = [l.strip() for l in item.get_text().splitlines() if l.strip()]
            titulo = lineas[1] if len(lineas) > 1 else lineas[0] if lineas else ''
            if len(titulo) < 5:
                continue
            resultado = {
                "titulo": titulo[:120],
                "descripcion": texto[:300],
                "tipo": detectar_tipo(texto),
                "fuente": "CC Recoleta",
                "url": "http://centroculturalrecoleta.org/agenda",
                "fecha": "",
            }
            encontrados.append(resultado)
    except Exception as e:
        print(f"CC Recoleta error: {e}")
    return encontrados


# ─────────────────────────────────────────
#  SCRAPERS DE NOTICIAS
# ─────────────────────────────────────────

@noticia("Balletín Dance")
async def scrapear_balletin_dance():
    """Usa el feed RSS para evitar el bloqueo de Cloudflare en Koyeb."""
    from email.utils import parsedate_to_datetime
    encontrados = []
    try:
        page = await fetch_simple('https://balletindance.com/feed/')
        # Extraer links con regex antes de parsear (BeautifulSoup xml trata <link> como void)
        links = re.findall(r'<link>(https://balletindance\.com[^<]+)</link>', page.html_content)
        soup = BeautifulSoup(page.html_content, 'xml')
        items = soup.select('item')
        for i, item in enumerate(items):
            titulo_tag = item.find('title')
            if not titulo_tag:
                continue
            titulo = limpiar(titulo_tag.get_text())
            if len(titulo) < 5:
                continue
            link = links[i] if i < len(links) else 'https://balletindance.com'
            pub = item.find('pubDate').get_text() if item.find('pubDate') else ''
            try:
                fecha_iso = parsedate_to_datetime(pub).strftime('%Y-%m-%dT%H:%M:%S')
            except Exception:
                fecha_iso = ''
            desc_tag = item.find('description')
            desc = limpiar(desc_tag.get_text()) if desc_tag else titulo
            encoded = item.find('encoded')
            imagen = None
            if encoded:
                m = re.search(r'src="(https://balletindance\.com/wp-content/uploads/[^"]+)"', encoded.get_text())
                if m:
                    imagen = re.sub(r'-\d{3,4}x\d{3,4}(?=\.\w+$)', '', m.group(1))
            resultado = {
                "titulo": titulo[:120], "descripcion": desc[:300],
                "tipo": detectar_tipo(titulo + ' ' + desc),
                "fuente": "Balletín Dance",
                "url": link, "fecha": "", "fecha_iso": fecha_iso,
                "es_danza": True,  # revista de danza — todo su contenido es de danza
            }
            if imagen:
                resultado["imagen"] = imagen
            encontrados.append(resultado)
    except Exception as e:
        print(f"Balletín Dance error: {e}")
    return encontrados


@noticia("Perfil")
async def scrapear_perfil():
    encontrados = []
    try:
        page = await fetch_simple('https://noticias.perfil.com/seccion/danza')
        soup = BeautifulSoup(page.html_content, 'html.parser')
        for item in soup.select('article, .nota, .story')[:20]:
            resultado = extraer_item(item, "Perfil", "https://noticias.perfil.com")
            if resultado:
                # Fecha: Perfil usa <span class="date-time">DD-MM-YYYY HH:MM</span>
                date_tag = item.select_one('.date-time')
                if date_tag:
                    resultado['fecha'] = limpiar(date_tag.get_text())
                img_tag = item.find('img')
                if img_tag:
                    # Perfil usa srcset con la imagen real; src es siempre un placeholder
                    srcset = img_tag.get('srcset') or img_tag.get('data-srcset', '')
                    if srcset:
                        # Tomar la URL más grande (última entrada del srcset)
                        src = srcset.split(',')[-1].strip().split(' ')[0]
                    else:
                        src = img_tag.get('data-src') or img_tag.get('data-lazy-src') or img_tag.get('src', '')
                    if src and not src.startswith('data:') and 'placeholder' not in src:
                        if src.startswith('//'): src = 'https:' + src
                        if src.startswith('http'): resultado['imagen'] = src
                encontrados.append(resultado)
    except Exception as e:
        print(f"Perfil error: {e}")
    return encontrados


@evento("Hoy Milonga")
async def scrapear_hoy_milonga():
    encontrados = []
    BASE = 'https://www.hoy-milonga.com'
    try:
        page = await fetch_simple(f'{BASE}/buenos-aires/es/encuentros')
        soup = BeautifulSoup(page.html_content, 'html.parser')
        vistos = set()
        for item in soup.select('a.bg-white')[:60]:
            titulo_tag = item.select_one('h3')
            if not titulo_tag:
                continue
            titulo = limpiar(titulo_tag.get_text())
            if len(titulo) < 5 or titulo in vistos:
                continue
            vistos.add(titulo)
            texto = limpiar(item.get_text(separator=' '))
            link = item.get('href', '')
            if link.startswith('/'):
                link = BASE + link
            img_tag = item.find('img', src=True)
            imagen = None
            if img_tag:
                src = img_tag.get('src', '')
                if src and src.startswith('http'):
                    imagen = src
            resultado = {
                "titulo": titulo[:120],
                "descripcion": texto[:300],
                "tipo": "tango",
                "fuente": "Hoy Milonga",
                "url": link,
                "fecha": "",
            }
            if imagen:
                resultado["imagen"] = imagen
            encontrados.append(resultado)
    except Exception as e:
        print(f"Hoy Milonga error: {e}")
    return encontrados


@evento("CTBA Agenda")
async def scrapear_ctba_agenda():
    """Scrape la agenda del Complejo Teatral BA para los próximos 7 días, filtrando danza."""
    encontrados = []
    BASE = 'https://complejoteatral.gob.ar'
    hoy = datetime.now()
    fechas = [(hoy + timedelta(days=i)).strftime('%d-%m-%Y') for i in range(7)]

    async def fetch_dia(fecha_str):
        items = []
        try:
            url = f'{BASE}/agenda?fecha={fecha_str}'
            page = await fetch_simple(url)
            soup = BeautifulSoup(page.html_content, 'html.parser')
            for item in soup.select('.small_item, .list-item, article'):
                texto = limpiar(item.get_text(separator=' '))
                if not es_de_danza(texto) or len(texto) < 20:
                    continue
                titulo_tag = item.select_one('h2, h3, h4, a')
                titulo = limpiar(titulo_tag.get_text()) if titulo_tag else texto[:80]
                if len(titulo) < 5:
                    continue
                link_tag = item.select_one('a[href]')
                link = link_tag['href'] if link_tag else BASE
                if link.startswith('/'):
                    link = BASE + link
                bg = item.select_one('[data-background-image]')
                imagen = bg['data-background-image'] if bg else None
                entry = {
                    "titulo": titulo[:120],
                    "descripcion": texto[:300],
                    "tipo": detectar_tipo(texto),
                    "fuente": "CTBA",
                    "url": link,
                    "fecha": fecha_str,
                }
                if imagen:
                    entry["imagen"] = imagen
                items.append(entry)
        except Exception as e:
            print(f"CTBA {fecha_str} error: {e}")
        return items

    resultados = await asyncio.gather(*[fetch_dia(f) for f in fechas])
    for lista in resultados:
        encontrados.extend(lista)
    return encontrados


@noticia("Clarín")
async def scrapear_clarin():
    encontrados = []
    try:
        page = await fetch_simple('https://www.clarin.com/tema/danza.html')
        soup = BeautifulSoup(page.html_content, 'html.parser')
        for art in soup.select('article')[:25]:
            h = art.select_one('h2.title')
            if not h:
                continue
            titulo = limpiar(h.get_text())
            if len(titulo) < 5:
                continue
            link_tag = art.select_one('a[href]')
            link = link_tag['href'] if link_tag else 'https://www.clarin.com'
            if link.startswith('/'):
                link = 'https://www.clarin.com' + link
            fecha_tag = art.select_one('span.date')
            fecha = limpiar(fecha_tag.get_text()) if fecha_tag else ''
            img = _imagen(art)
            resultado = {
                "titulo": titulo[:120], "descripcion": titulo[:300],
                "tipo": detectar_tipo(titulo), "fuente": "Clarín",
                "url": link, "fecha": fecha, "fecha_iso": "",
            }
            if img: resultado['imagen'] = img
            encontrados.append(resultado)
    except Exception as e:
        print(f"Clarín error: {e}")
    return encontrados


@noticia("Página 12")
async def scrapear_pagina12():
    encontrados = []
    try:
        for pag in range(1, 3):
            page = await fetch_simple(f'https://www.pagina12.com.ar/tags/danza/?page={pag}')
            soup = BeautifulSoup(page.html_content, 'html.parser')
            cards = soup.select('.p12-article-card-full')
            if not cards:
                break
            for card in cards:
                resultado = extraer_item(card, "Página 12", "https://www.pagina12.com.ar")
                if not resultado or not es_de_danza(resultado['titulo'] + ' ' + resultado['descripcion']):
                    continue
                img = _imagen(card)
                if img: resultado['imagen'] = img
                t = card.select_one('time[datetime]')
                if t: resultado['fecha_iso'] = t['datetime']
                encontrados.append(resultado)
    except Exception as e:
        print(f"Página 12 error: {e}")
    return encontrados


@noticia("Diario Uno")
async def scrapear_diario_uno():
    encontrados = []
    try:
        for pag in range(1, 3):
            page = await fetch_simple(f'https://www.diariouno.com.ar/tags/danza?page={pag}')
            soup = BeautifulSoup(page.html_content, 'html.parser')
            arts = soup.select('article')
            if not arts:
                break
            for art in arts:
                resultado = extraer_item(art, "Diario Uno", "https://www.diariouno.com.ar")
                if not resultado or not es_de_danza(resultado['titulo'] + ' ' + resultado['descripcion']):
                    continue
                img = _imagen(art)
                if img: resultado['imagen'] = img
                encontrados.append(resultado)
    except Exception as e:
        print(f"Diario Uno error: {e}")
    return encontrados


@noticia("TN")
async def scrapear_tn():
    encontrados = []
    try:
        for pag in range(1, 3):
            page = await fetch_simple(f'https://tn.com.ar/tags/danza/?page={pag}')
            soup = BeautifulSoup(page.html_content, 'html.parser')
            arts = soup.select('article.card__container')
            if not arts:
                break
            for art in arts:
                h = art.select_one('h2.card__headline a, h2.card__headline')
                if not h:
                    continue
                titulo = limpiar(h.get_text())
                if len(titulo) < 5:
                    continue
                link_tag = art.select_one('h2.card__headline a[href]')
                link = ('https://tn.com.ar' + link_tag['href']) if link_tag and link_tag['href'].startswith('/') else (link_tag['href'] if link_tag else 'https://tn.com.ar')
                desc_tag = art.select_one('p.card__subheadline')
                desc = limpiar(desc_tag.get_text()) if desc_tag else titulo
                img = _imagen(art)
                m_fecha = re.search(r'/(\d{4})/(\d{2})/(\d{2})/', link)
                fecha = f"{m_fecha.group(3)}/{m_fecha.group(2)}/{m_fecha.group(1)}" if m_fecha else ""
                fecha_iso = f"{m_fecha.group(1)}-{m_fecha.group(2)}-{m_fecha.group(3)}" if m_fecha else ""
                resultado = {
                    "titulo": titulo[:120], "descripcion": desc[:300],
                    "tipo": detectar_tipo(titulo + ' ' + desc), "fuente": "TN",
                    "url": link, "fecha": fecha, "fecha_iso": fecha_iso,
                }
                if img: resultado['imagen'] = img
                if es_de_danza(titulo + ' ' + desc):
                    encontrados.append(resultado)
    except Exception as e:
        print(f"TN error: {e}")
    return encontrados


@noticia("El Destape")
async def scrapear_el_destape():
    encontrados = []
    try:
        for pag in range(1, 3):
            page = await fetch_simple(f'https://www.eldestapeweb.com/tag/danza?page={pag}')
            soup = BeautifulSoup(page.html_content, 'html.parser')
            arts = soup.select('article.nota__amp')
            if not arts:
                break
            for art in arts:
                # Título en h2.nota__titulo-item, NO en h3.nota__volanta (que es la sección)
                h = art.select_one('h2.nota__titulo-item a, div.nota__titulo h2 a')
                if not h:
                    continue
                titulo = limpiar(h.get_text())
                if len(titulo) < 5:
                    continue
                link = h.get('href', '')
                if link.startswith('/'): link = 'https://www.eldestapeweb.com' + link
                if not link.startswith('http'): continue
                img = _imagen(art)
                t = art.select_one('time[datetime]')
                resultado = {
                    "titulo": titulo[:120], "descripcion": titulo[:300],
                    "tipo": detectar_tipo(titulo), "fuente": "El Destape",
                    "url": link, "fecha": "", "fecha_iso": t['datetime'] if t else "",
                }
                if img: resultado['imagen'] = img
                encontrados.append(resultado)
    except Exception as e:
        print(f"El Destape error: {e}")
    return encontrados


@noticia("Río Negro")
async def scrapear_rio_negro():
    encontrados = []
    try:
        for pag in range(1, 3):
            page = await fetch_simple(f'https://www.rionegro.com.ar/tag/danza/?page={pag}')
            soup = BeautifulSoup(page.html_content, 'html.parser')
            arts = soup.select('article.news')
            if not arts:
                break
            for art in arts:
                # Río Negro: el título está en el atributo title del <a> que envuelve la imagen
                link_tag = art.select_one('a[href][title]') or art.select_one('a[href]')
                if not link_tag: continue
                titulo = link_tag.get('title', '') or limpiar(link_tag.get_text())
                if not titulo:
                    h = art.select_one('h2, h3, h4')
                    titulo = limpiar(h.get_text()) if h else ''
                if len(titulo) < 5: continue
                link = link_tag['href']
                if not link.startswith('http'): link = 'https://www.rionegro.com.ar' + link
                img = _imagen(art)
                t = art.select_one('time[datetime]')
                resultado = {
                    "titulo": titulo[:120], "descripcion": titulo[:300],
                    "tipo": detectar_tipo(titulo), "fuente": "Río Negro",
                    "url": link, "fecha": "", "fecha_iso": t['datetime'] if t else "",
                }
                if img: resultado['imagen'] = img
                encontrados.append(resultado)
    except Exception as e:
        print(f"Río Negro error: {e}")
    return encontrados


@noticia("Tiempo Sur")
async def scrapear_tiempo_sur():
    encontrados = []
    try:
        for pag in range(1, 3):
            page = await fetch_simple(f'https://www.tiemposur.com.ar/tema/danza?page={pag}')
            soup = BeautifulSoup(page.html_content, 'html.parser')
            arts = soup.select('article')
            if not arts:
                break
            for art in arts:
                resultado = extraer_item(art, "Tiempo Sur", "https://www.tiemposur.com.ar")
                if not resultado:
                    continue
                img = _imagen(art)
                if img: resultado['imagen'] = img
                encontrados.append(resultado)
    except Exception as e:
        print(f"Tiempo Sur error: {e}")
    return encontrados


@noticia("Diario Democracia")
async def scrapear_democracia():
    encontrados = []
    BASE = 'https://www.diariodemocracia.com'
    try:
        for pag in range(1, 4):
            page = await fetch_simple(f'{BASE}/tag/danza/?page={pag}')
            soup = BeautifulSoup(page.html_content, 'html.parser')
            arts = soup.select('article.tag-detail__wrapper--content-stories-ctn--article')
            if not arts:
                break
            for art in arts:
                link_tag = art.select_one('a[title]') or art.select_one('a[href]')
                if not link_tag:
                    continue
                titulo = link_tag.get('title') or limpiar(link_tag.get_text())
                if len(titulo) < 5:
                    continue
                link = link_tag.get('href', '')
                if link.startswith('/'): link = BASE + link
                img_tag = art.select_one('img[src]')
                resultado = {
                    "titulo": titulo[:120], "descripcion": titulo[:300],
                    "tipo": detectar_tipo(titulo), "fuente": "Diario Democracia",
                    "url": link, "fecha": "", "fecha_iso": "",
                }
                if img_tag:
                    src = img_tag.get('src', '')
                    if src.startswith('http'): resultado['imagen'] = src
                encontrados.append(resultado)
    except Exception as e:
        print(f"Diario Democracia error: {e}")
    return encontrados


@noticia("El1 Digital")
async def scrapear_el1_digital():
    encontrados = []
    try:
        for pag in range(1, 3):
            page = await fetch_stealth(f'https://www.el1digital.com.ar/tag/danza/?page={pag}')
            soup = BeautifulSoup(page.html_content, 'html.parser')
            arts = soup.select('article')
            if not arts:
                break
            for art in arts:
                resultado = extraer_item(art, "El1 Digital", "https://www.el1digital.com.ar")
                if not resultado:
                    continue
                img = _imagen(art)
                if img: resultado['imagen'] = img
                t = art.select_one('time[datetime]')
                if t: resultado['fecha_iso'] = t['datetime']
                encontrados.append(resultado)
    except Exception as e:
        print(f"El1 Digital error: {e}")
    return encontrados


@noticia("La Nación")
async def scrapear_la_nacion():
    encontrados = []
    try:
        page = await fetch_simple('https://www.lanacion.com.ar/espectaculos/danza/')
        soup = BeautifulSoup(page.html_content, 'html.parser')
        for art in soup.select('article.mod-article')[:30]:
            h = art.select_one('h2.com-title a.com-link')
            if not h:
                continue
            titulo = limpiar(h.get_text())
            if len(titulo) < 5:
                continue
            link = h.get('href', '')
            if link.startswith('/'):
                link = 'https://www.lanacion.com.ar' + link
            t = art.select_one('time.com-date')
            fecha = limpiar(t.get_text()) if t else ''
            img = _imagen(art)
            resultado = {
                "titulo": titulo[:120], "descripcion": titulo[:300],
                "tipo": detectar_tipo(titulo), "fuente": "La Nación",
                "url": link, "fecha": fecha, "fecha_iso": t.get('datetime', '') if t else '',
            }
            if img: resultado['imagen'] = img
            encontrados.append(resultado)
    except Exception as e:
        print(f"La Nación error: {e}")
    return encontrados


@evento("Cultura Nación")
async def scrapear_cultura_nacion():
    """Agenda Cultural Federal filtrada por categoría danza."""
    encontrados = []
    BASE = 'https://www.cultura.gob.ar'
    try:
        page = await fetch_simple(f'{BASE}/agenda/filtro/?categoria=danza')
        soup = BeautifulSoup(page.html_content, 'html.parser')
        for art in soup.select('article'):
            titulo_tag = art.select_one('h3.titulo a')
            if not titulo_tag:
                continue
            titulo = limpiar(titulo_tag.get_text())
            if len(titulo) < 5:
                continue
            link_tag = art.select_one('a.goto')
            link = link_tag.get('href', '') if link_tag else ''
            if link.startswith('/'):
                link = BASE + link
            elif not link.startswith('http'):
                link = BASE + '/' + link.lstrip('/')
            fecha_tag = art.select_one('header small')
            fecha = limpiar(fecha_tag.get_text()) if fecha_tag else ''
            img_div = art.select_one('.image-wrapper[data-original]')
            imagen = (BASE + img_div['data-original']) if img_div else None
            desc_tag = art.select_one('.bajada')
            desc = limpiar(desc_tag.get_text()) if desc_tag else titulo
            resultado = {
                "titulo": titulo[:120],
                "descripcion": desc[:300],
                "tipo": detectar_tipo(titulo + ' ' + desc),
                "fuente": "Cultura Nación",
                "url": link,
                "fecha": fecha,
            }
            if imagen:
                resultado["imagen"] = imagen
            encontrados.append(resultado)
    except Exception as e:
        print(f"Cultura Nación error: {e}")
    return encontrados


@noticia("Infobae")
async def scrapear_infobae():
    encontrados = []
    try:
        page = await fetch_simple('https://www.infobae.com/tag/danza/')
        soup = BeautifulSoup(page.html_content, 'html.parser')
        for card in soup.select('.feed-list-card'):
            titulo_tag = card.select_one('h2')
            if not titulo_tag:
                continue
            titulo = limpiar(titulo_tag.get_text())
            if len(titulo) < 10 or not es_de_danza(titulo):
                continue
            link = card.get('href', '') if card.name == 'a' else ''
            if not link:
                a = card.select_one('a[href]')
                link = a['href'] if a else 'https://www.infobae.com'
            if link.startswith('/'): link = 'https://www.infobae.com' + link
            m_fecha = re.search(r'/(\d{4})/(\d{2})/(\d{2})/', link)
            fecha = f"{m_fecha.group(3)}/{m_fecha.group(2)}/{m_fecha.group(1)}" if m_fecha else ""
            fecha_iso = f"{m_fecha.group(1)}-{m_fecha.group(2)}-{m_fecha.group(3)}" if m_fecha else ""
            resultado = {
                "titulo": titulo[:120], "descripcion": titulo[:300],
                "tipo": detectar_tipo(titulo), "fuente": "Infobae",
                "url": link, "fecha": fecha, "fecha_iso": fecha_iso,
            }
            img = _imagen(card)
            if img: resultado['imagen'] = img
            encontrados.append(resultado)
    except Exception as e:
        print(f"Infobae error: {e}")
    return encontrados
