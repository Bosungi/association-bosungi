# Site de l'Association Bosungi

- Source : `template.html` + `sections.html` + `site.css` + `couleur-soleil.css`, assemblés par `build_site.py` (`THEME=soleil python3 build_site.py` → dossier `site-soleil/`).
- **Nos actions** : une action = un fichier `content/actions/AAAA-MM-nom.md`. La page `actions.html` (journal) et une page `action-<nom>.html` par action sont générées automatiquement. Les 3 dernières apparaissent sur l'accueil.
- **Espace d'Annie** : `/admin/` (raccourcis `/ecrire`, `/publier`, `/espace`). Elle publie, modifie et supprime ses actions avec un mot de passe ; l'espace écrit dans `content/actions/` et `img/uploads/` via l'API GitHub, puis GitHub Actions reconstruit et republie le site (~2 min).
- Le mot de passe déchiffre la clé d'accès stockée chiffrée dans `admin/coffre.txt` (AES-GCM + PBKDF2, voir le skill `plateforme_blog`). À créer avec une clé limitée à CE dépôt uniquement.
- Badge Toudoum : actif tant que la variable de dépôt `BADGE` ≠ `0` (à passer à 0 au paiement du solde).
