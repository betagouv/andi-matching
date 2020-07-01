[![Build Status](https://travis-ci.org/betagouv/andi-matching.svg?branch=master)](https://travis-ci.org/betagouv/andi-matching)
[![Python 3.7](https://img.shields.io/badge/python-3.7-blue.svg)](https://www.python.org/downloads/release/python-370/)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-no-red.svg)](https://GitHub.com/betagouv/andi-docker/graphs/commit-activity)
[![Generic badge](https://img.shields.io/badge/ANDi-toujours-green.svg)](https://shields.io/)
<p align="center">
  <a href="https://andi.beta.gouv.fr">
    <img alt="Début description. Marianne. Fin description." src="https://upload.wikimedia.org/wikipedia/fr/3/38/Logo_de_la_R%C3%A9publique_fran%C3%A7aise_%281999%29.svg" width="90" />
  </a>
</p>
<h1 align="center">
  andi.beta.gouv.fr
</h1>

[ANDi](https://andi.beta.gouv.fr) est une service numérique en développement visant à faciliter
l'immersion professionnelle des personnes en situation de handicap.

# Installation

## Dépendances

`andi-matching` nécessite Python 3.7 ou 3.8

**/!\ Attention** : Seul Python 3.7 est supporté sous Windows du fait d'un bug de `aiohttp` lorsque
votre poste accède au Web à travers un proxy. [Lire ceci pour plus de détails](https://github.com/aio-libs/aiohttp/issues/4536).

## Modes opératoires

Obtenir le code source depuis le dépôt Git, puis, pour un environnement de "production" :

```bash
pip install .
```

Pour un poste de développeur :
```bash
pip install -e .[dev]
```


# andi-matching

Outil "matching" entre profils PSH et DB Entreprises. En partant des critères de recherches
spécifiques à une PSH, l'outil permet de retrouver les entreprises qui y répondent tout en nuancant
les résultats, permettant de limiter certains biais de sélection (effet de primauté, ...)

Actuellement, le service mathing est se compose de l'**Outil Matching**, la librairie métier, et
l'**API Web** qui publie une interface REST de l'outil de matching.

## Utilisation et déploiement

### Outil CLI matching

L'application s'exécutant dans une console shell est invoquée par la commande `andi-matching`.

```bash
andi-matching --help

Usage: andi-matching [OPTIONS] COMMAND [ARGS]...

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

L'interface CLI accepte des paramètres directement saisis en ligne de commande, un lien vers un
Google Sheet contenant les variables nécessaires, ou un fichier CSV.

Exemples de commande:
```bash
andi-matching --lat '49.0465' --lon '2.0655' --max-distance 10 --rome K2112 \
              --config_file config.yaml --debug --pme
andi-matching --config_file config.yaml run-drive --profile [PROFIL]
```

TODO: fournir plus de détails sur ce que font les commandes.
TODO : fournir la définition des colonnes des fichiers CSV et Google sheet


### API Matching

Les variables d'environnement suivantes doivent être définies:

```bash
> cat env.sh 
export PG_DSN=postgres://[POSTGRES_DSN]
export LOG_LEVEL=[LOG_LEVEL]

# Si Internet est derrière un proxy
export HTTP_PROXY=http://mon.proxy.tld
export HTTPS_PROXY=http://mon.proxy.tld

# Pour les appliquer:
> . env.sh
```

TODO : passer par un fichier ".env" classique

Lancer le serveur avec soit la commande `andi-api` soit en utilisant l'infrastructure de déploiement
ASGI, à travers le fichier `main.asgi` à la racine de ce dépôt.

### Déploiement via Travis / Docker (obsolète et non maintenu)

Le déploiement de l'API Matching et de la librairie est détaillée dans le `DockerFile`. Celui-ci se
contente de définir les variables d'environnement requises, d'installer l'environnement Python, de
copier les fichiers nécesaires et de lancer l'API, qui sera fournie sur le port 9000 par défaut
(voir variables d'environnent du CI).

Le déploiement est assuré par Travis, et est détaillé dans le fichier `.travis.yml`.

## Socle technique

### Outil Matching

- Requête SQL utilisant la méthode [RFM](https://en.wikipedia.org/wiki/RFM_(customer_value\)) qui
  génère des ensembles de résultat, en fonction du score différencié sur les critères employés
- Python 3.7+
- Docker

### API Matching

- Python 3.7+
- framework [FastAPI](https://github.com/tiangolo/fastapi) implémentant
  [OpenAPI](https://pydantic-docs.helpmanual.io/) et [JSON Schema](http://json-schema.org/),
  intégrant [Starlette](https://github.com/encode/starlette) (framework ASGI, support WebSocket,
  GraphQL, CORS, ...) et [pydantic](https://pydantic-docs.helpmanual.io/) (validation de données)
- Docker
- documentation API auto-générée (via OpenAPi - ex-swagger)

## Tests et validation

Le lancement des tests et outils de validation (flake8, pylint, pytest) sont définis dans le
`MakeFile`.

Ils sont lancés comme suit:
```bash
# Tous (utilisé par le CLI):
make tests

# Uniquement l'un d'eux
make [flake8 | pylint | unittests]

```
Note: la commande `tests` fait passer `pylint` pour autant que le score dépasse 9.5 (cf. `MakeFile`
=> `pylint-fail-under`)

TODO : utiliser "invoke" au lieu de "make" pour permettre l'exécution sous Windows.

### Sous **tox**

Tox est le nouvel outil recommandé par python pour tester (et déployer) les composants Python. Il
est utilisé ici pour tester l'outil sous plusieurs versions Python dans le CI de Travis.

```bash
# Pour lancer tox
tox

# Pour spécifier une version supportée par le composant:
tox -e [py36 | py37 | py38]
```

### Travis

Le fichier `.travis.yml` détaille les procédures de test et de validation automatisées, ainsi que le
_build_ et le déploiement.
