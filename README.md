[![Build Status](https://travis-ci.org/betagouv/andi-matching.svg?branch=master)](https://travis-ci.org/betagouv/andi-matching)
[![Python 3.7](https://img.shields.io/badge/python-3.7-blue.svg)](https://www.python.org/downloads/release/python-370/)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://GitHub.com/betagouv/andi-matching/graphs/commit-activity)
[![Generic badge](https://img.shields.io/badge/ANDi-oui-green.svg)](https://shields.io/)
<p align="center">
  <a href="https://andi.beta.gouv.fr">
    <img alt="Début description. Marianne. Fin description." src="https://upload.wikimedia.org/wikipedia/fr/3/38/Logo_de_la_R%C3%A9publique_fran%C3%A7aise_%281999%29.svg" width="90" />
  </a>
</p>
<h1 align="center">
  andi.beta.gouv.fr
</h1>

[ANDi](https://andi.beta.gouv.fr) est une service numérique en développement visant à faciliter l'immersion professionnelle des personnes en situation de handicap.

# 🎚andi-matching
Outil "matching" entre profils PSH et DB Entreprises. En partant des critères de recherches spécifiques à une PSH, l'outil permet de retrouver les entreprises qui y répondent tout en nuancant les résultats, permettant de limiter certains biais de sélection (effet de primauté, ...)

Actuellement, le service mathing est se compose de l'**Outil Matching**, la librairie métier, et l'**API Web** qui publie une interface REST de l'outil de matching.

## Utilisation et déploiement
### Outil matching
Après installation par `pipenv` de l'environnemnt nécessaire (`pipenv install` à la racine du projet), l'outil de matching offre une interface en ligne de commande:
`export PYTHONPATH=./:$PYTHONPATH && matching/match.py`
```bash

Usage: match.py [OPTIONS] COMMAND [ARGS]...

Options:
  --config_file TEXT
  --debug
  --limit TEXT        Limit output rows (testing only)
  --help              Show this message and exit.

Commands:
  list-drive
  run-csv
  run-drive
```
L'interface CLI accepte des paramètres directement saisis en ligne de commande, un lien vers un Google Sheet contenant les variables nécessaires, ou un fichier CSV.

Exemples de commande:
```bash
./match.py --lat '49.0465' --lon '2.0655' --max-distance 10 --rome K2112  --config_file config.yaml --debug --pme
./match.py --config_file config.yaml run-drive --profile [PROFIL]
```

### API Matching
Les variables d'environnement suivantes doivent être définies:
```bash
> cat env.sh 
export PG_DSN=postgres://[POSTGRES_DSN]
export LOG_LEVEL=[LOG_LEVEL]

# Pour les appliquer:
> . env.sh
```

Pour lancer l'API matching en local (après un `pipenv install`)
```
# en _debug_
make serve-dev
# sinon
make serve
```

### Déploiement
Le déploiement de l'API Matching et de la librairie est détaillée dans le `DockerFile`.
Celui-ci se contente de définir les variables d'environnement requises, d'installer l'environnement Python figée dans le `Pipfile.lock`, de copier les fichiers nécesaires et de lancer l'API, qui sera fournie sur le port 9000 par défaut (voir variables d'environnent du CI).

Le déploiement est assuré par Travis, et est détaillé dans le fichier `.travis.yml`.


## Socle technique

### Outil Matching
- Requête SQL utilisant le méthode [RFM](https://en.wikipedia.org/wiki/RFM_(customer_value\)) qui génère des ensembles de résultat, en fonction du score différencié sur les critères employés
- Python 3.7+
- Pipenv / docker

### API Matching
- Python 3.7+
- framework [FastAPI](https://github.com/tiangolo/fastapi) implémentant [OpenAPI](https://pydantic-docs.helpmanual.io/) et [JSON Schema](http://json-schema.org/), intégrant [Starlette](https://github.com/encode/starlette) (framework ASGI, support WebSocket, GraphQL, CORS, ...) et [pydantic](https://pydantic-docs.helpmanual.io/) (validation de données)
- Pipenv / docker
- documentation API auto-générée (via OpenAPi - ex-swagger)

## Tests et validation
### Sous **pipenv**
Le lancement des tests et outils de validation (flake8, pylint, pytest) sont définis dans le `MakeFile`.

Ils sont lancés comme suit:
```bash
# Tous (utilisé par le CLI):
make tests

# Uniquement l'un d'eux
make [flake8 | pylint | unittests]

```
Note: la commande `tests` fait passer `pylint` pour autant que le score dépasse 9.5 (cf. `MakeFile` => `pylint-fail-under`)

### Sous **tox**
Tox est le nouvel outil recommandé par python pour tester (et déployer) les composants Python.
Il est utilisé ici pour tester l'outil sous plusieurs versions Python dans le CI de Travis.
```bash
# Pour lancer tox
tox

# Pour spécifier une version supportée par le composant:
tox -e [py36 | py37]
```

### Travis
Le fichier `.travis.yml` détaille les procédures de test et de validation automatisées, ainsi que le _build_ et le déploiement.


## Notes diverses
### Python, pipenv, PEP 582
Le composant matching utilise `pipenv` pour gérer les environnements virtuels de développement et de déploiement. Les outils tels que `pipenv` et `poetry` visent à mettre en place des flux de travail _souhaitables_, inspirés des meilleures pratiques et approches d'autres environnements, avec les moyens qu'offre Python.

Dans l'état actuel des chôses, cela signifie combiner _virtualenv_ et _pip_ pour obtenir des environnements définis, stables et reproductibles. Prochainement, la même fonctionnalité pourra être offerta par la proposition PEP 582 - _Python local packages directory_, toujours en développement.
