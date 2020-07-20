## Historique des versions

### Futur - à planifier

- Suppression de la commande `andi-matching` et de ses dépendances.
- Placer le SQL et les méthodes / fonctions y accédant dans le logiciel `an4.andidb`.

### 1.7.0.dev1

- La recherche de codes ROME / métiers est asynchrone (performances ++)
- Suppression des tests Behave, remplacement par des pytests
- Amélioration autodoc OpenAPI
- Suppression des routes /entreprise et /track
- Création de l'index persistant de recherche ROM dans un répertoire personnalisable.
- Préfixage des variables d'environnement spécifiques avec "AN4_"
- Fichier .env modèle ".env.example"
- Configurable par fichier de configuration
- Support des fichiers .env (via python-dotenv)
- Refactoring selon les recommandations FastAPI
- Ajout de tests unitaires

### 1.6.0 - 29 juin 2020

- Mise en conformité avec les règles de déploiement des applications Python / ASGI de la CDC
- Abandon du support de Python 3.6
