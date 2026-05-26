HTML = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Danza Argentina | Agenda de Ballet, Folklore y Danza Contemporánea en Buenos Aires</title>
<meta name="description" content="La agenda más completa de danza en Argentina. Eventos de ballet clásico, danza folklórica y contemporánea en Buenos Aires. Convocatorias, audiciones, becas y noticias actualizadas a diario.">
<meta name="keywords" content="danza argentina, ballet buenos aires, danza contemporánea argentina, danza folklórica, malambo, agenda cultural buenos aires, convocatorias danza, audiciones ballet, becas danza, eventos de danza 2026, Teatro Colón ballet, danza moderna argentina, espectáculos de danza">
<meta name="author" content="Danza Argentina">
<meta name="robots" content="index, follow">
<meta name="geo.region" content="AR-C">
<meta name="geo.placename" content="Buenos Aires, Argentina">
<link rel="canonical" href="__BASE_URL__/">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>

<meta property="og:type" content="website">
<meta property="og:title" content="Danza Argentina | Agenda de Ballet, Folklore y Contemporánea">
<meta property="og:description" content="La agenda más completa de danza en Argentina. Eventos, convocatorias, audiciones y noticias actualizadas a diario.">
<meta property="og:url" content="__BASE_URL__/">
<meta property="og:locale" content="es_AR">
<meta property="og:site_name" content="Danza Argentina">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="Danza Argentina | Agenda de Ballet, Folklore y Contemporánea">
<meta name="twitter:description" content="La agenda más completa de danza en Argentina. Eventos, convocatorias y noticias actualizadas a diario.">
<meta name="twitter:image" content="__BASE_URL__/static/og-image.png">
<meta property="og:image" content="__BASE_URL__/static/og-image.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">

<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@graph": [
    {"@type":"WebSite","@id":"__BASE_URL__/#website","name":"Danza Argentina","url":"__BASE_URL__/","description":"La agenda más completa de danza en Argentina: ballet, folklore y contemporánea.","inLanguage":"es-AR","publisher":{"@id":"__BASE_URL__/#organization"}},
    {"@type":"Organization","@id":"__BASE_URL__/#organization","name":"Danza Argentina","url":"__BASE_URL__/","areaServed":{"@type":"City","name":"Buenos Aires"},"knowsAbout":["Ballet","Danza Contemporánea","Folklore Argentino","Tango"]},
    {"@type":"WebPage","@id":"__BASE_URL__/#webpage","url":"__BASE_URL__/","name":"Agenda de Danza en Argentina | Ballet, Folklore y Contemporánea","isPartOf":{"@id":"__BASE_URL__/#website"},"inLanguage":"es-AR"}
  ]
}
</script>

<link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@700;800;900&family=Playfair+Display:ital,wght@0,600;0,900;1,400&family=Plus+Jakarta+Sans:wght@300;400;500;600&display=swap" rel="stylesheet">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<style>
*, *::before, *::after { box-sizing: border-box; }

:root {
  --bg: #050505;
  --bg-elev: #0c0c0c;
  --line: #1a1a1a;
  --line-strong: #2a2a2a;
  --fg: #ffffff;
  --fg-mute: #888;
  --fg-faint: #555;
  --accent: #ff3c3c;
  --ff-serif: "Playfair Display", Georgia, serif;
  --ff-sans: "Plus Jakarta Sans", system-ui, sans-serif;
  --ff-display: "Barlow Condensed", "Plus Jakarta Sans", sans-serif;
  --meta: 10px;
  --tracking: 0.18em;
}

html, body { margin: 0; padding: 0; background: var(--bg); color: var(--fg); font-family: var(--ff-sans); font-size: 15px; line-height: 1.5; -webkit-font-smoothing: antialiased; }
a { color: inherit; text-decoration: none; }
button { font: inherit; color: inherit; background: none; border: 0; cursor: pointer; padding: 0; }

