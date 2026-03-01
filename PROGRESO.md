# PROGRESO — Danza Argentina App

## Estado actual: en desarrollo local, pendiente deploy

---

## Lo que está implementado

### Scrapers de eventos (scrapers.py)
| Fuente | URL | Imagen |
|---|---|---|
| CIAD | laciad.info/todos-los-eventos.html | No |
| BA Ciudad | buenosaires.gob.ar/descubrir/agenda-2026 | No |
| Palacio Libertad | palaciolibertad.gob.ar/agenda/ | No |
| Alternativa Teatral | alternativateatral.com/buscar.asp?...danza | Sí (del HTML) |
| Teatro Colón | teatrocolon.org.ar/categoria-produccion/ballet/ | No |
| Teatro San Martín | complejoteatral.gob.ar/ver/danza | No |
| CC Borges | centroculturalborges.gob.ar/disciplinas?d=danza | Sí (del HTML) |
| Usina del Arte | usinadelarte.ar/actividades/ | No |
| CC Recoleta | centroculturalrecoleta.org/agenda | No |
| Hoy Milonga | hoy-milonga.com/buenos-aires/es/encuentros | Sí (del HTML) |
| CTBA Agenda | complejoteatral.gob.ar/agenda?fecha=DD-MM-YYYY | No |

**Nota CC Borges:** solo se scrapea la sección `py-5` (próximos). La sección `bg-white` es "lo que pasó" y se excluye.
**Nota Hoy Milonga:** selector `a.bg-white`, tipo forzado "tango", ~19 eventos de festivales y encuentros.
**Nota CTBA Agenda:** scraping de los próximos 7 días en paralelo. Filtra por `es_de_danza()`.
**Nota Teatro San Martín:** WebFetch ve 404 en /ver/danza pero StealthyFetcher headless sí lo renderiza y devuelve ~12 items.

### Scrapers de noticias (scrapers.py)
| Fuente | URL | Imagen | Fecha |
|---|---|---|---|
| Balletín Dance | balletindance.com/ | Sí (lazy-load, quita sufijo WP) | `<time datetime>` (0 items frecuente) |
| Perfil | noticias.perfil.com/seccion/danza | Sí (vía `srcset`) | `<span class="date-time">` DD-MM-YYYY HH:MM |
| Clarín | clarin.com/espectaculos/teatro/ | Sí (del HTML) | `<time>` si existe |

**Problema conocido:** Perfil y Clarín tienen casi todo su archivo de danza en 2023-2024. Después del filtro de 2 meses quedan 0 noticias reales → caída al NOTICIAS_RESPALDO (3 items hardcoded).
**Pendiente:** agregar fuentes de noticias más activas (Danzahoy, Página 12, Balletín Dance noticias — actualmente devuelve 0).

### Scrapers de convocatorias (scrapers_convocatorias.py)
| Fuente | URL | Subtipo detectado |
|---|---|---|
| Alt Teatral Castings | alternativateatral.com/convocatorias.php?...clasificacion=14 | casting/audición |
| Alt Teatral Conv | alternativateatral.com/convocatorias.php?pais=1 | variado |
| Recursos Culturales | recursosculturales.com/tag/danza/ | beca/subsidio/residencia |
| Teatro Cervantes | teatrocervantes.gob.ar/convocatorias-artisticas/ | audición (bailarines) |
| Balletín Dance | balletindance.com/category/audiciones/ + /subsidios... | audición/beca |

**Nota Cervantes:** filtra solo convocatorias con keywords de danza. Excluye años anteriores a 2026.

---

## Arquitectura general

```
Startup → scrape() en paralelo → globals (eventos, noticias, convocatorias)
asyncio.create_task(scraper_loop()) → refresca cada 24hs en background sin downtime
Cliente → GET / → HTML (frontend.py) → JS fetch /api/* → renderiza tarjetas
```

### Datos de respaldo (hardcoded en main.py)
- `EVENTOS_RESPALDO` — **eliminado**
- `NOTICIAS_RESPALDO` — 3 items hardcoded. Se usa cuando scrapers de noticias devuelven lista vacía.
- Convocatorias: sin respaldo.

### Deduplicación
- Por `titulo[:80].lower()`
- Límites: eventos 50, noticias 25, convocatorias 50

### Filtro de antigüedad (noticias)
- `filtrar_recientes(lista, meses=2)` en utils.py
- Parsea fechas con `parsear_fecha_iso()`: soporta ISO 8601, DD/MM/YYYY, DD-MM-YYYY, "15 de enero de 2025"
- Items sin fecha parseable se conservan (se asume que son recientes)
- Aplicado en main.py solo a noticias: `deduplicar(filtrar_recientes(todas_noticias, meses=2))`
- Perfil: fecha en `<span class="date-time">` capturada explícitamente en el scraper
- `extraer_item()` también captura atributo `datetime` de `<time>` → guarda en campo `fecha_iso`

