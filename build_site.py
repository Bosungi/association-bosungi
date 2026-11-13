#!/usr/bin/env python3
"""Site multi-pages Bosungi : assemble template.html (sections v3) + sections.html (nouvelles) en 6 pages.
Sortie : site/ (pages + img/) — c'est le dossier à glisser dans Netlify.
"""
import re, shutil, pathlib, subprocess, os
THEME = os.environ.get('THEME', '')  # THEME=ciel -> variante bleu ciel dans site-ciel/
root = pathlib.Path(__file__).parent
T = (root / 'template.html').read_text(encoding='utf-8')
S = (root / 'sections.html').read_text(encoding='utf-8')

def blocks(src):
    parts = re.split(r'<!-- ===== ([A-Z_]+) ===== -->', src)
    return {parts[i]: parts[i + 1] for i in range(1, len(parts), 2)}

B = blocks(T[T.index('<!-- ===== NAV'):T.index('<!-- ===== FOOTER')])
B.update(blocks(S))
B['HERO'] = B['HERO']  # contient hero + chiffres + manifeste + bandeau défilant
for k in ('MISSION', 'CONTACT', 'SOUTENIR', 'EQUIPE'):
    pass
head = T[:T.index('<!-- ===== NAV')]
foot_start = T.index('<!-- ===== FOOTER')
foot = T[foot_start:T.index('<script>')]
script = T[T.index('<script>'):T.rindex('</body>')]
# l'ancienne équipe (3 cartes) est remplacée par la version complète de sections.html
B['EQUIPE'] = blocks(S)['EQUIPE']


# ---------- JOURNAL « Nos actions » (blog) : content/actions/*.md ----------
import html as _h
ARR = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M13 6l6 6-6 6"/></svg>'
MOIS = ['janvier','février','mars','avril','mai','juin','juillet','août','septembre','octobre','novembre','décembre']
def lire_action(p):
    raw = p.read_text(encoding='utf-8')
    _, fm, corps = raw.split('---', 2)
    d = {}
    for l in fm.strip().splitlines():
        if ':' not in l: continue
        k, v = l.split(':', 1); v = v.strip()
        if len(v) >= 2 and v[0] == v[-1] == '"': v = v[1:-1]
        d[k.strip()] = v
    d['slug'] = 'action-' + p.stem
    d.setdefault('resume', d.get('description', ''))
    d.setdefault('categorie', d.get('tag', 'Action'))
    d.setdefault('alt', d.get('title', ''))
    d.setdefault('citation', '')
    if not d.get('date_affichee'):
        y, m, j = (d['date'].split('-') + ['01', '01'])[:3]
        d['date_affichee'] = f"{int(j)} {MOIS[int(m) - 1]} {y}"
    corps = corps.strip()
    d['html'] = corps if corps.startswith('<') else ''.join(f'<p>{_h.escape(x.strip())}</p>' for x in corps.split('\n\n') if x.strip())
    d['photos'] = [x.strip() for x in d.get('photos', '').split(',') if x.strip()]
    return d

def src_img(v):
    """nom court (photos du site, dossier opt/) ou chemin envoyé par l'espace d'Annie (img/uploads/...)"""
    return v if '/' in v else f'__IMG_{v}__'

ACTIONS = sorted((lire_action(p) for p in (root / 'content' / 'actions').glob('*.md')), key=lambda a: a['date'], reverse=True)

def carte(a, i=0):
    return (f'<a class="j-card rv" style="--d:{(i % 3) * .08:.2f}s" href="{a["slug"]}.html" data-cat="{_h.escape(a["categorie"])}">'
            f'<div class="ph"><img src="{src_img(a["image"])}" alt="{_h.escape(a["alt"])}" loading="lazy"><span class="j-cat">{_h.escape(a["categorie"])}</span></div>'
            f'<div class="tx"><time datetime="{a["date"]}">{a["date_affichee"]}</time><h3>{_h.escape(a["title"])}</h3><p>{_h.escape(a["resume"])}</p>'
            f'<span class="j-more">Lire l\'action {ARR}</span></div></a>')

cats = []
for a in ACTIONS:
    if a['categorie'] not in cats: cats.append(a['categorie'])
