"""components/styles.py — hoja de estilos unica de la app (CSS inyectado con st.markdown)."""

import nfl_graficos as G

BG, CARD, FG, MUTED, ACCENT, ACCENT2 = G.BG, G.CARD, G.FG, G.MUTED, G.ACCENT, G.ACCENT2


def css_block():
    return f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Oswald:wght@500;600;700&family=Inter:wght@400;500;600;700&display=swap');

/* --- Sistema de diseno: variables de color y curvas de animacion --- */
:root {{
    --bg-main:#0E1117; --bg-card:#1B1E2B; --bg-card-alt:#181B26; --border-subtle:#2A2D3E;
    --accent-red:{ACCENT}; --accent-blue:{ACCENT2};
    --text-primary:#FFFFFF; --text-secondary:#9CA3AF; --text-amber:#F59E0B;
    --ease-out:cubic-bezier(0.23,1,0.32,1);
}}
html, body, [class*="css"] {{ font-family:'Inter', sans-serif; }}
.stApp {{ background: radial-gradient(1200px 560px at 12% -12%, #35203a 0%, var(--bg-main) 45%),
                       radial-gradient(1000px 480px at 100% 0%, #163756 0%, var(--bg-main) 55%); color:#E9EDF5; }}

/* --- Ocultar chrome por defecto de Streamlit --- */
#MainMenu, footer, header[data-testid="stHeader"], [data-testid="stToolbar"],
[data-testid="stDecoration"], [data-testid="stStatusWidget"], .stAppDeployButton,
[data-testid="stAppDeployButton"] {{
    display:none !important; visibility:hidden !important; height:0 !important;
}}
.block-container {{ padding-top:1.1rem !important; padding-bottom:0; padding-left:2.2rem; padding-right:2.2rem; max-width:1680px; }}
h1,h2,h3 {{ font-family:'Oswald', sans-serif; letter-spacing:.5px; color:#fff; }}

@keyframes fadeUp {{ from {{ opacity:0; transform:translateY(14px); }} to {{ opacity:1; transform:translateY(0); }} }}
.fade-up {{ animation:fadeUp .5s ease both; }}
.d0{{animation-delay:.02s}} .d1{{animation-delay:.06s}} .d2{{animation-delay:.10s}} .d3{{animation-delay:.14s}}
.d4{{animation-delay:.18s}} .d5{{animation-delay:.22s}} .d6{{animation-delay:.26s}} .d7{{animation-delay:.30s}}
.d8{{animation-delay:.34s}} .d9{{animation-delay:.38s}}

/* --- Navbar --- */
.navbar {{ display:flex; align-items:center; gap:14px; padding:.3rem 0 .6rem; }}
.nav-brand {{ font-family:'Oswald'; font-weight:700; font-size:1.05rem; letter-spacing:.3px; color:#fff; display:flex; align-items:center; gap:.4rem; white-space:nowrap; overflow:hidden; }}
.nav-brand img {{ height:52px; width:52px; min-width:52px; border-radius:50%; object-fit:cover; box-shadow:0 0 0 2px rgba(255,255,255,.18); }}
.nav-brand .nfl {{ background:linear-gradient(135deg,{ACCENT},{ACCENT2}); color:#fff; padding:.02rem .35rem; border-radius:6px; font-size:.82rem; }}
:where(div[data-testid="stHorizontalBlock"] div[data-testid="stButton"] button) {{
    border-radius:999px !important; font-family:'Oswald'; font-size:.78rem; letter-spacing:.2px;
    padding:.4rem .5rem !important; white-space:nowrap; border:1px solid rgba(255,255,255,.10) !important;
    background:rgba(255,255,255,.03) !important; color:#C9D2DE !important;
    transition:border-color .16s ease, color .16s ease, transform .16s var(--ease-out), box-shadow .16s ease;
}}
:where(div[data-testid="stButton"] button:hover) {{ border-color:{ACCENT} !important; color:#fff !important; transform:translateY(-1px); }}
:where(div[data-testid="stButton"] button:active) {{ transform:scale(0.97); }}
:where(div[data-testid="stButton"] button[kind="primary"]) {{
    background:linear-gradient(135deg,{ACCENT},#a4142c) !important; border-color:transparent !important;
    color:#fff !important; box-shadow:0 4px 16px rgba(228,32,60,.35);
}}

/* --- Menu "Herramientas" (st.popover) y enlace a TikTok (st.link_button) --- */
div[data-testid="stPopover"] > div > button, div[data-testid="stPopover"] button[kind="secondary"],
div[data-testid="stPopover"] button[kind="primary"], div[data-testid="stLinkButton"] a {{
    border-radius:999px !important; font-family:'Oswald'; font-size:.78rem; letter-spacing:.2px;
    padding:.4rem .9rem !important; white-space:nowrap;
    transition:border-color .16s ease, color .16s ease, transform .16s var(--ease-out);
}}
div[data-testid="stLinkButton"] a {{
    border:1px solid rgba(255,255,255,.10) !important; background:rgba(255,255,255,.03) !important;
    color:#C9D2DE !important; display:flex; align-items:center; justify-content:center;
}}
div[data-testid="stLinkButton"] a:hover {{ border-color:{ACCENT} !important; color:#fff !important; }}
div[data-testid="stLinkButton"] a:active {{ transform:scale(0.97); }}
div[data-testid="stPopoverBody"], div[data-baseweb="popover"] div[role="tooltip"] {{
    background:var(--bg-card) !important; border:1px solid var(--border-subtle) !important;
    border-radius:14px !important; padding:.6rem !important;
}}

/* --- Hero slider (1 diapositiva centrada + flechas + puntos) --- */
@keyframes heroFade {{ from {{ opacity:0; transform:translateY(6px); }} to {{ opacity:1; transform:translateY(0); }} }}
div[class*="st-key-hero_banner"] {{
    background:linear-gradient(135deg,{ACCENT}26,var(--bg-card) 55%);
    border:1px solid rgba(255,255,255,.08); border-radius:20px; padding:28px 20px 14px; margin:.2rem 0 1.4rem;
}}
div[class*="st-key-hero_banner"] > div {{ background:transparent; border:none; padding:0; margin:0; }}
.hero-slide-body {{ text-align:center; animation:heroFade 220ms var(--ease-out) both; }}
.hero-badge {{ font-family:'Oswald'; font-size:.72rem; font-weight:700; letter-spacing:2px; color:#fff;
    background:rgba(0,0,0,.35); display:inline-block; padding:4px 12px; border-radius:20px; margin-bottom:14px;
    width:fit-content; }}
.hero-headline {{ font-family:'Bebas Neue'; font-size:2.4rem; line-height:1.08; color:#fff; letter-spacing:.5px; }}
.hero-sub {{ color:var(--text-secondary); font-size:.94rem; margin:10px auto 4px; max-width:620px; line-height:1.4; }}
div[class*="st-key-hero_banner"] div[data-testid="stButton"] button[kind="primary"] {{
    padding:.6rem 1.3rem !important; font-size:.85rem !important;
}}

/* Flechas de navegacion del slider */
div[class*="st-key-hero_prev"] button, div[class*="st-key-hero_next"] button {{
    border-radius:50% !important; width:38px; height:38px; padding:0 !important;
    font-family:'Oswald'; font-size:1.1rem !important; line-height:1 !important;
    display:flex; align-items:center; justify-content:center;
}}

/* Puntos indicadores de posicion */
.hero-dots {{ display:flex; justify-content:center; gap:7px; margin-top:16px; }}
.hero-dot {{ width:7px; height:7px; border-radius:50%; background:rgba(255,255,255,.22);
    transition:background-color 160ms ease, transform 160ms var(--ease-out); }}
.hero-dot.active {{ background:{ACCENT}; transform:scale(1.3); }}

/* Widget dinamico del slide (Partido / MVP / lider / noticia) */
.hero-widget-wrap {{ max-width:420px; margin:18px auto 6px; animation:heroFade 220ms var(--ease-out) both; }}
.hero-widget-card {{ background:rgba(0,0,0,.28); border:1px solid rgba(255,255,255,.10); border-radius:16px;
    padding:20px; display:flex; flex-direction:column; justify-content:center;
    text-decoration:none; transition:border-color .18s ease; }}
a.hero-widget-card:hover {{ border-color:{ACCENT}; }}
.hw-tag {{ font-family:'Oswald'; font-size:.68rem; font-weight:700; letter-spacing:1.5px; color:var(--text-amber);
    margin-bottom:12px; text-align:center; }}
.hw-duel-row {{ display:flex; align-items:center; justify-content:center; gap:14px; }}
.hw-team {{ display:flex; flex-direction:column; align-items:center; gap:6px; flex:1; min-width:0; }}
.hw-team img {{ width:56px; height:56px; object-fit:contain; }}
.hw-team span {{ font-family:'Oswald'; font-weight:700; font-size:.85rem; color:#fff; }}
.hw-vs {{ font-family:'Bebas Neue'; font-size:1.3rem; color:var(--text-secondary); flex:0 0 auto; }}
.hw-sub {{ text-align:center; color:var(--text-secondary); font-size:.78rem; margin-top:12px; }}
.hw-leader-row {{ display:flex; align-items:center; justify-content:center; gap:14px; }}
.hw-leader-logo {{ width:56px; height:56px; object-fit:contain; }}
.hw-leader-name {{ font-family:'Oswald'; font-weight:700; font-size:1.15rem; color:#fff; }}
.hw-leader-record {{ color:var(--text-secondary); font-size:.85rem; margin-top:2px; }}
.hw-news-title {{ font-family:'Oswald'; font-weight:600; font-size:1.05rem; color:#fff; line-height:1.3; text-align:center; }}
.hw-news-cta {{ color:{ACCENT}; font-size:.82rem; font-weight:600; margin-top:10px; text-align:center; }}
.hw-player-row {{ display:flex; align-items:center; justify-content:center; gap:14px; }}
.hw-player-photo {{ width:64px; height:64px; border-radius:50%; object-fit:cover; background:#222;
    border:2px solid rgba(255,255,255,.2); }}
.hw-player-name {{ font-family:'Oswald'; font-weight:700; font-size:1.15rem; color:#fff; text-align:left; }}
.hw-player-meta {{ color:var(--text-secondary); font-size:.8rem; margin-top:2px; text-align:left; }}
.hw-stat-row {{ display:flex; justify-content:center; gap:18px; margin-top:14px; padding-top:14px;
    border-top:1px solid rgba(255,255,255,.08); }}
.hw-stat {{ text-align:center; }}
.hw-stat-value {{ font-family:'Oswald'; font-weight:700; font-size:1.15rem; color:#fff; }}
.hw-stat-label {{ color:var(--text-secondary); font-size:.65rem; letter-spacing:.4px; text-transform:uppercase; margin-top:2px; }}
@media (max-width:900px) {{
  div[class*="st-key-hero_banner"] > div {{ padding:20px 14px 16px; }}
  .hero-headline {{ font-size:1.9rem; }}
  .hero-sub {{ max-width:100%; }}
}}

/* --- Tarjetas de partido (Jornada · horarios en España, grid de 3 columnas) --- */
.game-card {{ display:flex; align-items:center; background:var(--bg-card-alt); border:1px solid var(--border-subtle);
    border-radius:12px; padding:12px 10px; margin-bottom:12px; height:100%; transition:border-color .18s ease; }}
.game-card:hover {{ border-color:{ACCENT}; }}
.game-team {{ flex:0 0 38%; max-width:38%; display:flex; align-items:center; gap:8px; min-width:0; }}
.game-team.gt-home {{ justify-content:flex-end; text-align:right; }}
.game-team.gt-away {{ justify-content:flex-start; text-align:left; }}
.game-team img {{ width:34px; height:34px; object-fit:contain; flex:0 0 auto; }}
.game-team .gt-name {{ font-family:'Oswald'; font-weight:700; font-size:.82rem; color:var(--text-primary);
    line-height:1.15; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }}
.game-center {{ flex:0 0 24%; max-width:24%; display:flex; flex-direction:column; align-items:center; gap:4px; }}
.game-pill {{ background:rgba(255,255,255,.06); border:1px solid var(--border-subtle); border-radius:20px;
    padding:5px 8px; text-align:center; width:100%; }}
.game-vs {{ font-family:'Bebas Neue'; font-size:1.05rem; color:var(--text-primary); letter-spacing:1px; }}
.game-score {{ font-family:'Bebas Neue'; font-size:1.2rem; color:var(--text-primary); letter-spacing:1px; }}
.game-time {{ color:var(--text-amber); font-size:.64rem; font-weight:600; margin-top:5px; text-align:center; line-height:1.25; }}
.game-final {{ color:var(--text-secondary); font-size:.64rem; font-weight:700; letter-spacing:1px; margin-top:2px; }}
@media (max-width:900px) {{
  .game-card {{ flex-wrap:wrap; }}
  .game-team {{ flex:0 0 42%; max-width:42%; }}
  .game-team .gt-name {{ font-size:.8rem; white-space:normal; }}
  .game-center {{ flex:0 0 100%; max-width:100%; order:3; margin-top:10px; }}
}}

/* --- Titulos de seccion --- */
.sect-title {{ font-family:'Bebas Neue'; font-size:2.1rem; letter-spacing:1px; color:#fff; margin:.1rem 0 .2rem;
    position:relative; display:inline-block; }}
.sect-title::after {{ content:""; display:block; height:4px; width:64px; margin-top:4px; border-radius:3px;
    background:linear-gradient(90deg,{ACCENT},{ACCENT2}); }}
.sect-sub {{ color:#8A93A6; font-size:.92rem; margin:.3rem 0 1.1rem; }}

/* --- Cards genericas --- */
.lb-row, .std-row, .news-card {{ background:#1B2230; border:1px solid rgba(255,255,255,.05); border-radius:14px;
    transition:transform .15s, border-color .15s; }}
.lb-row {{ display:flex; align-items:center; gap:14px; padding:10px 16px; margin-bottom:10px; }}
.lb-row:hover {{ transform:translateX(4px); border-color:rgba(228,32,60,.5); }}
.lb-rank {{ font-family:'Oswald'; font-weight:700; font-size:1.45rem; width:36px; text-align:center; color:#8A93A6; }}
.rank-1 {{ color:#FFD54A; }} .rank-2 {{ color:#C9D2DE; }} .rank-3 {{ color:#E0925B; }}
.lb-photo {{ width:52px; height:52px; border-radius:50%; object-fit:cover; background:#222C3D; border:2px solid rgba(255,255,255,.15); }}
.lb-info {{ flex:1; min-width:0; }}
.lb-name {{ font-family:'Oswald'; font-weight:600; font-size:1.15rem; color:#fff; line-height:1.15; }}
.lb-meta {{ color:#8A93A6; font-size:.78rem; margin-bottom:6px; }}
.lb-track {{ height:8px; background:rgba(255,255,255,.06); border-radius:6px; overflow:hidden; }}
.lb-fill {{ height:100%; border-radius:6px; }}
.lb-value {{ font-family:'Oswald'; font-weight:700; font-size:1.5rem; color:#fff; text-align:right; white-space:nowrap; }}
.lb-value span {{ font-size:.72rem; color:#8A93A6; font-weight:500; margin-left:3px; }}
.prof-hd {{ display:flex; align-items:center; gap:16px; margin:.4rem 0 1rem; }}
.prof-hd img {{ width:84px; height:84px; border-radius:50%; object-fit:cover; background:#222C3D; border:3px solid rgba(255,255,255,.15); }}
.prof-name {{ font-family:'Oswald'; font-size:2rem; color:#fff; line-height:1; }}
.prof-meta {{ color:{ACCENT}; font-weight:600; font-size:.95rem; }}

/* --- Equipos --- */
.conf-h {{ font-family:'Oswald'; font-weight:700; font-size:1.05rem; letter-spacing:1px; color:{ACCENT2}; margin:1rem 0 .5rem; }}
.team-pick img {{ width:40px; height:40px; object-fit:contain; display:block; margin:0 auto 4px; }}
.team-hd {{ display:flex; align-items:center; gap:18px; margin:1rem 0 1.1rem; padding:18px 22px; border-radius:16px;
    border:1px solid rgba(255,255,255,.08); }}
.team-hd img {{ width:76px; height:76px; object-fit:contain; }}
.team-hd .tname {{ font-family:'Bebas Neue'; font-size:2.3rem; color:#fff; line-height:1; letter-spacing:1px; }}
.team-hd .tmeta {{ color:rgba(255,255,255,.85); font-weight:600; font-size:.95rem; margin-top:3px; }}
div[class*="st-key-roster_"] button {{
    border-radius:8px !important; justify-content:flex-start !important;
    font-family:'Inter'; font-size:.86rem; font-weight:500; letter-spacing:0; text-transform:none;
    padding:.5rem .7rem !important; border:1px solid transparent !important; background:transparent !important;
    color:#E9EDF5 !important;
}}
div[class*="st-key-roster_"] button > div {{ justify-content:flex-start !important; width:100%; }}
div[class*="st-key-roster_"] button p {{ text-align:left !important; }}
div[class*="st-key-roster_"] button:hover {{
    background:rgba(228,32,60,.10) !important; border-color:rgba(228,32,60,.35) !important; transform:none;
}}
.team-news-card {{ position:relative; height:100%; min-height:300px; border-radius:16px; overflow:hidden;
    border:1px solid rgba(255,255,255,.08); display:flex; flex-direction:column; justify-content:flex-end;
    padding:20px; }}
.team-news-card .tn-tag {{ font-family:'Oswald'; font-size:.7rem; font-weight:700; letter-spacing:1.5px;
    color:#fff; background:rgba(0,0,0,.35); display:inline-block; padding:3px 10px; border-radius:20px;
    margin-bottom:12px; width:fit-content; }}
.team-news-card .tn-title {{ font-family:'Bebas Neue'; font-size:1.6rem; color:#fff; margin-bottom:6px; }}
.team-news-card .tn-sub {{ color:rgba(255,255,255,.75); font-size:.86rem; }}

/* --- Clasificacion --- */
.div-h {{ font-family:'Oswald'; font-weight:700; font-size:.9rem; letter-spacing:1px; color:#8A93A6; text-transform:uppercase;
    margin:0 0 .5rem; padding-left:.5rem; border-left:3px solid {ACCENT2}; }}
.std-row {{ display:flex; align-items:center; gap:12px; padding:8px 14px; margin-bottom:6px; }}
.std-row:hover {{ border-color:rgba(31,163,232,.5); }}
.std-rank {{ width:22px; color:#8A93A6; font-weight:700; font-family:'Oswald'; }}
.std-logo {{ width:28px; height:28px; object-fit:contain; }}
.std-team {{ flex:1; min-width:0; font-weight:600; color:#fff; font-size:.92rem; }}
.std-team small {{ color:#8A93A6; font-weight:500; }}
.std-stat {{ width:50px; text-align:center; font-family:'Oswald'; font-weight:600; color:#E9EDF5; font-size:.92rem; }}
.std-head {{ display:flex; align-items:center; gap:12px; padding:0 14px; margin-bottom:4px; color:#8A93A6; font-size:.68rem; letter-spacing:.5px; text-transform:uppercase; }}
.std-head .std-rank {{ width:22px; }} .std-head .std-logo {{ width:28px; }} .std-head .std-team {{ flex:1; }}
.std-head .std-stat {{ width:50px; text-align:center; }}
.div-block {{ margin-bottom:1.2rem; }}

/* Filas de Clasificacion clicables: la fila es HTML, el boton real va
   superpuesto (transparente) encima para que toda la fila sea el area de clic. */
div[class*="st-key-std_row_"] {{ position:relative; margin-bottom:6px; }}
div[class*="st-key-std_row_"] .std-row {{ margin-bottom:0; cursor:pointer; }}
div[class*="st-key-std_row_"] div[data-testid="stButton"] {{
    position:absolute; inset:0; z-index:2; margin:0 !important;
}}
div[class*="st-key-std_row_"] div[data-testid="stButton"] button {{
    width:100%; height:100%; opacity:0; padding:0; margin:0; border:none !important;
    background:transparent !important; cursor:pointer; box-shadow:none !important;
    transform:none !important;
}}
div[class*="st-key-std_row_"]:hover .std-row {{ border-color:{ACCENT}; }}

/* --- Laboratorio / Tendencias / Matchups / Football IQ / Quiz --- */
.stat-card {{ background:#1B2230; border:1px solid rgba(255,255,255,.06); border-radius:14px; padding:16px 18px; height:100%; }}
.stat-card .sc-label {{ color:#8A93A6; font-size:.72rem; letter-spacing:.5px; text-transform:uppercase; font-weight:600; }}
.stat-card .sc-value {{ font-family:'Oswald'; font-weight:700; font-size:1.6rem; color:#fff; margin-top:4px; }}
.up-badge {{ color:#3ED598; font-weight:700; }} .down-badge {{ color:{ACCENT}; font-weight:700; }}
.duel-card {{ background:linear-gradient(135deg,{ACCENT}22,{ACCENT2}11); border:1px solid rgba(228,32,60,.35);
    border-radius:18px; padding:22px 26px; margin:1rem 0; }}
.duel-card .dc-tag {{ color:{ACCENT}; font-family:'Oswald'; font-weight:700; letter-spacing:2px; font-size:.75rem; }}
.duel-card .dc-title {{ font-family:'Bebas Neue'; font-size:2rem; color:#fff; margin:.2rem 0; }}
.duel-card .dc-detail {{ color:#C9D2DE; font-size:.92rem; }}
.iq-level-tag {{ display:inline-block; padding:4px 14px; border-radius:20px; font-family:'Oswald'; font-weight:700;
    font-size:.78rem; letter-spacing:1px; margin-bottom:1rem; }}
.iq-rookie {{ background:#1FA3E822; color:#1FA3E8; border:1px solid #1FA3E855; }}
.iq-aficionado {{ background:#FFD54A22; color:#FFD54A; border:1px solid #FFD54A55; }}
.iq-avanzado {{ background:{ACCENT}22; color:{ACCENT}; border:1px solid {ACCENT}55; }}
.term-card {{ background:#1B2230; border:1px solid rgba(255,255,255,.06); border-radius:14px; padding:16px 18px; margin-bottom:12px; }}
.term-card .tc-term {{ font-family:'Oswald'; font-weight:700; font-size:1.1rem; color:#fff; }}
.term-card .tc-def {{ color:#C9D2DE; font-size:.9rem; margin-top:4px; }}
.term-card .tc-example {{ color:#8A93A6; font-size:.84rem; margin-top:6px; font-style:italic; }}
.quiz-card {{ background:#1B2230; border:1px solid rgba(255,255,255,.08); border-radius:16px; padding:20px 24px; margin-bottom:1rem; }}
.quiz-score {{ font-family:'Bebas Neue'; font-size:3rem; color:{ACCENT}; text-align:center; }}

/* --- Contexto de estadisticas (DATOS -> CONTEXTO) --- */
.stat-context-card {{ background:#1B2230; border:1px solid rgba(255,255,255,.07); border-radius:14px;
    padding:14px 16px; height:100%; }}
.sxc-label {{ color:#8A93A6; font-size:.72rem; letter-spacing:.5px; text-transform:uppercase; font-weight:600; }}
.sxc-value {{ font-family:'Oswald'; font-weight:700; font-size:1.7rem; color:#fff; margin:2px 0 8px; }}
.sxc-unit {{ font-size:.85rem; color:#8A93A6; font-weight:600; }}
.sxc-row {{ display:flex; gap:18px; padding-top:8px; border-top:1px solid rgba(255,255,255,.06); }}
.sxc-mini-label {{ color:#5C6579; font-size:.62rem; letter-spacing:.4px; text-transform:uppercase; font-weight:700; }}
.sxc-mini-value {{ font-family:'Oswald'; font-weight:700; font-size:1.05rem; color:#C9D2DE; margin-top:2px; }}
.sxc-insight {{ color:#C9D2DE; font-size:.82rem; margin-top:10px; line-height:1.35; }}
.sxc-pop {{ color:#5C6579; font-size:.7rem; margin-top:6px; }}

/* --- "¿Por qué?" (desglose deterministico) --- */
.why-box {{ padding:4px 2px 2px; }}
.why-row {{ display:flex; justify-content:space-between; padding:7px 0; border-bottom:1px solid rgba(255,255,255,.06); font-size:.86rem; }}
.why-row:last-of-type {{ border-bottom:none; }}
.why-label {{ color:#8A93A6; }}
.why-value {{ font-family:'Oswald'; font-weight:600; color:#fff; }}

/* --- Footer --- */
.site-footer {{ margin-top:3rem; padding:2rem 0 1.4rem; border-top:1px solid rgba(255,255,255,.08); text-align:center; }}
.footer-brand {{ display:flex; align-items:center; justify-content:center; gap:10px; margin-bottom:.9rem; }}
.footer-brand img {{ width:34px; height:34px; border-radius:50%; object-fit:cover; }}
.footer-brand span {{ font-family:'Oswald'; font-weight:700; font-size:1.05rem; color:#fff; letter-spacing:.5px; }}
.footer-links {{ display:flex; justify-content:center; gap:22px; flex-wrap:wrap; margin-bottom:1rem; }}
.footer-links a {{ color:#C9D2DE; text-decoration:none; font-size:.88rem; font-weight:600; transition:color .15s; }}
.footer-links a:hover {{ color:{ACCENT}; }}
.footer-meta {{ color:#5C6579; font-size:.78rem; }}

/* --- Widgets nativos --- */
div[data-baseweb="select"] > div {{ border-radius:10px !important; }}
</style>
"""