/* ── HEADER ── */
.site-header {
  position: sticky; top: 0; z-index: 100;
  display: flex; align-items: center; justify-content: space-between;
  padding: 16px 40px;
  background: rgba(5,5,5,0.9); backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--line);
}
.logo {
  font-family: var(--ff-display); font-weight: 900; font-size: 22px;
  letter-spacing: -0.02em; text-transform: uppercase;
  display: flex; align-items: center; gap: 8px;
}
.logo::before { content: ""; width: 8px; height: 8px; background: var(--accent); display: inline-block; }
.logo-sub { color: var(--fg-faint); font-weight: 700; font-size: 11px; letter-spacing: .2em; }

.nav { display: flex; gap: 28px; font-size: 11px; font-weight: 500; text-transform: uppercase; letter-spacing: 0.12em; }
.nav-btn { color: var(--fg-mute); transition: color .15s; padding-bottom: 2px; border: none; background: none; cursor: pointer; font: inherit; text-transform: uppercase; letter-spacing: 0.12em; font-size: 11px; }
.nav-btn:hover { color: var(--fg); }
.nav-btn.activo { color: var(--fg); border-bottom: 1px solid var(--accent); }

.header-count { font-size: var(--meta); text-transform: uppercase; letter-spacing: var(--tracking); color: var(--fg-faint); }

/* ── LAYOUT ── */
.layout { display: grid; grid-template-columns: 220px 1fr; }

/* ── SIDEBAR ── */
.sidebar {
  padding: 36px 24px 60px 32px;
  border-right: 1px solid var(--line);
  position: sticky; top: 57px;
  align-self: start;
  height: calc(100vh - 57px);
  overflow-y: auto;
}
.filter-group { margin-bottom: 32px; }
.filter-group h4 {
  font-size: var(--meta); text-transform: uppercase;
  letter-spacing: var(--tracking); color: var(--fg-faint);
  margin: 0 0 12px; font-weight: 600;
}
.filter-list { list-style: none; padding: 0; margin: 0; }
.filter-list li {
  font-size: 13px; padding: 7px 0 7px 12px;
  color: var(--fg-mute); cursor: pointer;
  border-left: 1px solid transparent;
  transition: color .12s, border-color .12s;
  display: flex; justify-content: space-between; align-items: center;
  user-select: none;
}
.filter-list li:hover { color: var(--fg); }
.filter-list li.activo { color: var(--fg); border-left-color: var(--fg); font-weight: 500; }
.filter-list li .cnt { font-size: 10px; color: var(--fg-faint); letter-spacing: 0.1em; }
.sidebar-divider { height: 1px; background: var(--line); margin: 24px 0; }

/* ── MAIN ── */
.main { padding: 36px 36px 80px; min-width: 0; }

.section-head {
  display: flex; align-items: baseline; justify-content: space-between;
  margin-bottom: 24px; padding-bottom: 14px;
  border-bottom: 1px solid var(--line);
}
.section-head h2 {
  font-family: var(--ff-serif); font-weight: 600; font-size: 20px;
  letter-spacing: -0.01em; margin: 0;
}
.section-count { font-size: var(--meta); text-transform: uppercase; letter-spacing: var(--tracking); color: var(--fg-faint); }

/* ── VISTAS ── */
.vista { display: none; }
.vista.activa { display: block; }

/* ── EVENT CARDS (póster) ── */
.cards-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  min-height: 300px;
}

