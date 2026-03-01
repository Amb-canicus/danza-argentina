# SEO — Danza Argentina

Documentación exhaustiva de mejoras SEO. Investigación realizada en marzo 2026.

---

## Estado actual (ya implementado)

- `<title>` con keywords: "Danza Argentina | Agenda de Ballet, Folklore y Danza Contemporánea en Buenos Aires"
- `<meta description>` descriptivo
- `<meta name="keywords">` (ignorado por Google desde 2009, no hace daño)
- `lang="es"` en `<html>`, `og:locale: es_AR`
- `geo.region: AR-C`, `geo.placename: Buenos Aires, Argentina`
- Schema.org: `WebSite`, `Organization`, `WebPage`
- `<link rel="canonical">`
- `<meta name="robots" content="index, follow">`
- Open Graph: type, title, description, url, locale, site_name — **sin og:image**
- Twitter card: title, description — **sin twitter:image**
- `/sitemap.xml` con solo la URL raíz
- `preconnect` a Google Fonts

---

## Problemas críticos

### 1. Contenido JS-rendered invisible para Google

**El problema más grave.** El HTML de `/` contiene divs vacíos:

```html
<div id="lista-eventos" class="cards-grid"></div>
<div id="lista-noticias" class="cards-grid"></div>
<div id="lista-convocatorias" class="conv-grid"></div>
```

El contenido llega vía `fetch('/api/*')` después de carga. Googlebot tiene dos pasadas: primero indexa el HTML estático, luego encola el render JS, que puede demorar días. Para un agregador de eventos con contenido diario, cuando Google finalmente renderiza la página los eventos ya expiraron. El contenido es esencialmente invisible en búsquedas temporales.

**Solución: Dynamic Rendering**

Detectar si el visitante es un bot y servirle HTML pre-renderizado con contenido real. Es la solución oficial de Google para SPAs. No es cloaking porque el contenido es idéntico.

En `main.py`:

```python
from fastapi import Request

BOT_USER_AGENTS = [
    "googlebot", "bingbot", "slurp", "duckduckbot", "baiduspider",
    "yandexbot", "applebot", "twitterbot", "linkedinbot",
    "whatsapp", "telegrambot", "discordbot", "facebot",
]

def es_bot(request: Request) -> bool:
    ua = request.headers.get("user-agent", "").lower()
    return any(bot in ua for bot in BOT_USER_AGENTS)

def generar_html_bot() -> str:
    """HTML semántico con contenido real para crawlers."""
    import json

    def schema_eventos(items):
        return {
            "@context": "https://schema.org",
            "@type": "ItemList",
            "name": "Agenda de Danza en Buenos Aires",
            "numberOfItems": len(items),
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
                } for i, ev in enumerate(items)
            ]
        }

    arts_ev   = "".join(f'<article><h2><a href="{e["url"]}">{e["titulo"]}</a></h2><p>{e.get("descripcion","")}</p><p>{e["fuente"]} — {e.get("fecha","")}</p></article>' for e in eventos[:20])
    arts_conv = "".join(f'<article><h2><a href="{c["url"]}">{c["titulo"]}</a></h2><p>{c.get("descripcion","")}</p><p>{c.get("subtipo","")} — {c["fuente"]}</p></article>' for c in convocatorias[:15])
    arts_no   = "".join(f'<article><h2><a href="{n["url"]}">{n["titulo"]}</a></h2><p>{n.get("descripcion","")}</p><p>{n["fuente"]} — {n.get("fecha","")}</p></article>' for n in noticias[:10])

    schema_json = json.dumps(schema_eventos(eventos[:20]), ensure_ascii=False)

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>Agenda de Danza en Argentina | Ballet, Folklore y Contemporánea en Buenos Aires</title>
<meta name="description" content="La agenda más completa de danza en Argentina. Eventos de ballet, folklore, tango y contemporánea en Buenos Aires. Convocatorias, audiciones y becas.">
<meta name="robots" content="index, follow">
<link rel="canonical" href="https://danza-argentina.up.railway.app/">
<script type="application/ld+json">{schema_json}</script>
</head>
<body>
<h1>Agenda de Danza en Argentina — Ballet, Folklore y Contemporánea en Buenos Aires</h1>
<section><h2>Eventos de Danza en Buenos Aires</h2>{arts_ev}</section>
<section><h2>Audiciones, Becas y Castings de Danza Argentina</h2>{arts_conv}</section>
<section><h2>Noticias de Danza en Argentina</h2>{arts_no}</section>
</body>
</html>"""

# Reemplazar el @app.get("/") en main.py:
@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    if es_bot(request):
        return HTMLResponse(content=generar_html_bot())
    importlib.reload(frontend)
    return frontend.HTML
```

