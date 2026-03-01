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
<meta name="twitter:image:alt" content="Danza Argentina — Agenda de Ballet, Folklore y Contemporánea en Buenos Aires">

<meta property="og:image" content="__BASE_URL__/static/og-image.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Danza Argentina — Agenda de Ballet, Folklore y Contemporánea en Buenos Aires">

<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "WebSite",
      "@id": "__BASE_URL__/#website",
      "name": "Danza Argentina",
      "url": "__BASE_URL__/",
      "description": "La agenda más completa de danza en Argentina: ballet, folklore y contemporánea.",
      "inLanguage": "es-AR",
      "publisher": { "@id": "__BASE_URL__/#organization" }
    },
    {
      "@type": "Organization",
      "@id": "__BASE_URL__/#organization",
      "name": "Danza Argentina",
      "url": "__BASE_URL__/",
      "description": "Agregador de eventos, noticias y convocatorias de danza clásica, folklórica y contemporánea en Argentina.",
      "areaServed": {"@type": "City", "name": "Buenos Aires", "sameAs": "https://www.wikidata.org/wiki/Q1486"},
      "knowsAbout": ["Ballet", "Danza Contemporánea", "Folklore Argentino", "Tango"],
      "inLanguage": "es-AR"
    },
    {
      "@type": "WebPage",
      "@id": "__BASE_URL__/#webpage",
      "url": "__BASE_URL__/",
      "name": "Agenda de Danza en Argentina | Ballet, Folklore y Contemporánea",
      "isPartOf": { "@id": "__BASE_URL__/#website" },
      "about": {
        "@type": "Thing",
        "name": "Danza en Argentina",
        "description": "Eventos, espectáculos, convocatorias y noticias de danza clásica, folklórica y contemporánea en Argentina."
      },
      "inLanguage": "es-AR"
    }
  ]
}
</script>

<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;700&family=Playfair+Display:ital,wght@0,900;1,900&display=swap" rel="stylesheet">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<style>
:root {
    --bg: #050505; --card: #111111; --accent: #ff3c3c;
    --border: rgba(255,255,255,0.1); --text: #ffffff; --text-dim: #888;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
    background-color: var(--bg); color: var(--text);
    font-family: 'Plus Jakarta Sans', sans-serif; overflow-x: hidden;
}

.app-container { display: grid; grid-template-columns: 260px 1fr; min-height: 100vh; }

aside {
    padding: 3rem 1.5rem; border-right: 1px solid var(--border);
    position: sticky; top: 0; height: 100vh; overflow-y: auto;
    display: flex; flex-direction: column;
}

.logo {
    font-family: 'Playfair Display', serif; font-size: 2rem;
    line-height: 0.9; margin-bottom: 3rem; font-style: italic; color: var(--accent);
}

.nav-section-title {
    font-size: 0.6rem; text-transform: uppercase; letter-spacing: 2px;
    color: #444; margin: 1.5rem 0 0.5rem 0; padding-left: 1rem;
}

.nav-group { display: flex; flex-direction: column; gap: 0.3rem; }
.filtro {
    background: none; border: none; color: var(--text-dim);
    text-align: left; padding: 0.8rem 1rem; font-size: 0.8rem;
    cursor: pointer; transition: 0.2s; border-radius: 4px;
    text-transform: uppercase; letter-spacing: 1px;
}
.filtro.activo { background: rgba(255,255,255,0.05); color: var(--text); border-left: 2px solid var(--accent); }
.filtro:hover { color: var(--text); background: rgba(255,255,255,0.03); }

/* Vistas */
.vista { display: none; }
.vista.activa { display: block; }

.vista-single { padding: 3rem 2rem; }
.cards-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 1rem;
    min-height: 400px;
}

.col-header {
    margin-bottom: 3rem; display: flex; justify-content: space-between; align-items: baseline;
    border-bottom: 1px solid var(--accent); padding-bottom: 1rem;
}
.col-header h2 { font-family: 'Playfair Display', serif; font-size: 1.8rem; font-weight: 900; }
.count-badge { font-size: 0.8rem; color: var(--accent); font-weight: 700; }

