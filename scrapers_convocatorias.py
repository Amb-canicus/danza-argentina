from bs4 import BeautifulSoup
import httpx
from datetime import datetime, timedelta
import asyncio
import re
from utils import detectar_tipo, es_convocatoria_danza, limpiar

HTTP_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'es-AR,es;q=0.9',
}

# ─────────────────────────────────────────
#  REGISTRO DE SCRAPERS DE CONVOCATORIAS
# ─────────────────────────────────────────

SCRAPERS_CONVOCATORIAS = []

def convocatoria(nombre):
    """Decorador para registrar un scraper como fuente de convocatorias"""
    def decorator(fn):
        SCRAPERS_CONVOCATORIAS.append({"nombre": nombre, "fn": fn})
        return fn
    return decorator


# ─────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────

class _Page:
    def __init__(self, text): self.html_content = text

async def fetch_async(url):
    async with httpx.AsyncClient(headers=HTTP_HEADERS, follow_redirects=True, timeout=15) as client:
        r = await client.get(url)
        return _Page(r.text)

def fecha_es_vigente(texto):
    """
    Devuelve True si la convocatoria parece vigente:
    - fecha en los últimos 2 meses o próximos 6 meses, o
    - sin fecha (no se puede descartar)
    """
    hoy = datetime.now()
    hace_dos_meses = hoy - timedelta(days=60)
    en_seis_meses  = hoy + timedelta(days=180)

    meses = {
        'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4,
        'mayo': 5, 'junio': 6, 'julio': 7, 'agosto': 8,
        'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12
    }

    # Buscar DD/MM/YYYY
    fechas_encontradas = re.findall(r'(\d{1,2})/(\d{1,2})/(\d{2,4})', texto)
    for d, m, y in fechas_encontradas:
        try:
            year = int(y) if len(y) == 4 else 2000 + int(y)
            fecha = datetime(year, int(m), int(d))
            return hace_dos_meses <= fecha <= en_seis_meses
        except:
            pass

    # Buscar "mes año"
    for nombre_mes, num_mes in meses.items():
        if nombre_mes in texto.lower():
            for year in [hoy.year, hoy.year + 1]:
                try:
                    fecha = datetime(year, num_mes, 1)
                    if hace_dos_meses <= fecha <= en_seis_meses:
                        return True
                except:
                    pass

    # Sin fecha: incluir
    return True

def detectar_subtipo(texto):
    """
    Detecta el subtipo de convocatoria.
    El orden importa: de más específico a más genérico.
    """
    t = texto.lower()
    if any(k in t for k in ['casting', 'se busca', 'se buscan']):
        return 'casting'
    if any(k in t for k in ['audici', 'audición']):
        return 'audición'
    if any(k in t for k in ['beca', 'becas']):
        return 'beca'
    if any(k in t for k in ['subsidio', 'subsidios', 'prodanza', 'fondo']):
        return 'subsidio'
    if any(k in t for k in ['residencia', 'residencias']):
        return 'residencia'
    if any(k in t for k in ['concurso', 'certamen', 'premio']):
        return 'concurso'
    return 'convocatoria'

def construir_item(titulo, descripcion, url, fecha, fuente):
    """
    Construye un item de convocatoria estándar.
    Devuelve None si no pasa el filtro de danza o de vigencia.
    """
    texto_completo = titulo + ' ' + descripcion
    if not es_convocatoria_danza(texto_completo):
        return None
    if not fecha_es_vigente(fecha or texto_completo):
        return None
    return {
        "titulo":      titulo[:120],
        "descripcion": descripcion[:300],
        "tipo":        detectar_tipo(texto_completo),
        "subtipo":     detectar_subtipo(texto_completo),
        "fuente":      fuente,
        "url":         url,
        "fecha":       fecha,
        "es_danza":    True,
    }


# ─────────────────────────────────────────
#  SCRAPERS
# ─────────────────────────────────────────

@convocatoria("Alt Teatral Castings")
async def scrapear_alt_teatral_castings():
    """Castings y audiciones de baile en Argentina — Alternativa Teatral"""
    encontrados = []
    try:
        page = await fetch_async('http://www.alternativateatral.com/convocatorias.php?pais=1&clasificacion=14')
        soup = BeautifulSoup(page.html_content, 'html.parser')
        cuerpo = soup.select_one('div.cuerpo')
        if not cuerpo:
            return encontrados

        for a in cuerpo.find_all('a', href=True):
            href = a['href']
            if not href.startswith('casting'):
                continue
            texto = limpiar(a.get_text())
            if len(texto) < 10:
                continue

            fecha, titulo = '', texto
            match = re.match(r'(\d{2}/\d{2}/\d{4})\s*[-–]\s*(.+)', texto)
            if match:
                fecha  = match.group(1)
                titulo = match.group(2).strip()

            link = 'https://www.alternativateatral.com/' + href.lstrip('/')
            item = construir_item(titulo, texto, link, fecha, "Alternativa Teatral")
            if item:
                encontrados.append(item)

    except Exception as e:
        print(f"Alt Teatral Castings error: {e}")
    return encontrados