**Prioridad: ALTA | Esfuerzo: MEDIO | Impacto: MUY ALTO**

---

### 2. Sin og:image ni twitter:image

Al compartir en WhatsApp, Twitter, Telegram, LinkedIn: aparece texto sin imagen. Las publicaciones con imagen tienen hasta 3x más engagement.

**Crear la imagen:**

```python
# crear_og_image.py — ejecutar una sola vez
from PIL import Image, ImageDraw, ImageFont
import os

img = Image.new('RGB', (1200, 630), color=(5, 5, 5))
draw = ImageDraw.Draw(img)
draw.rectangle([0, 0, 8, 630], fill=(255, 60, 60))  # línea acento

try:
    font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf", 96)
    font_sub   = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 36)
except:
    font_title = font_sub = ImageFont.load_default()

draw.text((80, 200), "DANZA",     fill=(255, 60, 60),    font=font_title)
draw.text((80, 310), "ARGENTINA", fill=(255, 255, 255),  font=font_title)
draw.text((80, 450), "Agenda de Ballet, Folklore y Contemporánea", fill=(136, 136, 136), font=font_sub)
draw.text((80, 500), "Buenos Aires, Argentina", fill=(85, 85, 85), font=font_sub)

os.makedirs("static", exist_ok=True)
img.save("static/og-image.png", "PNG", optimize=True)
```

**Agregar en `main.py`:**

```python
from fastapi.staticfiles import StaticFiles
app.mount("/static", StaticFiles(directory="static"), name="static")
```

**Agregar en `frontend.py` (en el `<head>`):**

```html
<meta property="og:image" content="https://danza-argentina.up.railway.app/static/og-image.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Danza Argentina — Agenda de Ballet, Folklore y Contemporánea en Buenos Aires">
<meta name="twitter:image" content="https://danza-argentina.up.railway.app/static/og-image.png">
<meta name="twitter:image:alt" content="Danza Argentina — Agenda de Ballet, Folklore y Contemporánea en Buenos Aires">
```

**Prioridad: ALTA | Esfuerzo: BAJA | Impacto: ALTO (redes sociales)**

---

### 3. Sin robots.txt — bots rastrean /api/

Sin `robots.txt`, Googlebot indexa `/api/eventos`, `/api/noticias`, `/api/convocatorias` como páginas con JSON. Duplican el contenido, consumen crawl budget, y `/api/refrescar` podría disparar un re-scraping completo si Google lo llama.

**Agregar en `main.py`:**

```python
@app.get("/robots.txt")
def robots_txt():
    content = """User-agent: *
Allow: /
Disallow: /api/

Sitemap: https://danza-argentina.up.railway.app/sitemap.xml
"""
    return Response(content=content, media_type="text/plain")
```

**Prioridad: ALTA | Esfuerzo: MUY BAJA | Impacto: MEDIO**

---

### 4. Sin favicon — 404 en cada carga

El browser pide `/favicon.ico` automáticamente. Sin el archivo: 404 en cada visita, ícono gris genérico en las SERPs de Google (el favicon aparece junto al título desde 2019).

**Agregar en `main.py`:**

```python
@app.get("/favicon.svg")
def favicon_svg():
    svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">
  <rect width="32" height="32" fill="#050505"/>
  <text x="50%" y="55%" font-family="serif" font-size="14" font-weight="bold"
        fill="#ff3c3c" text-anchor="middle" dominant-baseline="middle"
        font-style="italic">DA</text>
</svg>"""
    return Response(content=svg, media_type="image/svg+xml")
```

**Agregar en `frontend.py` (en el `<head>`):**

```html
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
```

**Prioridad: ALTA | Esfuerzo: MUY BAJA | Impacto: MEDIO**

---

### 5. H1 oculto — riesgo de penalización

El H1 actual usa `clip:rect(0,0,0,0)` + `overflow:hidden`, técnica que Google puede interpretar como "hidden text" (keyword stuffing oculto). No es la intención, pero el riesgo existe.

