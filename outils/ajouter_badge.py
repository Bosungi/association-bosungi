"""Ajoute le badge « Maquette créée par Toudoum » + bouton vers toudoum.co + verrou d'expiration
à une maquette HTML (fichier unique ou chaque page d'un site multi-pages).

Usage :
  python3 ajouter_badge.py <fichier.html ou dossier> --campagne nom-du-prospect [--jours 6]

- Le logo est intégré dans la page (base64) : marche même en fichier unique, sans dossier img/.
- Le lien porte utm_source=maquette&utm_campaign=<campagne> pour voir dans les stats de toudoum.co
  les visites venues des maquettes.
- Verrou : après <jours> jours à partir d'aujourd'hui (23h59 heure de Paris), écran « Cette maquette a expiré ».
- Relancer le script sur un fichier déjà badgé remplace l'ancien badge (nouvelle date).
- Pour retirer le badge à la vente : --retirer
"""
import sys, os, re, base64, argparse, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
START, END = '<!-- TOUDOUM-BADGE:START -->', '<!-- TOUDOUM-BADGE:END -->'

def snippet(campagne, expiry_iso):
    logo = 'data:image/png;base64,' + base64.b64encode(open(os.path.join(HERE, 'toudoum-logo.png'), 'rb').read()).decode()
    u = lambda med: f'https://www.toudoum.co/?utm_source=maquette&amp;utm_medium={med}&amp;utm_campaign={campagne}'
    return f'''{START}
<style>
.tdm-badge{{position:fixed;left:16px;bottom:16px;z-index:2147483000;display:flex;align-items:center;gap:10px;background:#fff;border:1px solid #E4DCCF;box-shadow:0 10px 30px -12px rgba(15,29,43,.35);padding:8px 8px 8px 14px;border-radius:999px;font:500 12px/1 system-ui,-apple-system,"Segoe UI",sans-serif;color:#5C1420;letter-spacing:.02em;text-decoration:none;transition:bottom .35s,box-shadow .2s}}
.tdm-badge img{{height:22px;width:auto;display:block}}
.tdm-badge b{{font-weight:600;background:#5C1420;color:#fff;border-radius:999px;padding:7px 12px;white-space:nowrap}}
.tdm-badge b i{{font-style:normal;display:inline-block;transition:transform .2s}}
.tdm-badge:hover b i{{transform:translateX(3px)}}
.tdm-badge:hover{{box-shadow:0 14px 34px -12px rgba(92,20,32,.45)}}
.tdm-lock{{position:fixed;inset:0;z-index:2147483600;background:rgba(10,21,32,.94);-webkit-backdrop-filter:blur(6px);backdrop-filter:blur(6px);display:grid;place-items:center;padding:24px;font-family:system-ui,-apple-system,"Segoe UI",sans-serif}}
.tdm-lock[hidden]{{display:none}}
.tdm-box{{background:#F4EEE3;max-width:520px;padding:48px 40px;text-align:center;color:#3A1A1F}}
.tdm-box img{{height:52px;width:auto;margin:0 auto 26px;display:block}}
.tdm-box h2{{font-weight:500;font-size:28px;margin:0 0 14px}}
.tdm-box p{{font-size:16px;line-height:1.6;margin:0}}
.tdm-box .en{{margin-top:14px;font-size:14px;color:#7A6A5E}}
.tdm-cta{{display:inline-block;margin-top:24px;background:#5C1420;color:#fff;padding:14px 24px;border-radius:999px;font-weight:600;font-size:14px;text-decoration:none}}
@media (max-width:560px){{.tdm-badge{{left:12px;bottom:12px;padding:6px 6px 6px 12px;font-size:11px}}.tdm-badge img{{height:18px}}.tdm-badge b{{padding:6px 10px}}}}
@media print{{.tdm-badge{{display:none}}}}
</style>
<a class="tdm-badge" href="{u('badge')}" target="_blank" rel="noopener" aria-label="Maquette créée par Toudoum — créer mon site">
  <span>Maquette créée par</span><img src="{logo}" alt="Toudoum" width="82" height="22"><b>Créer mon site <i aria-hidden="true">→</i></b>
</a>
<div class="tdm-lock" id="tdm-lock" hidden>
  <div class="tdm-box">
    <img src="{logo}" alt="Toudoum" width="196" height="52">
    <h2>Cette maquette a expiré</h2>
    <p>Ce site est une maquette réalisée par Toudoum. La période de consultation est terminée.<br>Contactez Toudoum pour sa mise en ligne.</p>
    <p class="en">This website is a mock-up created by Toudoum. The preview period has ended.</p>
    <a class="tdm-cta" href="{u('lock')}" target="_blank" rel="noopener">Découvrir Toudoum →</a>
  </div>
</div>
<script>
(function(){{
  if(Date.now()>Date.parse('{expiry_iso}')){{var l=document.getElementById('tdm-lock');l.hidden=false;document.documentElement.style.overflow='hidden'}}
  // ne pas cacher un bouton fixe en bas de page (ex. « Appeler », « Contact ») : le badge remonte au-dessus
  var b=document.querySelector('.tdm-badge');
  function lift(){{var y=12;document.querySelectorAll('body *').forEach(function(e){{if(e===b||b.contains(e))return;var s=getComputedStyle(e);if(s.position!=='fixed'||s.display==='none'||s.visibility==='hidden'||+s.opacity===0)return;var r=e.getBoundingClientRect();if(r.width&&r.height&&r.bottom>innerHeight-90&&r.left<260&&r.top<innerHeight&&r.bottom>0)y=Math.max(y,innerHeight-r.top+10)}});b.style.bottom=y+'px'}}
  if(matchMedia('(max-width:560px)').matches){{addEventListener('scroll',lift,{{passive:true}});addEventListener('resize',lift);setTimeout(lift,600)}}
}})();
</script>
{END}'''

def files(target):
    if os.path.isdir(target):
        return [os.path.join(r, f) for r, _, fs in os.walk(target) for f in fs if f.endswith('.html')]
    return [target]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('cible'); ap.add_argument('--campagne', default='maquette'); ap.add_argument('--jours', type=int, default=6)
    ap.add_argument('--retirer', action='store_true')
    a = ap.parse_args()
    camp = re.sub(r'[^a-z0-9-]+', '-', a.campagne.lower()).strip('-') or 'maquette'
    end = datetime.date.today() + datetime.timedelta(days=a.jours)
    month = end.month
    off = '+02:00' if 4 <= month <= 9 or (month == 3 and end.day >= 25) or (month == 10 and end.day < 25) else '+01:00'  # heure de Paris approx.
    iso = f'{end.isoformat()}T23:59:00{off}'
    for f in files(a.cible):
        h = open(f, encoding='utf-8').read()
        h = re.sub(re.escape(START) + r'.*?' + re.escape(END) + r'\n?', '', h, flags=re.S)
        if not a.retirer:
            h = h.replace('</body>', snippet(camp, iso) + '\n</body>', 1) if '</body>' in h else h + snippet(camp, iso)
        open(f, 'w', encoding='utf-8').write(h)
        print(('retiré : ' if a.retirer else 'badge ajouté : ') + f)
    if not a.retirer:
        print(f'Expiration : {end.strftime("%d/%m/%Y")} à 23h59 (Paris) — campagne « {camp} »')

if __name__ == '__main__':
    main()