.event-card {
  position: relative; display: block;
  aspect-ratio: 3/4; overflow: hidden;
  background: #000; cursor: pointer;
  text-decoration: none;
}
.event-card .media {
  position: absolute; inset: 0;
  background-size: cover; background-position: center;
  transition: transform .9s cubic-bezier(.2,.7,.2,1);
  will-change: transform;
}
.event-card:hover .media { transform: scale(1.05); }
.event-card .scrim {
  position: absolute; inset: 0;
  background: linear-gradient(to top, rgba(0,0,0,0.92) 0%, rgba(0,0,0,0.55) 35%, rgba(0,0,0,0) 65%);
  pointer-events: none;
}
.event-card .corner {
  position: absolute; top: 14px; left: 14px; right: 14px;
  display: flex; justify-content: space-between; align-items: flex-start;
  z-index: 2;
  font-size: var(--meta); text-transform: uppercase; letter-spacing: var(--tracking);
  color: rgba(255,255,255,0.8);
}
.event-card .corner .date {
  background: var(--fg); color: var(--bg);
  padding: 5px 11px; font-family: var(--ff-display);
  font-weight: 800; font-size: 14px; letter-spacing: 0.08em;
  line-height: 1;
}
.event-card .info {
  position: absolute; left: 0; right: 0; bottom: 0;
  padding: 18px 16px 16px; z-index: 2;
  max-height: 65%;
}
.event-card .title {
  font-family: var(--ff-display); font-weight: 800;
  font-size: 26px; line-height: 0.95;
  letter-spacing: -0.005em; text-transform: uppercase;
  color: var(--fg); margin: 0 0 9px;
}
.event-card .meta-card {
  font-size: var(--meta); text-transform: uppercase;
  letter-spacing: var(--tracking); color: #888;
  display: flex; align-items: center; gap: 6px; flex-wrap: wrap;
}
.event-card .meta-card .dot { width: 2px; height: 2px; background: #555; border-radius: 50%; }
.event-card .meta-card .src { color: var(--fg); font-weight: 500; }
.event-card:hover .title { color: var(--accent); }

/* sin imagen */
.event-card.no-image { border: 1px solid var(--line); }
.event-card.no-image .info { position: absolute; inset: 0; display: flex; flex-direction: column; justify-content: space-between; padding: 16px; }
.event-card.no-image .title { font-size: clamp(26px, 3.5vw, 46px); line-height: 0.9; margin: 0; }
.event-card.no-image .meta-card { color: var(--fg-faint); }
.event-card.no-image:hover { border-color: var(--accent); }

/* featured: doble ancho */
.event-card.featured { grid-column: span 2; aspect-ratio: 16/10; }
.event-card.featured .title { font-size: 48px; }
.event-card.featured .info { padding: 28px; max-width: 68%; }

/* ── ASIDE-GRID (conv + noticias debajo de eventos) ── */
.aside-grid {
  margin-top: 72px;
  display: grid; grid-template-columns: 1.4fr 1fr; gap: 56px;
}
.aside-head { display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 6px; }
.aside-head h3 { font-family: var(--ff-serif); font-style: italic; font-weight: 400; font-size: 28px; letter-spacing: -0.01em; margin: 0; }
.aside-head button { font-size: var(--meta); text-transform: uppercase; letter-spacing: var(--tracking); color: var(--fg-faint); border: none; background: none; cursor: pointer; }
.aside-head button:hover { color: var(--accent); }

/* list-items: convocatorias */
.list-item {
  display: grid; grid-template-columns: 56px 1fr auto;
  gap: 16px; padding: 18px 0;
  border-top: 1px solid var(--line);
  align-items: baseline; cursor: pointer;
}
.list-item:last-child { border-bottom: 1px solid var(--line); }
.list-item:hover .item-title { color: var(--accent); }
.item-num { font-family: var(--ff-display); font-size: 11px; font-weight: 700; color: var(--fg-faint); letter-spacing: 0.1em; }
.item-title { font-family: var(--ff-serif); font-size: 17px; font-weight: 500; line-height: 1.25; margin: 0 0 4px; transition: color .15s; letter-spacing: -0.005em; }
.item-meta { font-size: var(--meta); text-transform: uppercase; letter-spacing: var(--tracking); color: var(--fg-faint); }
.item-deadline { font-family: var(--ff-display); font-size: 10px; text-transform: uppercase; letter-spacing: 0.14em; color: var(--fg-mute); white-space: nowrap; font-weight: 600; }

/* news-items */
.news-item { display: block; padding: 16px 0; border-top: 1px solid var(--line); cursor: pointer; }
.news-item:last-child { border-bottom: 1px solid var(--line); }
.news-kicker { font-size: var(--meta); text-transform: uppercase; letter-spacing: var(--tracking); color: var(--accent); margin-bottom: 5px; font-weight: 600; }
.news-item h4 { font-family: var(--ff-serif); font-size: 16px; font-weight: 500; line-height: 1.25; margin: 0 0 4px; letter-spacing: -0.005em; transition: color .15s; }
.news-item:hover h4 { color: var(--accent); }
.news-meta { font-size: var(--meta); text-transform: uppercase; letter-spacing: var(--tracking); color: var(--fg-faint); }

/* ── CONVOCATORIAS (vista completa) ── */
.subtipo-filters {
  display: flex; gap: 8px; flex-wrap: wrap;
  margin-bottom: 24px;
}
.subtipo-btn {
  border: 1px solid var(--line-strong); color: var(--fg-faint);
  padding: 5px 12px; font-size: var(--meta);
  text-transform: uppercase; letter-spacing: var(--tracking);
  cursor: pointer; transition: 0.2s; font-family: var(--ff-sans);
}
.subtipo-btn.activo, .subtipo-btn:hover { border-color: var(--fg); color: var(--fg); }

.conv-full-list { margin-top: 0; }

/* ── NOTICIAS (vista completa) — grid de cards noticias ── */
.news-grid { display: grid; grid-template-columns: repeat(3,1fr); gap: 20px; }
.news-card {
  border: 1px solid var(--line); padding: 20px;
  transition: border-color .2s; cursor: pointer;
}
.news-card:hover { border-color: var(--fg-mute); }
.news-card .news-kicker { font-size: var(--meta); text-transform: uppercase; letter-spacing: var(--tracking); color: var(--accent); margin-bottom: 8px; font-weight: 600; }
.news-card h3 { font-family: var(--ff-serif); font-size: 18px; font-weight: 500; line-height: 1.3; margin: 0 0 8px; letter-spacing: -0.005em; }
.news-card:hover h3 { color: var(--accent); }
.news-card p { font-size: 13px; color: var(--fg-mute); line-height: 1.5; margin: 0 0 12px; }
.news-card .news-meta { font-size: var(--meta); text-transform: uppercase; letter-spacing: var(--tracking); color: var(--fg-faint); }

/* ── FOOTER ── */
.site-footer {
  margin-top: 80px; padding: 32px 40px 48px;
  border-top: 1px solid var(--line);
  display: flex; justify-content: space-between; align-items: center;
  font-size: var(--meta); text-transform: uppercase; letter-spacing: var(--tracking); color: var(--fg-faint);
}
.foot-logo { font-family: var(--ff-display); font-size: 15px; font-weight: 900; color: var(--fg); letter-spacing: -0.01em; }

/* ── RESPONSIVE ── */
@media (max-width: 1100px) {
  .cards-grid { grid-template-columns: repeat(2, 1fr); }
  .event-card.featured { grid-column: span 2; }
  .aside-grid { grid-template-columns: 1fr; gap: 48px; }
  .news-grid { grid-template-columns: repeat(2,1fr); }
}
@media (max-width: 760px) {
  .layout { grid-template-columns: 1fr; }
  .sidebar { position: static; height: auto; border-right: 0; border-bottom: 1px solid var(--line); padding: 20px 24px; }
  .cards-grid { grid-template-columns: 1fr; }
  .event-card.featured { grid-column: span 1; aspect-ratio: 3/4; }
  .event-card.featured .title { font-size: 32px; }
  .event-card.featured .info { max-width: 100%; padding: 18px; }
  .site-header { padding: 14px 20px; }
  .nav { gap: 16px; }
  .main { padding: 24px 20px 60px; }
  .news-grid { grid-template-columns: 1fr; }
  .list-item { grid-template-columns: 40px 1fr auto; gap: 10px; }
}
</style>
</head>
<body>
<h1 style="position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap">Agenda de Danza en Argentina — Ballet, Folklore y Contemporánea en Buenos Aires</h1>

<header class="site-header">
  <div class="logo">DANZA<span class="logo-sub">.AR</span></div>
  <nav class="nav">
    <button class="nav-btn activo" onclick="cambiarVista('eventos',this)">Agenda</button>
    <button class="nav-btn" onclick="cambiarVista('tango',this)">Tango</button>
    <button class="nav-btn" onclick="cambiarVista('convocatorias',this)">Convocatorias</button>
    <button class="nav-btn" onclick="cambiarVista('prensa',this)">Prensa</button>
  </nav>
  <div class="header-count" id="header-count"></div>
</header>

<div class="layout">

  <aside class="sidebar">
    <div class="filter-group">
      <h4>Disciplina</h4>
      <ul class="filter-list" id="filtros-tipo">
        <li class="activo" onclick="filtrarTipo('',this)">Todas <span class="cnt" id="cnt-todas"></span></li>
        <li onclick="filtrarTipo('contemporánea',this)">Contemporánea <span class="cnt" id="cnt-contemp"></span></li>
        <li onclick="filtrarTipo('clásica',this)">Clásica <span class="cnt" id="cnt-clasica"></span></li>
        <li onclick="filtrarTipo('folklórica',this)">Folklórica <span class="cnt" id="cnt-folk"></span></li>
      </ul>
    </div>
    <div class="sidebar-divider"></div>
    <div class="filter-group" id="sidebar-subtipo" style="display:none">
      <h4>Tipo</h4>
      <ul class="filter-list" id="filtros-subtipo">
        <li class="activo" onclick="aplicarSubtipo('',this)">Todas</li>
        <li onclick="aplicarSubtipo('casting',this)">Castings</li>
        <li onclick="aplicarSubtipo('audición',this)">Audiciones</li>
        <li onclick="aplicarSubtipo('beca',this)">Becas</li>
        <li onclick="aplicarSubtipo('subsidio',this)">Subsidios</li>
        <li onclick="aplicarSubtipo('residencia',this)">Residencias</li>
        <li onclick="aplicarSubtipo('concurso',this)">Concursos</li>
      </ul>
    </div>
  </aside>

  <main class="main">

    <!-- ── AGENDA (eventos + conv+noticias abajo) ── -->
    <div id="vista-eventos" class="vista activa">
      <div class="section-head">
        <h2>En cartel</h2>
        <span class="section-count" id="count-ev">0 eventos</span>
      </div>
      <div id="lista-eventos" class="cards-grid"></div>

      <div class="aside-grid">
        <section>
          <div class="aside-head">
            <h3>Convocatorias</h3>
            <button onclick="cambiarVista('convocatorias', document.querySelectorAll('.nav-btn')[2])">Ver todas →</button>
          </div>
          <div id="conv-mini"></div>
        </section>
        <section>
          <div class="aside-head">
            <h3>Noticias</h3>
            <button onclick="cambiarVista('prensa', document.querySelectorAll('.nav-btn')[3])">Más →</button>
          </div>
          <div id="news-mini"></div>
        </section>
      </div>
    </div>

    <!-- ── TANGO ── -->
    <div id="vista-tango" class="vista">
      <div class="section-head">
        <h2>Milongas y Tango</h2>
        <span class="section-count" id="count-tango">0 eventos</span>
      </div>
      <div id="lista-tango" class="cards-grid"></div>
    </div>

    <!-- ── CONVOCATORIAS ── -->
    <div id="vista-convocatorias" class="vista">
      <div class="section-head">
        <h2>Audiciones, Becas y Castings</h2>
        <span class="section-count" id="count-conv">0</span>
      </div>
      <div class="subtipo-filters">
        <button class="subtipo-btn activo" onclick="aplicarSubtipo('',this)">Todas</button>
        <button class="subtipo-btn" onclick="aplicarSubtipo('casting',this)">Castings</button>
        <button class="subtipo-btn" onclick="aplicarSubtipo('audición',this)">Audiciones</button>
        <button class="subtipo-btn" onclick="aplicarSubtipo('beca',this)">Becas</button>
        <button class="subtipo-btn" onclick="aplicarSubtipo('subsidio',this)">Subsidios</button>
        <button class="subtipo-btn" onclick="aplicarSubtipo('residencia',this)">Residencias</button>
        <button class="subtipo-btn" onclick="aplicarSubtipo('concurso',this)">Concursos</button>
      </div>
      <div class="conv-full-list" id="lista-convocatorias"></div>
    </div>

    <!-- ── PRENSA ── -->
    <div id="vista-prensa" class="vista">
      <div class="section-head">
        <h2>Noticias de Danza</h2>
        <span class="section-count" id="count-no">0</span>
      </div>
      <div id="lista-noticias" class="news-grid"></div>
    </div>

  </main>
</div>

<footer class="site-footer">
  <div class="foot-logo">DANZA.AR</div>
  <div>Agenda independiente · Buenos Aires, ARG</div>
  <div>Actualizado a diario</div>
</footer>

<script>
let dataStore = { eventos: [], noticias: [], convocatorias: [] };
let subtipoActivo = '';
let tipoActivo = '';
let vistaActiva = 'eventos';

const MESES = ['enero','febrero','marzo','abril','mayo','junio','julio','agosto','septiembre','octubre','noviembre','diciembre'];
const MESES_ES = {enero:0,febrero:1,marzo:2,abril:3,mayo:4,junio:5,julio:6,agosto:7,septiembre:8,octubre:9,noviembre:10,diciembre:11};
const CIUDADES = {'Ente Cultural Tucumán':'Tucumán','FAD UNCuyo':'Mendoza'};

function mesDesde(fecha) {
    if (!fecha) return '';
    let m = fecha.match(/\\b(\\d{4})-(\\d{2})-\\d{2}\\b/);
    if (m) return MESES[parseInt(m[2])-1] || '';
    m = fecha.match(/\\b(\\d{1,2})[\\/-](\\d{1,2})[\\/-](\\d{4})\\b/);
    if (m) return MESES[parseInt(m[2])-1] || '';
    const lower = fecha.toLowerCase();
    for (const [n,i] of Object.entries(MESES_ES)) { if (lower.includes(n)) return MESES[i]; }
    return '';
}

function crearEventCard(item, featured) {
    const mes = mesDesde(item.fecha);
    const ciudad = (item.ciudad || CIUDADES[item.fuente] || 'CABA').toUpperCase();
    const tag = (item.tipo || '').toUpperCase();
    const dateLabel = mes ? mes.toUpperCase() : '';
    const metaRight = [mes ? mes.toUpperCase() : '', ciudad].filter(Boolean).join(' · ');
    const dateBadge = dateLabel ? `<div class="date">${dateLabel}</div>` : '<div></div>';
    const dateBadgeDark = dateLabel ? `<div class="date" style="background:var(--fg);color:var(--bg)">${dateLabel}</div>` : '<div></div>';

    if (item.imagen) {
        const cls = featured ? 'event-card featured' : 'event-card';
        return `<a class="${cls}" href="${item.url}" target="_blank" rel="noopener">
            <div class="media" style="background-image:url('${item.imagen}')"></div>
            <div class="scrim"></div>
            <div class="corner">
                ${dateBadge}
                <div>${tag}</div>
            </div>
            <div class="info">
                <h3 class="title">${item.titulo}</h3>
                <div class="meta-card">
                    <span class="src">${item.fuente}</span>
                    <span class="dot"></span>
                    <span>${metaRight}</span>
                </div>
            </div>
        </a>`;
    } else {
        return `<a class="event-card no-image" href="${item.url}" target="_blank" rel="noopener">
            <div class="corner">
                ${dateBadgeDark}
                <div>${tag}</div>
            </div>
            <div class="info">
                <h3 class="title">${item.titulo}</h3>
                <div class="meta-card">
                    <span class="src">${item.fuente}</span>
                    <span class="dot"></span>
                    <span>${metaRight}</span>
                </div>
            </div>
        </a>`;
    }
}

function renderGrid(items, containerId) {
    let usedFeatured = false;
    const html = items.map(item => {
        const feat = !usedFeatured && !!item.imagen;
        if (feat) usedFeatured = true;
        return crearEventCard(item, feat);
    }).join('');
    document.getElementById(containerId).innerHTML = html || '<p style="color:#555;padding:2rem 0">Sin resultados.</p>';
}

function crearListItem(item, num) {
    const subtipo = item.subtipo || 'convocatoria';
    return `<div class="list-item" onclick="window.open('${item.url}','_blank')">
        <div class="item-num">${String(num).padStart(2,'0')}</div>
        <div>
            <h4 class="item-title">${item.titulo}</h4>
            <div class="item-meta">${subtipo} · ${item.fuente}</div>
        </div>
        <div class="item-deadline">${item.fecha || ''}</div>
    </div>`;
}

function crearNewsItem(item) {
    return `<article class="news-item" onclick="window.open('${item.url}','_blank')">
        <div class="news-kicker">${item.tipo || item.fuente}</div>
        <h4>${item.titulo}</h4>
        <div class="news-meta">${item.fuente}</div>
    </article>`;
}

function crearNewsCard(item) {
    return `<article class="news-card" onclick="window.open('${item.url}','_blank')">
        <div class="news-kicker">${item.tipo || item.fuente}</div>
        <h3>${item.titulo}</h3>
        <p>${item.descripcion || ''}</p>
        <div class="news-meta">${item.fuente}</div>
    </article>`;
}

function render() {
    const noTango = arr => arr.filter(i => i.tipo !== 'tango');
    const soloTango = arr => arr.filter(i => i.tipo === 'tango');
    const porTipo = arr => tipoActivo ? arr.filter(i => i.tipo === tipoActivo) : arr;
    const porSubtipo = arr => subtipoActivo ? arr.filter(i => i.subtipo === subtipoActivo) : arr;

    const evBase = noTango(dataStore.eventos);
    const evFiltrados = porTipo(evBase);
    const tangoItems = soloTango(dataStore.eventos);
    const convFiltradas = porSubtipo(dataStore.convocatorias);

    renderGrid(evFiltrados, 'lista-eventos');
    renderGrid(tangoItems, 'lista-tango');

    // counts sidebar
    document.getElementById('cnt-todas').textContent = evBase.length;
    document.getElementById('cnt-contemp').textContent = evBase.filter(i=>i.tipo==='contemporánea').length;
    document.getElementById('cnt-clasica').textContent = evBase.filter(i=>i.tipo==='clásica').length;
    document.getElementById('cnt-folk').textContent = evBase.filter(i=>i.tipo==='folklórica').length;

    document.getElementById('count-ev').textContent = evFiltrados.length + ' eventos';
    document.getElementById('count-tango').textContent = tangoItems.length + ' eventos';
    document.getElementById('count-conv').textContent = convFiltradas.length;
    document.getElementById('count-no').textContent = dataStore.noticias.length;

    document.getElementById('header-count').textContent =
        (evFiltrados.length + tangoItems.length) + ' funciones · ARG';

    // aside-grid previews (6 cada uno)
    document.getElementById('conv-mini').innerHTML =
        dataStore.convocatorias.slice(0,6).map((c,i) => crearListItem(c, i+1)).join('');
    document.getElementById('news-mini').innerHTML =
        dataStore.noticias.slice(0,6).map(crearNewsItem).join('');

    // listas completas
    document.getElementById('lista-convocatorias').innerHTML =
        convFiltradas.map((c,i) => crearListItem(c, i+1)).join('');
    document.getElementById('lista-noticias').innerHTML =
        dataStore.noticias.map(crearNewsCard).join('');
}

function cambiarVista(nombre, btn) {
    vistaActiva = nombre;
    document.querySelectorAll('.vista').forEach(v => v.classList.remove('activa'));
    document.getElementById('vista-' + nombre).classList.add('activa');
    document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('activo'));
    btn.classList.add('activo');
    // sidebar: mostrar subtipo solo en convocatorias
    document.getElementById('sidebar-subtipo').style.display = nombre === 'convocatorias' ? 'block' : 'none';
    // discipline filter: solo en eventos
    document.getElementById('filtros-tipo').parentElement.style.display =
        (nombre === 'eventos' || nombre === 'tango') ? 'block' : 'none';
}

function filtrarTipo(tipo, el) {
    tipoActivo = tipo;
    document.querySelectorAll('#filtros-tipo li').forEach(li => li.classList.remove('activo'));
    el.classList.add('activo');
    render();
}

function aplicarSubtipo(subtipo, btn) {
    subtipoActivo = subtipo;
    document.querySelectorAll('.subtipo-btn').forEach(b => b.classList.remove('activo'));
    btn.classList.add('activo');
    render();
}

async function cargar() {
    try {
        const [ev, no, conv] = await Promise.all([
            fetch('/api/eventos').then(r => r.json()),
            fetch('/api/noticias').then(r => r.json()),
            fetch('/api/convocatorias').then(r => r.json())
        ]);
        dataStore = { eventos: ev, noticias: no, convocatorias: conv };
        render();
    } catch(e) { console.error('Error carga', e); }
}

cargar();
</script>
</body>
</html>
"""