```html
<!-- ACTUAL — riesgoso -->
<h1 style="position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap">
    Agenda de Danza en Argentina...
</h1>
```

**Opciones:**
1. Hacerlo visible e integrarlo al diseño (mejor opción).
2. Reemplazar el clip antiguo por `clip-path: inset(50%)` (patrón `sr-only` moderno, más tolerable para Google).

**Prioridad: MEDIA | Esfuerzo: BAJA**

---

### 6. Schema.org Event — sin rich results de eventos

Google muestra un carrusel especial de eventos en la SERP cuando hay `DanceEvent` / `Event` schema válido. El schema actual solo tiene `WebSite`, `Organization`, `WebPage`. Sin `Event` schema, el sitio no puede aparecer en ese carrusel aunque tenga los mejores eventos.

El código del schema para eventos va dentro de `generar_html_bot()` (ver punto 1). Para que también lo lean los usuarios normales (y redes sociales), se puede inyectar vía JS después de cargar datos:

```javascript
// En la función render() del frontend, agregar al final:
function inyectarSchemaEventos(items) {
    const existing = document.getElementById('schema-eventos');
    if (existing) existing.remove();
    const schema = {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": "Agenda de Danza en Buenos Aires",
        "numberOfItems": items.length,
        "itemListElement": items.slice(0, 10).map((ev, i) => ({
            "@type": "ListItem",
            "position": i + 1,
            "item": {
                "@type": "DanceEvent",
                "name": ev.titulo,
                "description": ev.descripcion || "",
                "url": ev.url,
                "organizer": {"@type": "Organization", "name": ev.fuente},
                "location": {
                    "@type": "Place",
                    "address": {"@type": "PostalAddress", "addressLocality": "Buenos Aires", "addressCountry": "AR"}
                }
            }
        }))
    };
    const script = document.createElement('script');
    script.id = 'schema-eventos';
    script.type = 'application/ld+json';
    script.text = JSON.stringify(schema);
    document.head.appendChild(script);
}
// Llamar dentro de render() después de renderizar eventos
```

**Prioridad: ALTA | Esfuerzo: MEDIO | Impacto: MUY ALTO (rich results)**

---

## Mejoras menores (implementación rápida)

### 7. Sitemap ampliado con secciones

```python
@app.get("/sitemap.xml")
def sitemap():
    hoy = date.today().isoformat()
    base = "https://danza-argentina.up.railway.app"
    urls = [
        (f"{base}/",              "1.0", "daily"),
        (f"{base}/eventos",       "0.9", "daily"),
        (f"{base}/tango",         "0.8", "daily"),
        (f"{base}/convocatorias", "0.8", "daily"),
        (f"{base}/prensa",        "0.7", "weekly"),
    ]
    tags = "".join(f"""
  <url>
    <loc>{loc}</loc>
    <lastmod>{hoy}</lastmod>
    <changefreq>{freq}</changefreq>
    <priority>{prio}</priority>
  </url>""" for loc, prio, freq in urls)
    return Response(
        content=f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{tags}\n</urlset>',
        media_type="application/xml"
    )
```

**Prioridad: ALTA | Esfuerzo: MUY BAJA**

---

### 8. alt text en imágenes de tarjetas

En `frontend.py`, función `crearTarjeta()`:

```javascript
// ACTUAL
`<img class="card-thumb" src="${item.imagen}" alt="">`

// CORREGIR A
`<img class="card-thumb" src="${item.imagen}" alt="${item.titulo}" loading="lazy" decoding="async">`
```

**Prioridad: ALTA | Esfuerzo: MUY BAJA | Doble impacto: SEO + accesibilidad**

---

### 9. H2 de secciones con keywords

```javascript
// ACTUAL
<h2>Eventos</h2>
<h2>Tango y Milongas</h2>
<h2>Convocatorias</h2>
<h2>Prensa</h2>

// MEJORADO
<h2>Agenda de Danza en Buenos Aires</h2>
<h2>Milongas y Eventos de Tango en Buenos Aires</h2>
<h2>Audiciones, Becas y Castings de Danza Argentina</h2>
<h2>Noticias de Danza Argentina</h2>
```

**Prioridad: MEDIA | Esfuerzo: MUY BAJA**

---

### 10. min-height en contenedores (reduce CLS)

Las cards que aparecen de golpe tras el fetch JS causan Cumulative Layout Shift, señal negativa para Core Web Vitals.