filtres = '<button class="on" data-j="all">Toutes</button>' + ''.join(f'<button data-j="{_h.escape(c)}">{_h.escape(c)}</button>' for c in cats)
B['JOURNAL'] = f"""<section class="sec j-sec" id="journal">
  <div class="wrap">
    <div class="sec-head">
      <span class="eyebrow rv">Le journal de terrain</span>
      <h2 class="wr" data-wr>Ce que nous avons fait, <span class="accent">action par action.</span></h2>
      <p class="rv">Rentrées scolaires, ateliers, journées avec les familles, ouverture de la maison : chaque action a sa page, avec ses photos.</p>
    </div>
    <div class="gal-bar j-bar rv" role="group" aria-label="Filtrer les actions">{filtres}</div>
    <div class="j-grid" id="jgrid">{''.join(carte(a, i) for i, a in enumerate(ACTIONS))}</div>
  </div>
</section>
<script>document.querySelectorAll('.j-bar button').forEach(function(b){{b.addEventListener('click',function(){{document.querySelectorAll('.j-bar button').forEach(function(x){{x.classList.toggle('on',x===b)}});var f=b.dataset.j;document.querySelectorAll('#jgrid .j-card').forEach(function(c){{c.style.display=(f==='all'||c.dataset.cat===f)?'':'none'}})}})}});</script>
"""
B['JOURNAL_TEASER'] = f"""<section class="sec j-sec j-teaser">
  <div class="wrap">
    <div class="j-head">
      <div class="sec-head" style="margin-bottom:0">
        <span class="eyebrow rv">Nos dernières actions</span>
        <h2 class="wr" data-wr>Sur le terrain, <span class="accent">chaque semaine.</span></h2>
      </div>
      <a href="actions.html#journal" class="btn btn-primary rv">Toutes nos actions {ARR}</a>
    </div>
    <div class="j-grid">{''.join(carte(a, i) for i, a in enumerate(ACTIONS[:3]))}</div>
  </div>
</section>
"""

EXTRA_CSS = open(root / 'site.css', encoding='utf-8').read()
if THEME: EXTRA_CSS += '\n' + open(root / f'couleur-{THEME}.css', encoding='utf-8').read()
head = head.replace('</style>', EXTRA_CSS + '\n</style>')

PAGES = [
    ('index.html', 'Accueil', None, ['HERO', 'VOIX', 'MISSION', 'PRES_TEASER', 'POLES_TEASER', 'JOURNAL_TEASER', 'MAISON_TEASER', 'IMPACT', 'APPEL', 'CONVICTION', 'CONTACT']),
    ('association.html', "L'association", ("Qui sommes-nous", "Du ghetto <span class='accent'>à l'espoir.</span>", "Fondée en mars 2021 par Annie Kiamuangana-Boloko, Bosungi aide les orphelines et les jeunes filles vulnérables de Kinshasa à se reconstruire.", 'fs_groupe'),
        ['PRESIDENTE', 'ANNIE_TERRAIN', 'APPROCHE', 'METHODE', 'HISTOIRE', 'SUITE', 'EQUIPE', 'STATUT']),
    ('constat.html', 'Le constat', ("Le constat", "Pourquoi c'est <span class='accent'>urgent.</span>", "À Kinshasa, les filles orphelines ou issues de familles très précaires sont les premières à quitter l'école et à être exposées aux violences.", 'kin_rue'),
        ['CONSTAT', 'PREVENTION', 'APPEL']),
    ('actions.html', 'Nos actions', ("Nos actions", "Cinq pôles pour <span class='accent'>se relever.</span>", "Éducation, aide sociale, suivi psycho-médical, ateliers, soutien aux familles et à la communauté : un accompagnement complet, du premier jour à l'autonomie.", 'remise'),
        ['JOURNAL', 'POLES']),
    ('maison.html', "La maison d'accueil", ("La maison d'accueil", "Une maison <span class='accent'>pour elles.</span>", "Inaugurée le 16 août 2026 et ouverte aux jeunes filles le 2 septembre, au 5B, 1ère rue, quartier Kimbangu, à Kalamu.", 'maison'),
        ['MAISON_REPONSE', 'PORTE', 'MAISON', 'PREMIER_JOUR', 'TERRAIN', 'BESOINS']),
    ('transparence.html', 'Transparence', ("Transparence", "Chaque euro <span class='accent'>a une adresse.</span>", "Bosungi est une structure de terrain, sans intermédiaire : l'argent arrive directement dans la Maison d'accueil de Kimbangu.", 'kits2026'),
        ['TRANSPARENCE', 'HELLOASSO', 'CONTACT']),
    ('partenaires.html', 'Partenaires', ("Partenaires", "Construisons <span class='accent'>ensemble.</span>", "Entreprises, fondations, écoles, associations : financez un chantier entier ou une part, et suivez ses résultats sur place.", 'groupe'),
        ['CHANTIERS', 'PARTENARIAT', 'CONTACT']),
    ('galerie.html', 'Galerie', ("Galerie", "Retour <span class='accent'>en images.</span>", "Rentrées scolaires, ateliers, journées avec les familles, ouverture de la maison : cinq ans d'actions en photos et en vidéos.", 'kits2026'),
        ['GALERIE', 'MOTS', 'MEDIAS']),
    ('soutenir.html', 'Nous soutenir', ("Nous soutenir", "Ne passez pas <span class='accent'>votre chemin.</span>", "Un don, un kit, une heure de votre temps, un partenariat : chaque geste compte pour changer la vie d'une fille.", 'hero4'),
        ['SAMARITAIN', 'IMPACT', 'GESTE', 'HELLOASSO', 'SOUTENIR', 'BESOINS', 'STATUT', 'CONTACT']),
]