@convocatoria("Alt Teatral Convocatorias")
async def scrapear_alt_teatral_conv():
    """Convocatorias generales de danza en Argentina — Alternativa Teatral"""
    encontrados = []
    try:
        page = await fetch_async('http://www.alternativateatral.com/convocatorias.php?pais=1')
        soup = BeautifulSoup(page.html_content, 'html.parser')
        cuerpo = soup.select_one('div.cuerpo')
        if not cuerpo:
            return encontrados

        for a in cuerpo.find_all('a', href=True):
            href = a['href']
            if not (href.startswith('casting') or href.startswith('convocatoria')):
                continue
            texto = limpiar(a.get_text())
            if len(texto) < 10:
                continue

            fecha, titulo = '', texto
            match = re.match(r'(\d{2}/\d{2}/\d{4})\s*[-–]\s*(.+)', texto)
            if match:
                fecha  = match.group(1)
                titulo = match.group(2).strip()

            link = 'https://www.alternativateatral.com/' + href.lstrip('/')
            item = construir_item(titulo, texto, link, fecha, "Alternativa Teatral")
            if item:
                encontrados.append(item)

    except Exception as e:
        print(f"Alt Teatral Conv error: {e}")
    return encontrados


@convocatoria("Recursos Culturales")
async def scrapear_recursos_culturales():
    """Becas, subsidios, residencias y concursos de danza — recursosculturales.com"""
    encontrados = []
    try:
        page = await fetch_async('https://www.recursosculturales.com/tag/danza/')
        soup = BeautifulSoup(page.html_content, 'html.parser')

        for article in soup.select('article')[:30]:
            titulo_tag = article.select_one('h2.is-title, h2, h3')
            if not titulo_tag:
                continue
            titulo = limpiar(titulo_tag.get_text())
            if len(titulo) < 10:
                continue

            link_tag = article.select_one('a[href]')
            link = link_tag['href'] if link_tag else 'https://www.recursosculturales.com/tag/danza/'

            descripcion = limpiar(article.get_text(separator=' '))

            fecha = ''
            match = re.search(r'\d{1,2}/\d{1,2}/\d{2,4}', descripcion)
            if match:
                fecha = match.group(0)

            item = construir_item(titulo, descripcion, link, fecha, "Recursos Culturales")
            if item:
                encontrados.append(item)

    except Exception as e:
        print(f"Recursos Culturales error: {e}")
    return encontrados


@convocatoria("Teatro Cervantes")
async def scrapear_cervantes_conv():
    """Convocatorias de danza vigentes — Teatro Nacional Cervantes"""
    encontrados = []
    try:
        page = await fetch_async('https://www.teatrocervantes.gob.ar/convocatorias-artisticas/')
        soup = BeautifulSoup(page.html_content, 'html.parser')

        DANZA_KW = {'bailarin', 'bailarina', 'bailarines', 'bailarinas', 'danza', 'coreograf', 'audici'}

        for a in soup.find_all('a', href=True):
            titulo = limpiar(a.get_text())
            if len(titulo) < 15:
                continue
            href = a['href']
            if not href.startswith('http'):
                href = 'https://www.teatrocervantes.gob.ar' + href
            # solo convocatorias con keywords de danza
            t = titulo.lower()
            if not any(k in t for k in DANZA_KW):
                continue
            # descartar las de años anteriores
            anos = re.findall(r'\b(20\d\d)\b', titulo)
            if anos and all(int(a) < 2026 for a in anos):
                continue
            item = construir_item(titulo, titulo, href, '', "Teatro Cervantes")
            if item:
                encontrados.append(item)

    except Exception as e:
        print(f"Teatro Cervantes error: {e}")
    return encontrados


@convocatoria("Balletín Dance")
async def scrapear_balletin_conv():
    """Audiciones, becas y subsidios de danza — balletindance.com"""
    encontrados = []
    try:
        for busqueda, subtipo in [
            ('audiciones', 'audición'),
            ('becas+danza', 'beca'),
        ]:
            page = await fetch_async(f'https://balletindance.com/?s={busqueda}')
            soup = BeautifulSoup(page.html_content, 'html.parser')
            for mod in soup.select('.td_module_wrap'):
                link_tag = mod.select_one('h3.entry-title a, h3 a')
                if not link_tag:
                    continue
                titulo = limpiar(link_tag.get_text())
                link = link_tag.get('href', 'https://balletindance.com')
                item = construir_item(titulo, titulo, link, subtipo, "Balletín Dance")
                if item:
                    encontrados.append(item)
    except Exception as e:
        print(f"Balletín Conv error: {e}")
    return encontrados