```css
/* Agregar al CSS */
#lista-eventos, #lista-noticias, #lista-convocatorias, #lista-tango {
    min-height: 400px;
}
```

**Prioridad: MEDIA | Esfuerzo: MUY BAJA**

---

### 11. areaServed en Organization schema

```json
{
  "@type": "Organization",
  "@id": "https://danza-argentina.up.railway.app/#organization",
  "name": "Danza Argentina",
  "url": "https://danza-argentina.up.railway.app/",
  "description": "Agregador de eventos, noticias y convocatorias de danza clásica, folklórica y contemporánea en Argentina.",
  "areaServed": {
    "@type": "City",
    "name": "Buenos Aires",
    "sameAs": "https://www.wikidata.org/wiki/Q1486"
  },
  "knowsAbout": ["Ballet", "Danza Contemporánea", "Folklore Argentino", "Tango"],
  "inLanguage": "es-AR"
}
```

**Prioridad: MEDIA | Esfuerzo: MUY BAJA**

---

### 12. BASE_URL como variable de entorno

El canonical y las URLs del schema están hardcodeadas. Riesgo cuando se cambie de Railway a Koyeb o dominio propio.

```python
# En main.py
import os
BASE_URL = os.getenv("BASE_URL", "https://danza-argentina.up.railway.app")
```

Inyectarlo en el HTML y el sitemap. En Koyeb, configurar `BASE_URL=https://nuevo-dominio.com`.

**Prioridad: MEDIA | Esfuerzo: BAJA**

---

## Mejoras de arquitectura (mediano plazo)

### 13. History API routing — URLs indexables por sección

Actualmente toda la app vive en `/`. Google no puede indexar la sección de convocatorias por separado porque no existe como URL.

**Frontend JS:**
```javascript
function cambiarVista(nombre, btn) {
    vistaActiva = nombre;
    history.pushState({ seccion: nombre }, '', '/' + (nombre === 'eventos' ? '' : nombre));
    // ... resto igual
}

window.addEventListener('popstate', (e) => {
    const seccion = e.state?.seccion || 'eventos';
    // restaurar vista
});

// Al iniciar, leer sección de la URL
const seccionInicial = window.location.pathname.replace('/', '') || 'eventos';
if (['tango', 'convocatorias', 'prensa'].includes(seccionInicial)) {
    cambiarVista(seccionInicial, document.querySelector(`[onclick*="'${seccionInicial}'"]`));
}
```

**Backend FastAPI:**
```python
SECCIONES_VALIDAS = {"eventos", "tango", "convocatorias", "prensa"}

@app.get("/{seccion}", response_class=HTMLResponse)
def vista_seccion(request: Request, seccion: str):
    if seccion not in SECCIONES_VALIDAS:
        return HTMLResponse(status_code=404)
    if es_bot(request):
        return HTMLResponse(content=generar_html_seccion(seccion))
    importlib.reload(frontend)
    return frontend.HTML
```

**Prioridad: MEDIA | Esfuerzo: MEDIO**

---

### 14. Font auto-hosting (mejora LCP)

Las fuentes de Google Fonts son render-blocking. Auto-hospedarlas elimina la dependencia externa y mejora el LCP (Largest Contentful Paint).