# ---------- pages article du journal ----------
for i, a in enumerate(ACTIONS):
    prev_a = ACTIONS[i + 1] if i + 1 < len(ACTIONS) else None   # plus ancienne
    next_a = ACTIONS[i - 1] if i > 0 else None                   # plus récente
    paras = a['html']
    cit = f'<blockquote class="art-quote">« {_h.escape(a["citation"].strip("«» "))} »</blockquote>' if a.get('citation') and not a['citation'].startswith('#') else (f'<p class="art-tag">{_h.escape(a["citation"])}</p>' if a.get('citation') else '')
    pics = ''.join(f'<figure class="rv-img"><img src="{src_img(p)}" alt="{_h.escape(a["title"])}" loading="lazy"></figure>' for p in a['photos'])
    nav_art = '<nav class="art-nav" aria-label="Autres actions">'
    nav_art += (f'<a href="{prev_a["slug"]}.html" class="prev"><small>Action précédente</small><b>{_h.escape(prev_a["title"])}</b></a>' if prev_a else '<span></span>')
    nav_art += (f'<a href="{next_a["slug"]}.html" class="next"><small>Action suivante</small><b>{_h.escape(next_a["title"])}</b></a>' if next_a else '<span></span>')
    nav_art += '</nav>'
    B['ART_' + a['slug']] = f"""<section class="sec art-sec">
  <div class="wrap art-wrap">
    <a href="actions.html#journal" class="art-back">← Toutes nos actions</a>
    <div class="art-meta"><time datetime="{a['date']}">{a['date_affichee']}</time><span class="j-cat">{_h.escape(a['categorie'])}</span></div>
    <figure class="art-main rv-img"><img src="{src_img(a['image'])}" alt="{_h.escape(a['alt'])}"></figure>
    <div class="art-body">{paras}{cit}</div>
    {'<div class="art-pics">' + pics + '</div>' if pics else ''}
    {nav_art}
  </div>
</section>
"""
    PAGES.append((a['slug'] + '.html', a['title'], (a['date_affichee'] + ' · ' + a['categorie'], _h.escape(a['title']), _h.escape(a['resume']), a['image']), ['ART_' + a['slug'], 'HELLOASSO']))

NAV_LINKS = [('index.html', 'Accueil'), ('constat.html', 'Le constat'), ('association.html', "L'association"),
             ('maison.html', "Maison d'accueil"), ('actions.html', 'Nos actions'), ('transparence.html', 'Transparence'),
             ('partenaires.html', 'Partenaires'), ('galerie.html', 'Galerie')]

def nav(active):
    cur = ' class="current" aria-current="page"'
    links = ''.join(f'<a href="{h}"{cur if h == active else ""}>{t}</a>' for h, t in NAV_LINKS)
    n = B['NAV']
    n = re.sub(r'<nav class="menu" id="menu"[^>]*>.*?</nav>',
               f'<nav class="menu" id="menu" aria-label="Navigation principale">{links}<a href="soutenir.html" class="btn btn-sun">Nous soutenir</a></nav>', n, flags=re.S)
    return n.replace('href="#top"', 'href="index.html"')

def page_hero(eyebrow, title, lead, img):
    return f'''<section class="phero">
  <div class="phero-bg" aria-hidden="true"><img src="{img if '/' in img else '__IMG_' + img + '__'}" alt=""></div>
  <div class="wrap phero-in">
    <svg class="phero-sun" viewBox="0 0 1300 700" aria-hidden="true"><g class="phero-rays"></g></svg>
    <span class="eyebrow light rv">{eyebrow}</span>
    <h1 class="wr" data-wr>{title}</h1>
    <p class="rv" style="--d:.4s">{lead}</p>
  </div>
</section>
'''

