# Sección "Talleres / Formación" — Investigación previa

Investigado el 2026-03-02. Todavía no implementado.

---

## Concepto

Sección nueva en la app para listar talleres, cursos y programas de formación en danza en Argentina.
Posible nombre: **"Formación"** (cubre talleres + audiciones/inscripciones que ya están en Convocatorias).

---

## Fuentes verificadas y scraperables

### ✅ Rojas UBA — PRIORIDAD ALTA
- **URL:** `https://www.rojas.uba.ar/cursos/categoria/danza`
- **Método:** `fetch_stealth` + `wait_selector='.card'`
- **Items actuales:** 6 cursos de danza
- **Campos disponibles:**
  - Título completo: `a.card__title[title]`
  - Descripción completa: `p.card__long-description[title]`
  - Docente + cantidad de clases: `p.italic` → ej. "6 clases / Capacita: Laura Kahan"
  - Horario: `p.mb-2.uppercase span` → ej. "miércoles de 18:30 a 20:30"
  - Imagen: `div[style*=background-image]` → regex `url("...")`
  - URL: `a.card__title[href]`
- **Cursos actuales:**
  - Coreografía + Investigación del Movimiento (Laura Kahan, miércoles 18:30)
  - Danza contemporánea: poesía del cuerpo (Susana Szperling, martes 18:00)
  - Danza contemporánea. Seminario (Pablo Castronovo, martes y jueves 20:00)
  - Danza digital. Poéticas de danza en la dimensión digital (Dina Schonhaut, viernes 18:00)
  - Prácticas para el bienestar. Conexión, alineamiento y estiramiento corporal
  - Tai chi - Chi Kung
- **Notas:** JS-rendered (Vue.js). Funciona con patchright. Actualiza por cuatrimestre.

```python
# Scraper para scrapers.py (tipo "taller")
@taller("Rojas UBA")
async def scrapear_rojas_uba():
    page = await fetch_stealth('https://www.rojas.uba.ar/cursos/categoria/danza', wait_selector='.card')
    soup = BeautifulSoup(page.html_content, 'html.parser')
    encontrados = []
    for card in soup.select('.card'):
        titulo_tag = card.select_one('a.card__title')
        if not titulo_tag: continue
        titulo = titulo_tag.get('title', '') or limpiar(titulo_tag.get_text())
        if len(titulo) < 5: continue
        desc_tag = card.select_one('p.card__long-description')
        desc = desc_tag.get('title', '') or limpiar(desc_tag.get_text()) if desc_tag else titulo
        docente_tag = card.select_one('p.italic')
        horario_tag = card.select_one('p.mb-2.uppercase span')
        docente = limpiar(docente_tag.get_text()) if docente_tag else ''
        horario = limpiar(horario_tag.get_text()) if horario_tag else ''
        link = titulo_tag.get('href', '')
        if link.startswith('//'): link = 'https://www.rojas.uba.ar' + link[1:]
        elif link.startswith('/'): link = 'https://www.rojas.uba.ar' + link
        img_div = card.select_one('div[style*=background-image]')
        imagen = None
        if img_div:
            m = re.search(r'url\(["\']?(.*?)["\']?\)', img_div.get('style', ''))
            if m: imagen = m.group(1)
        encontrados.append({
            "titulo": titulo[:120],
            "descripcion": f"{horario} | {docente} | {desc}"[:300] if horario else f"{docente} | {desc}"[:300],
            "tipo": detectar_tipo(titulo + ' ' + desc),
            "fuente": "Rojas UBA",
            "url": link,
            "fecha": horario,
            **({"imagen": imagen} if imagen else {}),
        })
    return encontrados
```

---

### ✅ Hoy Milonga — Escuelas de Tango
- **URL:** `https://www.hoy-milonga.com/buenos-aires/es/catalog/tango_school`
- **Método:** `fetch_simple`
- **Items actuales:** 13 escuelas de tango
- **Selector:** `a.bg-white` (mismo patrón que milongas/encuentros)
- **Campos:** nombre, foto, link al perfil de la escuela
- **Notas:** Tango exclusivo. Complementa la pestaña Tango. Podría ir en Tango, no en Formación.

---

### ✅ CTBA — Taller de Danza Contemporánea del Teatro San Martín
- **URL:** `https://complejoteatral.gob.ar/ver/taller_de_danza_contemporenea_del_teatro_san_martin`
- **Método:** `fetch_simple`
- **Items:** 1 (programa anual, trienal, gratuito)
- **Notas:** Descripción estática del programa. Inscripción ciclo 2025/2026. Muy prestigioso.
  Solo vale como ítem fijo, no como listado dinámico.

---

### ⚠️ Palacio Libertad — Talleres
- **URL:** `https://palaciolibertad.gob.ar/talleres/`
- **Método:** necesita investigación (actualmente falla en Koyeb por JS)
- **Notas:** Cuando resolvamos Palacio Libertad en Koyeb, los talleres vendrían solos.

---

### ⚠️ Alternativa Teatral — Talleres
- **URL:** `http://www.alternativateatral.com/buscar.asp?objetivo=talleres&texto=danza`
- **Método:** `fetch_simple` (mismo que eventos)
- **Items actuales:** 0 items de danza (variable según temporada)
- **Notas:** En temporada puede tener talleres. Agregar como fuente de oportunidad.

---

## Fuentes descartadas

| Fuente | Motivo |
|---|---|
| CC Recoleta talleres | SSL error (http/https mismatch) |
| ARTEINFORMADO | Items de 2023/2024, no actualiza |
| Cultura Nación talleres | 0 items actuales |
| BA Ciudad API `?tipo=taller` | Devuelve eventos genéricos, no filtra talleres reales |
| Escuelas individuales (SP Dance, Full Dance, etc.) | Muchas para mantener, actualizan poco |
| Fuentes del interior (Rosario, Tucumán, etc.) | Solo 1-2 novedades por año |
| Rojas UBA (primera investigación) | Error: solo probé con fetch_simple, funciona con fetch_stealth ✅ |

---

## Arquitectura propuesta para la sección

```python
# scrapers.py — nuevo decorador
SCRAPERS_TALLERES = []

def taller(nombre):
    def decorator(fn):
        SCRAPERS_TALLERES.append({"nombre": nombre, "fn": fn})
        return fn
    return decorator
```

```python
# main.py — nuevo endpoint
@app.get("/api/talleres")
async def get_talleres():
    return talleres  # global, igual que eventos/noticias/convocatorias
```

```python
# frontend.py — nueva pestaña
# Pestaña 5: "Formación" (o integrar en Convocatorias como subtipo)
```

**Subtipo propuesto para items:**
- `taller_intensivo` — talleres de días/semanas
- `curso_regular` — cuatrimestral o semanal (Rojas UBA, etc.)
- `programa` — ciclos multianuales (CTBA, Colón)

---

## Próximos pasos

1. Implementar decorador `@taller` en scrapers.py
2. Agregar scraper de Rojas UBA (código listo arriba)
3. Decidir si es pestaña propia o se integra en Convocatorias
4. Agregar más fuentes a medida que aparezcan
