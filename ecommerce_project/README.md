# 🛒 Application E-commerce (Django) — Côté Vendeur & Côté Client

Application web e-commerce complète avec deux types de comptes :
- **Client** : parcourt le catalogue, gère son panier, passe commande, suit l'état de ses commandes.
- **Vendeur** : gère sa boutique, publie/modifie/supprime ses produits, consulte les commandes reçues et met à jour leur statut.

## 🏗️ Structure du projet

```
ecommerce_project/
├── ecommerce_project/   # Config (settings, urls)
├── accounts/            # Utilisateur personnalisé (rôle Client/Vendeur), auth, dashboards
├── products/             # Catalogue, produits, catégories
├── cart/                 # Panier
├── orders/               # Commandes, checkout, suivi de statut
├── templates/            # Template de base (base.html)
├── static/                # CSS
└── manage.py
```

## ⚙️ Installation

```bash
python3 -m venv venv
source venv/bin/activate        # Windows : venv\Scripts\activate

pip install -r requirements.txt

python manage.py migrate
python manage.py createsuperuser   # pour accéder à /admin/
python manage.py runserver
```

Puis ouvrez **http://127.0.0.1:8000/**

## 🔑 Fonctionnalités principales (livrées)

### Authentification (priorité #1)
- Choix du type de compte à l'inscription : Client ou Vendeur (`/comptes/`)
- Modèle `User` personnalisé avec champ `role` (CLIENT / VENDEUR)
- Un compte Vendeur crée automatiquement un profil boutique (`VendorProfile`)
- Connexion / déconnexion / gestion de profil
- Décorateurs `@client_required` et `@vendeur_required` pour protéger les vues selon le rôle
- Redirection automatique vers le bon tableau de bord après connexion

### Côté Vendeur
- Tableau de bord dédié
- CRUD complet sur ses produits (ajout, modification, suppression)
- Liste des commandes reçues (uniquement les commandes contenant ses produits)
- Mise à jour du statut de chaque commande (En attente → Confirmée → Expédiée → Livrée / Annulée)

### Côté Client
- Tableau de bord dédié
- Catalogue public avec recherche et filtre par catégorie
- Panier (ajout, modification de quantité, suppression)
- Checkout → création de la commande + décrémentation du stock
- Historique des commandes avec suivi du statut en temps réel

## 🧩 Prochaines étapes suggérées
- Intégration d'un moyen de paiement (Stripe, CMI, etc.)
- Système de notation/avis produits
- Notifications email lors des changements de statut
- Upload de plusieurs images par produit
- Tableau de bord vendeur avec statistiques de ventes

## 🌍 Notes
- Interface entièrement en français
- Devise utilisée : DH (Dirham marocain) — modifiable dans les templates
- `DEBUG = True` par défaut : à désactiver avant toute mise en production, avec configuration de `ALLOWED_HOSTS`, `SECRET_KEY` en variable d'environnement, et base de données de production (PostgreSQL recommandé).
