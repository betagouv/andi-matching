## Historique des versions

### 1.7.0.dev3

- pylint : 10/10
- options de pylint et tox dans setup.cfg
- andi.matching supprimé. Ressources nécessaires à andi.webservice déménagées dans ce dernier.
- Suppression de la commande `andi-matching` et de ses dépendances.
- Nouvelles meta informations dans la route /
- Possibilité d'exécuter ou non les tests avec connexions
- Plus de tests, mocking des API externes
- Suppression des ressources inutilisées (fonctions, ...)
- Suppression du tracking

### 1.7.0.dev2 - 23 juillet 2020

- Suppression de l'enregistrement de l'exécution de /match dans la table de tracking
- La recherche de codes ROME / métiers est asynchrone (performances ++)
- Suppression des tests Behave, remplacement par des pytests
- Amélioration autodoc OpenAPI

### 1.7.0.dev1 - 19 juillet 2020

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
