# PROGRESO — Danza Argentina App

## Estado actual: deployado en Koyeb (2026-03-01)
URL: https://guilty-sheila-kathryn-danzig-0b1aa800.koyeb.app

**Conteo en vivo (2026-03-01):**
- Eventos tab: ~15 (8 base + 7 CC Borges hardcoded)
- Tango tab: ~17 (Hoy Milonga)
- Noticias: ~38
- Convocatorias: ~40

---

## Scrapers de eventos (scrapers.py)

| Fuente | Estado Koyeb | Método | Imagen | Notas |
|---|---|---|---|---|
| CIAD | ✅ ~9 items | fetch_stealth (patchright) | No | |
| BA Ciudad | ✅ ~6 items | httpx JSON API | No | API: `/api/v1/eventos?categoria=danza&page={n}` |
| Palacio Libertad | ❌ 0 items | fetch_simple | No | Funciona local, falla en Koyeb — pendiente |
| Alternativa Teatral | ✅ ~4 items | fetch_simple | Sí | |
| Teatro Colón | ✅ ~6 items | fetch_simple | No | |
| CC Borges | ❌ 0 scraped | cloudscraper | Sí | Cloudflare bloquea IP Koyeb (datacenter). **Ver respaldo hardcoded.** |
| Usina del Arte | ❌ 0 items | fetch_stealth | No | Pendiente investigar |
| CC Recoleta | ❌ 0 items | fetch_simple | No | 0 eventos de danza actuales (filtra por `#Danza`) |
| Cultura Nación | ✅ ~1-5 items | fetch_simple | Sí | `cultura.gob.ar/agenda/filtro/?categoria=danza` |
| Hoy Milonga | ✅ ~17 items | fetch_simple | Sí | tipo forzado "tango" |
| CTBA Agenda | ✅ ~4 items | fetch_simple | No | Próximos 7 días en paralelo |

### CC Borges — respaldo hardcodeado (main.py)
- Cloudflare bloquea IP de Koyeb sin solución gratuita
- 8 eventos hardcodeados con `es_danza: True` y fecha
- Se filtran automáticamente cuando `fecha < hoy`
- **Recordatorio: actualizar el 2026-03-08** (o cuando expiren los eventos de abril)
- Última actualización: 2026-03-01

---

## Scrapers de noticias (scrapers.py)

| Fuente | Estado | Imagen | Fecha | Notas |
|---|---|---|---|---|
| Balletín Dance | ✅ ~10 items | Sí | `pubDate` RSS | Migrado a RSS feed — bypasea Cloudflare. |
| Perfil | ⚠️ filtrado | Sí (srcset) | `<span class="date-time">` | Artículos de 2023-2024 → descartados por filtro 2 meses |
| Clarín | ⚠️ filtrado | Sí | `<time>` | Ídem Perfil |
| Página 12 | ✅ ~10 items | No | — | |
| Diario Uno | ⚠️ 0 items | — | — | Pendiente |
| TN | ⚠️ 0 items | — | — | Pendiente |
| El Destape | ✅ ~102 items | — | — | Muchos items, cap en 10 |
| Río Negro | ✅ ~26 items | — | — | |
| Tiempo Sur | ✅ ~64 items | — | — | |
| Diario Democracia | ✅ ~54 items | — | — | |
| El1 Digital | ⚠️ 0 items | — | — | Pendiente |
| La Nación | ❌ 0 items | — | — | URL `/tags/danza/` da 404 — URL correcta desconocida |
| Infobae | ✅ ~6 items | — | — | |

**Cap por fuente:** 10 items antes de mezclar.
**Filtro antigüedad:** `filtrar_recientes(meses=2)` — items sin fecha parseable se conservan.

---

## Scrapers de convocatorias (scrapers_convocatorias.py)

| Fuente | Estado | Subtipo |
|---|---|---|
| Alt Teatral Castings | ✅ ~17 items | casting/audición |
| Alt Teatral Conv | ✅ ~4 items | variado |
| Recursos Culturales | ✅ ~7 items | beca/subsidio/residencia |
| Teatro Cervantes | ✅ ~2 items | audición (bailarines) |
| Balletín Dance | ✅ ~13 items | audición/beca |

---

## Arquitectura general

```
Startup → scrape() en paralelo → globals (eventos, noticias, convocatorias)
asyncio.create_task(scraper_loop()) → refresca cada 24hs en background sin downtime
Cliente → GET / → HTML (frontend.py) → JS fetch /api/* → renderiza tarjetas
```

