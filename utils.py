from datetime import datetime, timedelta
import random
import re

# ─────────────────────────────────────────
#  KEYWORDS
# ─────────────────────────────────────────

KEYWORDS_CLASICA = ["ballet", "clásic", "classic", "colón", "líric", "ópera", "pas de deux"]
KEYWORDS_FOLK    = ["folklor", "folclor", "malambo", "zamba", "chacarera", "gaucho", "peña", "regional", "chamame", "chamamé"]
KEYWORDS_CONTEMP = ["contemporánea", "contemporanea", "contemporáneo", "contemporaneo", "moderno", "moderna", "experimental", "escénico", "escenico", "coreograf"]
KEYWORDS_TANGO   = ["tango", "milonga", "bandoneon", "bandoneón", "orquesta típica", "tango escenario", "tango pista", "milonguero"]
KEYWORDS_DANZA   = ["danza", "baile", "bailarín", "bailarina", "ballet", "coreograf", "malambo", "zamba", "tango", "milonga"]

# Keywords para filtrar convocatorias.
# Solo pasan convocatorias que mencionen alguna de estas disciplinas.
# Editá esta lista para ampliar o acotar el filtro.
KEYWORDS_CONVOCATORIA_DANZA = [
    "danza", "baile", "bailar", "bailarín", "bailarina",
    "ballet", "tango", "coreograf",
    "contemporán", "clásic", "classic",
    "performance", "escénic",
    "folklor", "folclor", "malambo",
    "tap", "jazz dance",
]

TITULOS_BLOQUEADOS = [
    "trio pop femenino",
]

# Secciones de URL que siempre se excluyen (policiales, deportes, etc.)
SECCIONES_EXCLUIDAS_URL = [
    "/justicia/", "/policiales/", "/policial/", "/crimen/", "/seguridad/",
    "/deportes/", "/deporte/",
]

KEYWORDS_EXCLUIR_SIEMPRE = [
    "newsletter", "suscribite", "suscripción",
    "política de privacidad", "términos y condiciones",
    "iniciar sesión", "registrate", "olvidaste tu contraseña",
    "archivo en pdf", "revistas del año", "archivos pdf",
    "e-learning", "jornadas presenciales", "webinar",
    "recuperá tu contraseña", "sponsoreo", "donaciones",
    "visita guiada", "visitas guiadas", "centro de documentación",
    "centro de vestuario", "recursos para espectadores",
    "renovación de abonos", "venta de abonos",
    "orquesta académica", "contenidos en off",
]

# ─────────────────────────────────────────
#  FUNCIONES
# ─────────────────────────────────────────

def detectar_tipo(texto):
    t = texto.lower()
    if any(k in t for k in KEYWORDS_TANGO):     return "tango"
    if any(k in t for k in KEYWORDS_CONTEMP):   return "contemporánea"
    if any(k in t for k in KEYWORDS_CLASICA):   return "clásica"
    if any(k in t for k in KEYWORDS_FOLK):      return "folklórica"
    return "contemporánea"

def es_de_danza(texto):
    t = texto.lower()
    if any(k in t for k in KEYWORDS_EXCLUIR_SIEMPRE):
        return False
    return any(k in t for k in KEYWORDS_DANZA + KEYWORDS_CLASICA + KEYWORDS_FOLK + KEYWORDS_CONTEMP)

def es_convocatoria_danza(texto):
    """
    Filtra convocatorias: solo pasan las que sean de danza clásica,
    contemporánea, ballet, tango o performance.
    Editá KEYWORDS_CONVOCATORIA_DANZA para ajustar el filtro.
    Editá TITULOS_BLOQUEADOS para excluir avisos específicos.
    """
    t = texto.lower()
    if any(k in t for k in KEYWORDS_EXCLUIR_SIEMPRE):
        return False
    if any(k in t for k in TITULOS_BLOQUEADOS):
        return False
    return any(k in t for k in KEYWORDS_CONVOCATORIA_DANZA)

def limpiar(texto):
    return ' '.join(texto.split())

def titulo_igual_copete(titulo, descripcion):
    t1 = titulo.strip().lower()
    t2 = descripcion.strip().lower()
    return t1 == t2 or t1 in t2[:len(t1)+10]

def limpiar_item(item):
    if titulo_igual_copete(item["titulo"], item["descripcion"]):
        item["descripcion"] = ""
    return item

def parsear_fecha_iso(texto):
    """Intenta parsear un string de fecha. Devuelve datetime o None."""
    if not texto:
        return None
    # ISO 8601: 2025-01-15 o 2025-01-15T10:30:00...
    m = re.search(r'(\d{4}-\d{2}-\d{2})', texto)
    if m:
        try:
            return datetime.strptime(m.group(1), '%Y-%m-%d')
        except:
            pass
    # DD/MM/YYYY o DD-MM-YYYY
    m = re.search(r'(\d{1,2})[/\-](\d{1,2})[/\-](\d{4})', texto)
    if m:
        dia, mes, anio = m.groups()
        try:
            return datetime(int(anio), int(mes), int(dia))
        except:
            pass
    # Fecha en español: "15 de enero de 2025"
    meses_es = {
        'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4,
        'mayo': 5, 'junio': 6, 'julio': 7, 'agosto': 8,
        'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12
    }
    m = re.search(r'(\d{1,2})\s+de\s+(\w+)\s+(?:de\s+)?(\d{4})', texto.lower())
    if m:
        dia, mes_str, anio = m.groups()
        mes = meses_es.get(mes_str)
        if mes:
            try:
                return datetime(int(anio), mes, int(dia))
            except:
                pass
    return None

def filtrar_recientes(lista, meses=2):
    """Descarta noticias con fecha parseada anterior a `meses` meses atrás.
    Items sin fecha parseable se conservan (se asume que son recientes)."""
    limite = datetime.now() - timedelta(days=meses * 30)
    resultado = []
    for item in lista:
        fecha_dt = parsear_fecha_iso(item.get('fecha_iso') or item.get('fecha', ''))
        if fecha_dt is None or fecha_dt >= limite:
            resultado.append(item)
    return resultado

def evento_es_proximo(texto):
    hoy = datetime.now()
    limite = hoy + timedelta(days=60)
    meses = {
        'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4,
        'mayo': 5, 'junio': 6, 'julio': 7, 'agosto': 8,
        'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12
    }
    for nombre, numero in meses.items():
        if nombre in texto.lower():
            try:
                fecha = datetime(hoy.year, numero, 1)
                if hoy <= fecha <= limite:
                    return True
            except:
                pass
    return False

def deduplicar(lista):
    vistos = set()
    resultado = []
    for item in lista:
        url = item.get("url", "")
        if any(s in url for s in SECCIONES_EXCLUIDAS_URL):
            continue
        k = item["titulo"][:80].lower()
        if k not in vistos and len(item["titulo"]) > 5:
            if item.get("es_danza") or es_de_danza(item["titulo"] + " " + item["descripcion"]):
                vistos.add(k)
                resultado.append(limpiar_item(item))
    return resultado

def mezclar(listas):
    todos = []
    for lista in listas:
        todos.extend(lista)
    random.shuffle(todos)
    return todos
