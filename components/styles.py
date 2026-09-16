"""components/styles.py — hoja de estilos unica de la app (CSS inyectado con st.markdown)."""

import nfl_graficos as G

BG, CARD, FG, MUTED, ACCENT, ACCENT2 = G.BG, G.CARD, G.FG, G.MUTED, G.ACCENT, G.ACCENT2


def css_block():
    return f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Oswald:wght@500;600;700&family=Inter:wght@400;500;600;700&display=swap');
html, body, [class*="css"] {{ font-family:'Inter', sans-serif; }}
.stApp {{ background: radial-gradient(1200px 560px at 12% -12%, #2a1420 0%, #0B0E14 45%),
                       radial-gradient(1000px 480px at 100% 0%, #0e2438 0%, #0B0E14 55%); color:#E9EDF5; }}
#MainMenu, footer, header {{ visibility:hidden; }}
.block-container {{ padding-top:1rem; padding-bottom:0; padding-left:2.2rem; padding-right:2.2rem; max-width:1680px; }}
h1,h2,h3 {{ font-family:'Oswald', sans-serif; letter-spacing:.5px; color:#fff; }}

@keyframes fadeUp {{ from {{ opacity:0; transform:translateY(14px); }} to {{ opacity:1; transform:translateY(0); }} }}
.fade-up {{ animation:fadeUp .5s ease both; }}
.d0{{animation-delay:.02s}} .d1{{animation-delay:.06s}} .d2{{animation-delay:.10s}} .d3{{animation-delay:.14s}}
.d4{{animation-delay:.18s}} .d5{{animation-delay:.22s}} .d6{{animation-delay:.26s}} .d7{{animation-delay:.30s}}
.d8{{animation-delay:.34s}} .d9{{animation-delay:.38s}}

/* --- Navbar --- */
.navbar {{ display:flex; align-items:center; gap:14px; padding:.3rem 0 .6rem; }}
.nav-brand {{ font-family:'Oswald'; font-weight:700; font-size:1.22rem; letter-spacing:.5px; color:#fff; display:flex; align-items:center; gap:.4rem; white-space:nowrap; overflow:hidden; }}
.nav-brand img {{ height:32px; width:32px; min-width:32px; border-radius:50%; object-fit:cover; box-shadow:0 0 0 2px rgba(255,255,255,.18); }}
.nav-brand .nfl {{ background:linear-gradient(135deg,{ACCENT},{ACCENT2}); color:#fff; padding:.02rem .4rem; border-radius:6px; font-size:.95rem; }}
:where(div[data-testid="stHorizontalBlock"] div[data-testid="stButton"] button) {{
    border-radius:999px !important; font-family:'Oswald'; font-size:.78rem; letter-spacing:.2px;
    padding:.4rem .5rem !important; white-space:nowrap; border:1px solid rgba(255,255,255,.10) !important;
    background:rgba(255,255,255,.03) !important; color:#C9D2DE !important; transition:all .18s ease;
}}
:where(div[data-testid="stButton"] button:hover) {{ border-color:{ACCENT} !important; color:#fff !important; transform:translateY(-1px); }}
:where(div[data-testid="stButton"] button[kind="primary"]) {{
    background:linear-gradient(135deg,{ACCENT},#a4142c) !important; border-color:transparent !important;
    color:#fff !important; box-shadow:0 4px 16px rgba(228,32,60,.35);
}}

/* --- Hero carousel --- */
.hero-carousel {{ position:relative; height:230px; border-radius:20px; overflow:hidden; margin:.2rem 0 1.4rem;
    border:1px solid rgba(255,255,255,.08); }}
.hc-slide {{ position:absolute; inset:0; display:flex; flex-direction:column; justify-content:flex-end;
    padding:22px 28px; text-decoration:none; opacity:0; animation:hcFade 25s infinite ease-in-out; }}
@keyframes hcFade {{ 0%{{opacity:1}} 16%{{opacity:1}} 20%{{opacity:0}} 96%{{opacity:0}} 100%{{opacity:0}} }}
.hc-tag {{ font-family:'Oswald'; font-size:.72rem; font-weight:700; letter-spacing:2px; color:#fff;
    background:rgba(0,0,0,.35); display:inline-block; padding:3px 10px; border-radius:20px; margin-bottom:10px;
    width:fit-content; }}
.hc-title {{ font-family:'Bebas Neue'; font-size:2.1rem; line-height:1.05; color:#fff; max-width:78%;
    text-shadow:0 2px 12px rgba(0,0,0,.5); }}
.hc-cta {{ color:#fff; opacity:.85; font-size:.82rem; font-weight:600; margin-top:8px; }}
.hc-dots {{ position:absolute; bottom:14px; right:20px; display:flex; gap:6px; }}
.hc-dot {{ width:22px; height:4px; border-radius:3px; background:rgba(255,255,255,.25); animation:hcDot 25s infinite; }}
@keyframes hcDot {{ 0%{{background:#fff}} 16%{{background:#fff}} 20%{{background:rgba(255,255,255,.25)}} 100%{{background:rgba(255,255,255,.25)}} }}

/* --- Titulos de seccion --- */
.sect-title {{ font-family:'Bebas Neue'; font-size:2.1rem; letter-spacing:1px; color:#fff; margin:.1rem 0 .2rem;
    position:relative; display:inline-block; }}
.sect-title::after {{ content:""; display:block; height:4px; width:64px; margin-top:4px; border-radius:3px;
    background:linear-gradient(90deg,{ACCENT},{ACCENT2}); }}
.sect-sub {{ color:#8A93A6; font-size:.92rem; margin:.3rem 0 1.1rem; }}

/* --- Cards genericas --- */
.lb-row, .std-row, .news-card {{ background:#131A26; border:1px solid rgba(255,255,255,.05); border-radius:14px;
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
.div-grid {{ display:grid; grid-template-columns:1fr 1fr; gap:0 26px; }}
@media (max-width:900px) {{ .div-grid {{ grid-template-columns:1fr; }} }}
.div-block {{ margin-bottom:1.2rem; }}

/* --- Laboratorio / Tendencias / Matchups / Football IQ / Quiz --- */
.stat-card {{ background:#131A26; border:1px solid rgba(255,255,255,.06); border-radius:14px; padding:16px 18px; height:100%; }}
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
.term-card {{ background:#131A26; border:1px solid rgba(255,255,255,.06); border-radius:14px; padding:16px 18px; margin-bottom:12px; }}
.term-card .tc-term {{ font-family:'Oswald'; font-weight:700; font-size:1.1rem; color:#fff; }}
.term-card .tc-def {{ color:#C9D2DE; font-size:.9rem; margin-top:4px; }}
.term-card .tc-example {{ color:#8A93A6; font-size:.84rem; margin-top:6px; font-style:italic; }}
.quiz-card {{ background:#131A26; border:1px solid rgba(255,255,255,.08); border-radius:16px; padding:20px 24px; margin-bottom:1rem; }}
.quiz-score {{ font-family:'Bebas Neue'; font-size:3rem; color:{ACCENT}; text-align:center; }}

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
