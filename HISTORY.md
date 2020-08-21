## Historique des versions

### Branche feature/api-versioning

- Informations plus complètes dans le path "/" (environnement + versions API)
- API versionnée. Seule la version "1.0" pour le moment.
- Suppression de l'échange de métadonnées (doublon de l'utilisation de Matomo)
- Vocabulaire et méthodes conformes aux normes ICDC
  - `GET /romme_suggest` devient `GET /1.0/romes` (opération `rechercherROMEs`)
  - `POST /match` devient `GET /1.0/entreprises` (opération `rechercherEntreprises`)
  - **Attention** aux changement de signature des méthodes (voir le OpenAPI / Swagger)
- Ajout de la pseudo-globale de cycle de request `andi.webservice.library.g()` comme décrit dans
  [cet article](http://glenfant.github.io/flask-g-object-for-fastapi.html).
- Disponibilité de la version utilisée de l'API comme dans cet exemple :
```python
from andi.webservice.library import g

def some_function():
    api_version = g().api_version_info
    if api_version > (1, 5):
        x = do_new_stuff()
    else:
        x = do_old_stuff()
    return play_with(x)
``` 


### 1.7.0.dev4 - 16 aout 2020

- Support de la variable d'environnement SCRIPT_NAME nécessaire pour la publication Apache ->
  Unicorn -> Uvicorn -> Appli FastAPI. Et documentation associée.

### 1.7.0.dev3 - 10 aout 2020

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