1. Descargar desde [google-webfonts-helper.herokuapp.com](https://gwfh.mranftl.com/fonts)
2. Guardar en `static/fonts/`
3. Reemplazar el `<link>` de Google Fonts por `@font-face` local con `font-display: swap`

**Prioridad: MEDIA | Esfuerzo: MEDIA**

---

### 15. JobPosting schema para convocatorias

Las convocatorias de tipo casting/audición mapean a `JobPosting` en Schema.org. Google puede mostrar rich results específicos para ofertas de trabajo artístico.

```python
def generar_schema_convocatorias(items: list) -> dict:
    from datetime import datetime, timedelta
    return {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": "Convocatorias de Danza Argentina",
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": i + 1,
                "item": {
                    "@type": "JobPosting",
                    "title": cv["titulo"],
                    "description": cv.get("descripcion", ""),
                    "url": cv["url"],
                    "datePosted": datetime.now().strftime("%Y-%m-%d"),
                    "validThrough": (datetime.now() + timedelta(days=90)).strftime("%Y-%m-%d"),
                    "hiringOrganization": {"@type": "Organization", "name": cv["fuente"]},
                    "jobLocation": {
                        "@type": "Place",
                        "address": {"@type": "PostalAddress", "addressLocality": "Buenos Aires", "addressCountry": "AR"}
                    }
                }
            } for i, cv in enumerate(items[:10])
        ]
    }
```

**Prioridad: MEDIA | Esfuerzo: MEDIA**

---

## Estrategia de keywords

### Keywords de alta oportunidad

Las de **intento transaccional** son las más valiosas — quien las busca necesita exactamente lo que el sitio ofrece, y la competencia es baja:

| Keyword | Intento | Competencia |
|---------|---------|-------------|
| `audiciones ballet argentina` | Transaccional | Baja |
| `casting bailarines contemporáneos` | Transaccional | Muy baja |
| `becas danza argentina 2026` | Transaccional | Muy baja |
| `convocatorias danza contemporánea` | Transaccional | Baja |
| `subsidio danza ministerio cultura` | Transaccional | Muy baja |
| `milongas hoy buenos aires` | Informacional urgente | Baja |
| `agenda danza buenos aires` | Informacional | Media |
| `espectáculos ballet buenos aires` | Informacional | Media |

### Long-tail por sección

**Eventos:**
- `espectáculos de danza contemporánea en buenos aires este fin de semana`
- `ballet gratis buenos aires`
- `agenda usina del arte danza`
- `cc borges danza agenda`

**Tango:**
- `milongas en palermo hoy`
- `milongas en san telmo`
- `donde bailar tango en buenos aires`
- `milonga para principiantes buenos aires`

**Convocatorias:**
- `audicion ballet colon`
- `beca danza ministerio cultura argentina`
- `residencia artística danza argentina`
- `concurso coreográfico argentina 2026`

### Términos específicos argentinos que deben aparecer en el sitio

Para señalar autoridad temática:

**Instituciones:** Teatro Colón, Teatro San Martín, Palacio Libertad, CC Borges, Usina del Arte, CC Recoleta, IUNA/UNA, CTBA, CIAD, Fundación Julio Bocca

**Festivales:** Festival Buenos Aires Tango, Festival de Malambo de Laborde, Festival Nacional de Folklore Cosquín

**Disciplinas locales:** malambo, chacarera sureña, zamba, tango escenario, tango de pista, milonguero, danzas nativas, folklore escénico

**Vocabulario profesional:** convocatoria abierta, llamado a audición, becario, residente artístico, ensamble de danza, danza-teatro

---

## Análisis de competidores

| Sitio | Fortaleza SEO | Brecha explotable |
|-------|--------------|-------------------|
| **alternativateatral.com** | Alta autoridad, URLs por obra, miles de páginas | Su sección danza mezcla con teatro/cine; no es especialista |
| **balletindance.com** | Contenido editorial largo, antigüedad, keywords de ballet clásico | No tienen tango, no agregan múltiples fuentes, sin agenda unificada |
| **recursosculturales.com** | Rankea para "convocatorias culturales" genéricas | Mezcla música, artes plásticas, teatro; no filtra por danza |
| **Teatro Colón / San Martín** | Altísima autoridad de dominio | Solo muestran su propio contenido — nadie los agrega todos juntos |

**Diferencial único de Danza Argentina:** Es el único sitio que agrega contenido de múltiples instituciones (Colón, San Martín, CIAD, Usina, CC Borges, etc.) en una sola interfaz filtrada por disciplina.

---

## Acciones off-page (trabajo humano, no de código)

### Backlinks de alta prioridad
1. **Google Search Console** — registrar el sitio en cuanto esté en producción. Sin esto, nada de lo anterior sirve.
2. **Dominio propio** — `danzaargentina.com.ar` o `agendadanza.com.ar` en NIC.ar (~$150-200 ARS/año). Los `.com.ar` tienen señal geográfica preferida por Google para búsquedas desde Argentina.
3. **Outreach a 10-15 escuelas de danza** — email simple: "Agregamos sus eventos automáticamente. ¿Nos linkean en su sección de recursos?" El intercambio de valor es claro.
4. **Instagram de @danzaargentina** — post semanal con convocatorias destacadas (imagen simple con 5 bullets), link a la web. Alta utilidad para bailarines, fácil de compartir.
5. **Grupos de Facebook de milonga** — publicar agenda de milongas cuando hay actualizaciones.

### Contenido educativo (largo plazo, mayor impacto SEO)
Nadie en Argentina tiene páginas bien optimizadas sobre:
- "Qué es el malambo" (pico de búsquedas después de Laborde)
- "Cómo hacer una audición de ballet en Argentina"
- "Festivales de danza en Argentina: calendario anual"
- "Historia del tango en Buenos Aires"
- "Cómo ingresar al Ballet Estable del Colón"

Este contenido evergreen atrae links naturales de escuelas, blogs de padres de alumnas de ballet, foros de tango. No caduca y puede rankear por años.

---

## Plan de implementación

### Sprint 1 — Un día, sin riesgo de romper nada
1. `robots.txt` (5 min)
2. Favicon SVG (10 min)
3. Sitemap ampliado con secciones (10 min)
4. `alt="${item.titulo}"` + `loading="lazy"` en imágenes (5 min)
5. `min-height: 400px` en contenedores (2 min)
6. og:image + twitter:image (crear imagen con Pillow + agregar meta tags) (30 min)
7. `areaServed` en Organization schema (5 min)

### Sprint 2 — Cambios sustanciales
8. Dynamic rendering para bots (detección de User-Agent + `generar_html_bot()`) (2-3h)
9. DanceEvent / ItemList schema inyectado en HTML estático para bots (incluido en punto 8)
10. `BASE_URL` como variable de entorno (30 min)
11. H2 de secciones con keywords (10 min)

### Sprint 3 — Refactor de routing
12. History API routing (`/eventos`, `/tango`, `/convocatorias`, `/prensa`) (3-4h)
13. H1 visible integrado al diseño (variable)
14. Font auto-hosting (1-2h)

### Sprint 4 — Largo plazo
15. JobPosting schema para convocatorias
16. Páginas por disciplina (`/ballet/`, `/tango/`, etc.)
17. Páginas por venue (Teatro Colón, San Martín, etc.)
18. Contenido editorial/glosario

---

## Tabla resumen de prioridades

| # | Mejora | Prioridad | Esfuerzo | Impacto |
|---|--------|-----------|----------|---------|
| 1 | Dynamic rendering (bots ven contenido real) | **ALTA** | Medio | Muy alto |
| 2 | DanceEvent schema en HTML para bots | **ALTA** | Medio | Muy alto (rich results) |
| 3 | og:image + twitter:image | **ALTA** | Bajo | Alto (redes sociales) |
| 4 | robots.txt | **ALTA** | Muy bajo | Medio |
| 5 | Favicon SVG | **ALTA** | Muy bajo | Medio |
| 6 | alt text en imágenes + lazy loading | **ALTA** | Muy bajo | Alto (SEO + accesibilidad) |
| 7 | Sitemap con secciones | **ALTA** | Muy bajo | Medio |
| 8 | H2 con keywords | **MEDIA** | Muy bajo | Medio |
| 9 | min-height contenedores (CLS) | **MEDIA** | Muy bajo | Medio |
| 10 | areaServed en Organization | **MEDIA** | Muy bajo | Bajo |
| 11 | BASE_URL como variable de entorno | **MEDIA** | Bajo | Bajo (mantenibilidad) |
| 12 | H1 visible | **MEDIA** | Bajo | Bajo-medio |
| 13 | History API routing | **MEDIA** | Medio | Alto |
| 14 | Font auto-hosting | **MEDIA** | Medio | Medio (LCP) |
| 15 | JobPosting schema convocatorias | **MEDIA** | Medio | Alto (rich results) |
| 16 | Registrar en Google Search Console | **ALTA** | Muy bajo | **Requisito para todo lo demás** |
| 17 | Dominio .com.ar propio | **MEDIA** | Muy bajo ($) | Alto (señal geolocalización) |
| 18 | Outreach a escuelas de danza | **MEDIA** | Alto (tiempo) | Alto (backlinks) |
| 19 | Contenido educativo/glosario | **BAJA** | Alto | Muy alto (largo plazo) |
| 20 | hreflang | **NO aplica** | — | Solo si hubiera versión en otro idioma |
| 21 | News sitemap | **NO aplica** | — | Solo para contenido editorial propio |
| 22 | AMP | **NO aplica** | — | Solo para contenido editorial propio |

---

*Documento generado: marzo 2026. Revisar anualmente — las prácticas SEO de Google evolucionan.*