---

## Disciplinas / tipos
- **clásica** — ballet, ópera-ballet, pas de deux
- **folklórica** — malambo, zamba, chacarera
- **contemporánea** — experimental, escénica, coreografía (fallback)
- **tango** — tango, milonga, bandoneón, tango escenario (agregado 2026-03-01)

Detección en `detectar_tipo()` (utils.py): orden tango → clásica → folklórica → contemporánea.

---

## Frontend (frontend.py)

- Stack: HTML/CSS/JS inline como string Python
- Fuentes: Playfair Display (serif, títulos) + Plus Jakarta Sans (body)
- Colores: fondo `#050505`, cards `#111`, acento `#ff3c3c`
- Layout: sidebar 260px fijo + contenido en grid
- **3 pestañas separadas:** Eventos (default) | Convocatorias | Prensa
- Filtros disciplina en sidebar: Todo / Clásica / Folklórica / Contemporánea / **Tango**
- Tarjeta con imagen: `<img class="card-thumb">` + placeholder de fallback si falla
- Tarjeta sin imagen: placeholder con título en italic y gradiente oscuro

---

## SEO implementado

- Title: "Danza Argentina | Agenda de Ballet, Folklore y Danza Contemporánea en Buenos Aires"
- Meta description, keywords expandidos
- JSON-LD structured data: WebSite + Organization + WebPage schemas
- H1 oculto visualmente pero indexable
- Meta geo: `AR-C`, Buenos Aires
- Canonical URL
- Sitemap con `<lastmod>` dinámico (fecha del día)
- Preconnect a Google Fonts

---

## Deploy

- **Actual:** No deployado (Railway tiene costo mínimo $5/mes)
- **Evaluado:** Koyeb — gratis, sin sleep, sin tarjeta de crédito requerida
- **Pendiente:** hacer deploy en Koyeb

### Para correr localmente
```bash
cd /home/sor/Documentos/Proyectos-web/Danza-app
source venv/bin/activate
uvicorn main:app --reload > /tmp/danza-app.log 2>&1 &
xdg-open http://127.0.0.1:8000
```

---

## Fuentes investigadas para agregar (pendiente)

### Eventos / Noticias
| Fuente | URL | Prioridad | Nota |
|---|---|---|---|
| Danzahoy | danzahoy.com.ar | Alta | Revista especializada, WordPress fácil |
| CCK | cck.gob.ar | Alta | Muchos eventos de danza de alta producción |
| Cultura Nación | cultura.gob.ar/agenda | Alta | Agenda oficial nacional |
| FIBA | fiba.gob.ar | Alta | Festival internacional, edición 2026 |
| INT | inteatro.gob.ar | Media | Convocatorias y subsidios |
| Teatro Coliseo | teatrocoliseo.org.ar | Media | Danza clásica |
| Teatro Argentino LP | teatroargentino.gob.ar | Media | Ballet Estable de La Plata |
| Página 12 | pagina12.com.ar | Media | Noticias de danza, fácil de scrapear |
| Ticketek | ticketek.com.ar | Baja | JS-heavy, mucho trabajo |

### Convocatorias / Subsidios
| Programa | URL | Nota |
|---|---|---|
| ProDanza CABA | buenosaires.gob.ar/cultura/danza/prodanza | Convoca feb-abr |
| Fondo Nacional de las Artes | fnartes.gov.ar | Múltiples convocatorias al año |
| Iberescena | iberescena.org | Anual ene-mar, requiere 2 países |
| Mecenazgo CABA | mecenazgo.buenosaires.gob.ar | Continuo |

### Tango (para ampliar)
| Fuente | URL | Nota |
|---|---|---|
| TangoBA | tangoba.org | Oficial del Mundial. Poco scrapeable, más institucional |
| TangoCat | tangocat.net | 420+ eventos globales 2026, maestros argentinos en el mundo |
| TangoFestivals | tangofestivals.net | Directorio internacional con mapa |

### Clases privadas (posible nueva sección)
| Fuente | Nota |
|---|---|
| MercadoLibre Servicios | Tiene API pública oficial — más fácil de integrar |
| Superprof | 200-400 profesores en GBA, precios visibles |
| Profes.com.ar | Más pequeño, HTML estático |

---

## Problemas conocidos / pendiente técnico

- **Balletín Dance noticias devuelve 0 items** — scraper funciona para convocatorias pero falla en la home. Pendiente investigar selector.
- **Noticias casi vacías** — Perfil/Clarín tienen archivo de danza de 2023-2024. El filtro de 2 meses los descarta a casi todos. Necesitamos fuentes más activas (Danzahoy, Página 12).
- **Usina del Arte y CC Recoleta: 0 items** — posiblemente JS dinámico o cambio de estructura.