### Stack de scraping
- `patchright` (fork anti-bot de playwright): CIAD y fetch_stealth
- `httpx`: HTTP simple y APIs JSON
- `fetch_simple`: httpx con headers, timeout 30s
- `fetch_stealth`: patchright headless, domcontentloaded + wait_selector
- `cloudscraper`: CC Borges (devuelve 403 en Koyeb — se usa respaldo hardcoded)

### Datos de respaldo (main.py)
- `EVENTOS_BORGES_RESPALDO` — 8 items de CC Borges con fecha, filtro automático por vencimiento
- `NOTICIAS_RESPALDO` — 3 items hardcoded, fallback cuando noticias scraped = vacío

### Deduplicación
- Por `titulo[:80].lower()`
- Límites: eventos 50, noticias 50, convocatorias 50

### Filtro de antigüedad (noticias)
- `filtrar_recientes(lista, meses=2)` en utils.py
- Parsea fechas: ISO 8601, DD/MM/YYYY, DD-MM-YYYY, "15 de enero de 2025"
- Items sin fecha parseable se conservan

---

## Disciplinas / tipos

- **clásica** — ballet, ópera-ballet, pas de deux
- **folklórica** — malambo, zamba, chacarera
- **contemporánea** — experimental, escénica, coreografía (fallback)
- **tango** — tango, milonga, bandoneón, tango escenario

Detección en `detectar_tipo()` (utils.py): orden tango → clásica → folklórica → contemporánea.

---

## Frontend (frontend.py)

- Stack: HTML/CSS/JS inline como string Python
- Fuentes: Playfair Display (serif, títulos) + Plus Jakarta Sans (body)
- Colores: fondo `#050505`, cards `#111`, acento `#ff3c3c`
- Layout: sidebar 260px fijo + contenido en grid
- **4 pestañas:** Eventos (default) | Tango y Milongas | Convocatorias | Prensa
- Filtros disciplina en sidebar: Todo / Clásica / Folklórica / Contemporánea
- Tarjeta con imagen: `<img class="card-thumb">` + placeholder de fallback si falla

---

## SEO implementado

- Title: "Danza Argentina | Agenda de Ballet, Folklore y Danza Contemporánea en Buenos Aires"
- Meta description, keywords expandidos
- JSON-LD structured data: WebSite + Organization + WebPage schemas
- H1 oculto visualmente pero indexable
- Meta geo: `AR-C`, Buenos Aires
- Canonical URL dinámica via `BASE_URL` env var
- Sitemap con `<lastmod>` dinámico
- Bot detection: crawlers reciben HTML semántico con eventos en vez del SPA

---

## Deploy

- **Plataforma:** Koyeb (gratis, sin sleep)
- **URL:** https://guilty-sheila-kathryn-danzig-0b1aa800.koyeb.app
- **Repo:** https://github.com/Amb-canicus/danza-argentina
- **Dockerfile:** patchright + chromium instalado para scrapers headless

### Para correr localmente
```bash
cd /home/sor/Documentos/Proyectos-web/Danza-app
source venv/bin/activate
uvicorn main:app --reload > /tmp/danza-app.log 2>&1 &
xdg-open http://127.0.0.1:8000
```

---

## Pendiente (próxima sesión)

### Prioridad alta
- [ ] **Dominio personalizado** — agregar dominio a Koyeb
- [ ] **Palacio Libertad** — funciona local, devuelve 0 en Koyeb (¿JS? ¿IP bloqueada?)
- [ ] **Usina del Arte** — siempre 0 items, investigar

### Fuentes nuevas a agregar
| Fuente | URL | Tipo | Estado |
|---|---|---|---|
| ~~Cultura Nación~~ | cultura.gob.ar/agenda/filtro/?categoria=danza | Eventos | ✅ Agregado (2026-03-02) |
| La Nación danza | lanacion.com.ar | Noticias | Pendiente — URL correcta desconocida |

### Fuentes descartadas (investigadas)
| Fuente | Motivo |
|---|---|
| Danzahoy (danzahoy.com) | Sitio español, no argentino |
| CCK | Es el mismo sitio que Palacio Libertad (ya tenemos scraper) |
| FIBA | Festival bienal, sin listado de eventos activo entre ediciones |
| ProDanza CABA | Solo links a convocatorias 2022/2023, sin estructura scraeable actual |
| Fondo Nacional de las Artes | 1 item de danza de 2024, no actualiza regularmente |
| Teatro Argentino LP | Programación hardcodeada en HTML, sigue mostrando diciembre 2024 |

### Problemas conocidos
- **Balletín Dance noticias**: devuelve 0 — investigar selector
- **La Nación**: URL de sección danza desconocida (`/tags/danza/` da 404)
- **TN y El1 Digital**: 0 items — investigar
- **Perfil/Clarín**: archivo de danza muy viejo, filtro 2 meses los descarta casi siempre