/* Tarjetas estándar */
.card {
    background: #0d0d0d; border: 1px solid var(--border);
    border-radius: 8px; overflow: hidden;
    margin-bottom: 1rem; transition: border-color .2s, transform .2s;
}
.card:hover { border-color: rgba(255,60,60,.3); transform: translateY(-2px); }
.card-thumb { width: 100%; height: 160px; object-fit: cover; display: block; }
.card-placeholder {
    width: 100%; height: 160px;
    background: linear-gradient(160deg, #0c0c0c 0%, #150404 100%);
    border-left: 3px solid rgba(255,60,60,.35);
    display: flex; flex-direction: column; justify-content: flex-end;
    padding: 1rem; position: relative; overflow: hidden;
}
.card-placeholder::before {
    content: ''; position: absolute; bottom: -25px; right: -25px;
    width: 110px; height: 110px; border-radius: 50%;
    border: 1px solid rgba(255,60,60,.07);
}
.ph-titulo {
    font-family: 'Playfair Display', serif; font-style: italic;
    color: rgba(255,255,255,.17); font-size: 1rem; line-height: 1.3; margin: 0;
    overflow: hidden; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical;
}
.card-body { padding: 1.1rem; }
.card h3 { font-size: 1.1rem; margin-bottom: 0.5rem; line-height: 1.3; font-weight: 600; }
.card h3 a { color: var(--text); text-decoration: none; }
.card h3 a:hover { color: var(--accent); }
.card p { color: var(--text-dim); font-size: 0.82rem; line-height: 1.5; margin-bottom: 0.8rem; }
.meta { display: flex; justify-content: space-between; font-size: 0.7rem; color: #555; font-weight: 700; }

/* Convocatorias */
.conv-header {
    padding: 3rem 2rem 1.5rem;
    border-bottom: 1px solid var(--border);
    display: flex; justify-content: space-between; align-items: baseline;
}
.conv-header h2 { font-family: 'Playfair Display', serif; font-size: 1.8rem; font-weight: 900; }

.subtipo-filters {
    display: flex; gap: 0.5rem; flex-wrap: wrap;
    padding: 1.5rem 2rem;
    border-bottom: 1px solid var(--border);
}
.subtipo-btn {
    background: none; border: 1px solid #333; color: #666;
    padding: 5px 12px; font-size: 0.65rem; text-transform: uppercase;
    letter-spacing: 1px; cursor: pointer; border-radius: 3px; transition: 0.2s;
}
.subtipo-btn.activo, .subtipo-btn:hover { border-color: var(--accent); color: var(--text); }

.conv-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 1.5rem;
    padding: 2rem;
    min-height: 400px;
}

.conv-card {
    background: #111; border: 1px solid var(--border);
    border-radius: 6px; padding: 1.5rem;
    transition: 0.3s; display: flex; flex-direction: column; gap: 0.8rem;
}
.conv-card:hover { border-color: var(--accent); background: #161616; }

.conv-subtipo {
    font-size: 0.6rem; font-weight: 700; text-transform: uppercase;
    letter-spacing: 1px; padding: 3px 8px; border-radius: 3px;
    display: inline-block; width: fit-content;
}
.conv-subtipo.casting     { background: rgba(255,60,60,0.15);   color: #ff3c3c; }
.conv-subtipo.audición    { background: rgba(255,150,0,0.15);   color: #ff9600; }
.conv-subtipo.beca        { background: rgba(0,200,100,0.15);   color: #00c864; }
.conv-subtipo.subsidio    { background: rgba(0,150,255,0.15);   color: #0096ff; }
.conv-subtipo.residencia  { background: rgba(180,0,255,0.15);   color: #b400ff; }
.conv-subtipo.concurso    { background: rgba(255,220,0,0.15);   color: #ffdc00; }
.conv-subtipo.convocatoria{ background: rgba(255,255,255,0.08); color: #aaa; }

.conv-card h3 { font-size: 1rem; line-height: 1.4; font-weight: 600; }
.conv-card h3 a { color: var(--text); text-decoration: none; }
.conv-card h3 a:hover { color: var(--accent); }
.conv-card p { color: var(--text-dim); font-size: 0.8rem; line-height: 1.5; flex: 1; }
.conv-meta { display: flex; justify-content: space-between; font-size: 0.65rem; color: #555; font-weight: 700; margin-top: auto; }

@media (max-width: 800px) {
    .app-container { grid-template-columns: 1fr; }
    aside { position: relative; height: auto; }
    .conv-grid { grid-template-columns: 1fr; }
    .cards-grid { grid-template-columns: 1fr; }
}
</style>
</head>
<body>
<div class="app-container">
    <aside>
        <div class="logo">DANZA<br>ARGENTINA</div>

        <div class="nav-section-title">Sección</div>
        <nav class="nav-group">
            <button class="filtro activo" onclick="cambiarVista('eventos', this)">Eventos</button>
            <button class="filtro" onclick="cambiarVista('tango', this)">Tango y Milongas</button>
            <button class="filtro" onclick="cambiarVista('convocatorias', this)">Convocatorias</button>
            <button class="filtro" onclick="cambiarVista('prensa', this)">Prensa</button>
        </nav>

    </aside>

    <main>
        <h1 style="position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap">Agenda de Danza en Argentina — Ballet, Folklore y Contemporánea en Buenos Aires</h1>

        <!-- Vista: Eventos -->
        <div id="vista-eventos" class="vista activa">
            <div class="vista-single">
                <div class="col-header">
                    <h2>Agenda de Danza en Buenos Aires</h2>
                    <span id="count-ev" class="count-badge">0</span>
                </div>
                <div id="lista-eventos" class="cards-grid"></div>
            </div>
        </div>

        <!-- Vista: Tango y Milongas -->
        <div id="vista-tango" class="vista">
            <div class="vista-single">
                <div class="col-header">
                    <h2>Milongas y Eventos de Tango en Buenos Aires</h2>
                    <span id="count-tango" class="count-badge">0</span>
                </div>
                <div id="lista-tango" class="cards-grid"></div>
            </div>
        </div>

        <!-- Vista: Convocatorias -->
        <div id="vista-convocatorias" class="vista">
            <div>
                <div class="conv-header">
                    <h2>Audiciones, Becas y Castings de Danza Argentina</h2>
                    <span id="count-conv" class="count-badge">0</span>
                </div>
                <div class="subtipo-filters">
                    <button class="subtipo-btn activo" onclick="aplicarSubtipo('', this)">Todas</button>
                    <button class="subtipo-btn" onclick="aplicarSubtipo('casting', this)">Castings</button>
                    <button class="subtipo-btn" onclick="aplicarSubtipo('audición', this)">Audiciones</button>
                    <button class="subtipo-btn" onclick="aplicarSubtipo('beca', this)">Becas</button>
                    <button class="subtipo-btn" onclick="aplicarSubtipo('subsidio', this)">Subsidios</button>
                    <button class="subtipo-btn" onclick="aplicarSubtipo('residencia', this)">Residencias</button>
                    <button class="subtipo-btn" onclick="aplicarSubtipo('concurso', this)">Concursos</button>
                </div>
                <div id="lista-convocatorias" class="conv-grid"></div>
            </div>
        </div>

        <!-- Vista: Prensa -->
        <div id="vista-prensa" class="vista">
            <div class="vista-single">
                <div class="col-header">
                    <h2>Noticias de Danza en Argentina</h2>
                    <span id="count-no" class="count-badge">0</span>
                </div>
                <div id="lista-noticias" class="cards-grid"></div>
            </div>
        </div>
    </main>
</div>

<script>
let dataStore = { eventos: [], noticias: [], convocatorias: [] };
let subtipoActivo = '';
let vistaActiva   = 'eventos';

async function cargar() {
    try {
        const [ev, no, conv] = await Promise.all([
            fetch('/api/eventos').then(r => r.json()),
            fetch('/api/noticias').then(r => r.json()),
            fetch('/api/convocatorias').then(r => r.json())
        ]);
        dataStore.eventos = ev;
        dataStore.noticias = no;
        dataStore.convocatorias = conv;
        render();
    } catch(e) {
        console.error("Error en carga", e);
    }
}

function crearTarjeta(item) {
    const ph = `<div class="card-placeholder"><p class="ph-titulo">${item.titulo}</p></div>`;
    const media = item.imagen
        ? `<img class="card-thumb" src="${item.imagen}" alt="${item.titulo}" loading="lazy" decoding="async" onerror="this.style.display='none';this.nextElementSibling.style.display='flex'">${ph.replace('class="card-placeholder"', 'class="card-placeholder" style="display:none"')}`
        : ph;
    return `
        <article class="card">
            ${media}
            <div class="card-body">
                <h3><a href="${item.url}" target="_blank">${item.titulo}</a></h3>
                <p>${item.descripcion || ''}</p>
                <div class="meta">
                    <span>${item.fuente.toUpperCase()}</span>
                    <span>${item.fecha || ''}</span>
                </div>
            </div>
        </article>`;
}

function crearTarjetaConv(item) {
    const subtipo = item.subtipo || 'convocatoria';
    return `
        <article class="conv-card">
            <span class="conv-subtipo ${subtipo}">${subtipo}</span>
            <h3><a href="${item.url}" target="_blank">${item.titulo}</a></h3>
            <p>${item.descripcion || ''}</p>
            <div class="conv-meta">
                <span>${item.fuente.toUpperCase()}</span>
                <span>${item.fecha || ''}</span>
            </div>
        </article>`;
}

function render() {
    const porSubtipo = arr => subtipoActivo ? arr.filter(i => i.subtipo === subtipoActivo) : arr;
    const noTango    = arr => arr.filter(i => i.tipo !== 'tango');
    const soloTango  = arr => arr.filter(i => i.tipo === 'tango');

    const evFiltrados   = noTango(dataStore.eventos);
    const tangoItems    = soloTango(dataStore.eventos);
    const noFiltradas   = dataStore.noticias;
    const convFiltradas = porSubtipo(dataStore.convocatorias);

    document.getElementById('lista-eventos').innerHTML       = evFiltrados.map(crearTarjeta).join('');
    document.getElementById('lista-tango').innerHTML         = tangoItems.map(crearTarjeta).join('');
    document.getElementById('lista-noticias').innerHTML      = noFiltradas.map(crearTarjeta).join('');
    document.getElementById('lista-convocatorias').innerHTML = convFiltradas.map(crearTarjetaConv).join('');

    document.getElementById('count-ev').textContent    = evFiltrados.length;
    document.getElementById('count-tango').textContent = tangoItems.length;
    document.getElementById('count-no').textContent    = noFiltradas.length;
    document.getElementById('count-conv').textContent  = convFiltradas.length;
}

function cambiarVista(nombre, btn) {
    vistaActiva = nombre;
    document.querySelectorAll('.vista').forEach(v => v.classList.remove('activa'));
    document.getElementById('vista-' + nombre).classList.add('activa');
    document.querySelectorAll('aside .filtro').forEach(b => b.classList.remove('activo'));
    btn.classList.add('activo');
}

function aplicarSubtipo(subtipo, btn) {
    subtipoActivo = subtipo;
    document.querySelectorAll('.subtipo-btn').forEach(b => b.classList.remove('activo'));
    btn.classList.add('activo');
    render();
}

async function refrescar() {
    await fetch('/api/refrescar');
    await cargar();
}

cargar();
</script>
</body>
</html>
"""