# liens internes : anciens #ancres de la page unique vers les bonnes pages
LINKS = {'#soutenir': 'soutenir.html', '#maison': 'maison.html', '#presidente': 'association.html#presidente',
         '#association': 'association.html', '#histoire': 'association.html#histoire', '#galerie': 'galerie.html',
         '#actions': 'actions.html', '#contact': 'soutenir.html#contact', '#manifeste': '#manifeste'}

out = root / ('site-' + THEME if THEME else 'site')
if out.exists(): shutil.rmtree(out)
(out / 'img').mkdir(parents=True)
used = set()
for fname, title, ph, secs in PAGES:
    body = ''
    if ph: body += page_hero(*ph)
    body += ''.join(B[s] for s in secs)
    if fname == 'maison.html': body = re.sub(r'<blockquote class="door rv">.*?</blockquote>', '', body, flags=re.S)  # la phrase est déjà sur la porte
    body += B['SIGNATURE']
    html = head.replace('<title>Association Bosungi — Un espoir, un avenir · Kinshasa</title>',
                        f'<title>{title} · Association Bosungi</title>' if fname != 'index.html' else '<title>Association Bosungi — Ensemble pour elles · Kinshasa</title>')
    html += nav('actions.html' if fname.startswith('action-') else fname) + '\n<main id="top">\n' + body + '\n</main>\n' + foot + script + '</body>\n</html>\n'
    for a, b in LINKS.items():
        html = html.replace(f'href="{a}"', f'href="{b}"')
    # page courante : les liens vers soi redeviennent des ancres
    html = html.replace(f'href="{fname}#', 'href="#')
    first = 'sourire' if fname == 'index.html' else ph[3]
    if '/' not in first: html = html.replace('</head>', f'<link rel="preload" as="image" href="img/{first}.webp" fetchpriority="high">\n</head>', 1)
    used |= set(re.findall(r'__IMG_([a-z0-9_]+)__', html))
    html = re.sub(r'__IMG_([a-z0-9_]+)__', lambda m: f'img/{m.group(1)}.' + ('webp' if (root / 'opt' / f'{m.group(1)}.webp').exists() else 'jpg'), html)
    (out / fname).write_text(html, encoding='utf-8')
shutil.copytree(root / 'clips', out / 'clips')
for n in sorted(used):
    ext = 'webp' if (root / 'opt' / f'{n}.webp').exists() else 'jpg'
    shutil.copy(root / 'opt' / f'{n}.{ext}', out / 'img' / f'{n}.{ext}')

if (root / 'img' / 'uploads').exists(): shutil.copytree(root / 'img' / 'uploads', out / 'img' / 'uploads', dirs_exist_ok=True)
badge = root / 'outils' / 'ajouter_badge.py'
if os.environ.get('BADGE', '1') == '1' and badge.exists():
    subprocess.run(['python3', str(badge), str(out), '--campagne', 'bosungi', '--jours', os.environ.get('JOURS', '6')], check=True)
if (root / 'admin').exists():
    shutil.copytree(root / 'admin', out / 'admin', dirs_exist_ok=True)
    adm = out / 'admin' / 'index.html'
    coffre = (root / 'admin' / 'coffre.txt').read_text().strip() if (root / 'admin' / 'coffre.txt').exists() else ''
    adm.write_text(adm.read_text().replace('__REPO__', os.environ.get('GITHUB_REPOSITORY', 'COMPTE/bosungi-site')).replace('__COFFRE__', coffre))
    for f in ('coffre.txt',):
        (out / 'admin' / f).unlink(missing_ok=True)
    # raccourcis faciles à retenir
    for alias in ('ecrire', 'publier', 'espace'):
        (out / alias).mkdir(exist_ok=True)
        (out / alias / 'index.html').write_text('<!doctype html><meta charset="utf-8"><meta name="robots" content="noindex"><meta http-equiv="refresh" content="0; url=../admin/"><a href="../admin/">Espace de publication</a>')
    assert 'Espace de publication' in adm.read_text() and 'refresh' not in adm.read_text()
size = sum(f.stat().st_size for f in out.rglob('*') if f.is_file())
print(f'{len(PAGES)} pages, {len(used)} images, {size/1024/1024:.1f} Mo')
