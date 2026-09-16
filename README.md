# WatchBid — enchères de montres de collection

Application web d'enchères en ligne dédiée aux montres de prestige, développée en **Flask**. Projet du cours de programmation web (Master 1 DCI, Université Paris Cité, 2025), à partir d'une première version réalisée en M1 SII à l'USTHB (2024).

## Fonctionnalités

- **Comptes utilisateurs** : inscription, connexion et déconnexion avec Flask-Login ; mots de passe hachés (PBKDF2-SHA256).
- **Catalogue** : recherche plein texte, filtres par catégorie et par marque, tris (enchères populaires, bientôt terminées, offre la plus haute ou la plus basse) et fiche détaillée de chaque montre (marque, catégorie, année, description, 3 photos).
- **Vente** : un utilisateur connecté met une montre aux enchères avec un prix de départ et des dates de début et de fin ; les photos sont téléversées.
- **Enchères** : placement d'offres sur une montre ; l'offre maximale courante est calculée en base.
- **Espace personnel** : profil, produits mis en vente (avec suppression), historique des offres soumises.

## Modèle de données

```
User (id, full_name, tel, email, password)
 ├─< Watch (id_watch, nom, marque, categorie, annee, prix, dateStart, dateEnd, desc, detail, img1..3)
 └─< Bid   (id_bid, id_product → Watch, id_buyer → User, offer)
```

## Lancer l'application

```bash
pip install -r requirements.txt
python main.py
```

Le site est servi sur http://localhost:5000. La base SQLite (`instance/ecom.db`) est créée automatiquement au premier lancement.

En dehors du développement local, définir une clé secrète :

```bash
export SECRET_KEY="une-valeur-longue-et-aleatoire"
```

## Stack

Python · Flask · Flask-SQLAlchemy (SQLite) · Flask-Login · Jinja2 · Bootstrap 5 · jQuery · Slick. L'interface est adaptée du template gratuit *Zay Shop* de [TemplateMo](https://templatemo.com).

## Licence

Code distribué sous [licence MIT](LICENSE). Le template d'interface *Zay Shop* (TemplateMo), Bootstrap, jQuery, Font Awesome et Slick restent soumis à leurs propres licences.

## Auteurs

**Amar Merabti**, Lynda Farah Hammouche et Abdelkader Souayah.
