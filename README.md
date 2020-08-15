<h1 align="center">
  andi-matching
</h1>

[ANDi](https://andi.beta.gouv.fr) est une service numérique en développement visant à faciliter
l'immersion professionnelle des personnes en situation de handicap. **andi-matching** est le serveur
backend motorisant cette application.

------------
[TOC]
------------

# Installation

## Dépendances

`andi-matching` nécessite Python 3.7 ou 3.8

> **📣 Attention**
> 
> Seul Python 3.7 est supporté sous Windows du fait d'un bug de `aiohttp` lorsque votre poste accède
> au Web à travers un proxy. [Lire ceci pour plus de
> détails](https://github.com/aio-libs/aiohttp/issues/4536).

## Modes opératoires

Obtenir le code source depuis le dépôt Git, puis, pour un environnement de "production" :

```bash
cd /le/repertoire/contenant/ce/document
pip install .
```

Pour un poste de développeur, vous installez en mode "éditable" (les modifications effectuées dans
`src/...` ne nécessitent pas de réinstallation, les outils de développement et de tests sont
également installés.) :

```bash
pip install -e .[dev]
```

# andi-matching

Outil "matching" entre profils PSH et DB Entreprises. En partant des critères de recherches
spécifiques à une PSH, l'outil permet de retrouver les entreprises qui y répondent tout en nuançant
les résultats, permettant de limiter certains biais de sélection (effet de primauté, ...)

Actuellement, le service mathing est se compose de l'**Outil Matching**, la librairie métier, et
l'**API Web** qui publie une interface REST de l'outil de matching.

## API Restful Matching

### Lancement

Le serveur d'API peut s'exécuter de deux façons :

- En ligne de commande avec la commande `andi-api`. Tapez `andi-api --help` pour afficher les
  options possibles d'utilisation.
- Par un serveur ASGI externe de production. L'application ASGI pré-initialisée et configurée est
  accessible par l'objet `app` du module Python `andi.webservice.asgi`.

  Par exemple, avec **uvicorn** : `uvicorn [options] andi.webservice.asgi:app`.

### Index de recherche ROME

Actuellement, le endpoint `/rome_suggest` nécessite l'utilisation d'un moteur d'indexation pour
fournir ses résultats, utilisant les services de l'outil
[Woosh](https://whoosh.readthedocs.io/en/latest/), une sorte d'ElasticSearch allégé et "serverless".

Les fichiers index sont des fichiers binaires compilés depuis des fichiers sources en CSV fournis
dans la distribution `andi-matching`. Cette compilation s'effectue automatiquement en cas d'absence
de ces fichiers d'index dans le répertoire par défaut `rome-index-suggest/` du répertoire courant
(cwd) lors du lancement de l'application `andi-api`. En cas d'absence de ce répertoire, le lancement
du serveur est **retardé d'environ une dizaine de secondes**, le temps de construire ce répertoire
et son contenu.

En conséquence, il est impératif de lancer la commande `andi-api` depuis un répertoire où
l'utilisateur propriétaire du processus exécutant l'application **dispose des droits d'écriture**.

> **NOTE**
>
> Le chemin de ce répertoire peut être personnalisé comme indiqué dans le paragraphe
> **Configuration** ci-après.


> **☝️ TODO**
>
> Une version future d'`andi-matching` construira ces fichier d'index "définitivement" lors de
> l'installation.

### Configuration

Dans les deux cas de figure, vous devez préalablement configurer l'application. Cette configuration
peut se faire de deux façons non exclusives:

* Les options simples et essentielles peuvent être fournies par des **variables d'environnement**.
* L'ensemble des options, incluant celles définies par les variables d'environnement peuvent être
  fournies par un **fichier de configuration**.

En fournissant les **variables d'environnement** suivantes :

**`AN4_PG_DSN`** (obligatoire)
> Le DSN de la base de données PostgreSQL à laquelle se connecter, conforme à la spécification de la
> section [Connection URIs](https://www.postgresql.org/docs/10/libpq-connect.html#LIBPQ-CONNSTRING)
> de la documentation PostgreSQL.
>
> Exemple : `AN4_PG_DSN=postgresql://dupont:secret@dbserver.domain.fr:5432/database_name`
>
> **/!\ Lisez la FAQ** à propos l'encodage des mots de passe incluant des caractères spéciaux.

**`AN4_UVICORN_HOST`**, **`AN4_UVICORN_PORT`**, **`AN4_UVICORN_LOG_LEVEL`** (facultatif)
> Les paramètres d'initialisation du serveur de développement **Uvicorn** intégré. Voir la
> [documentation Uvicorn](https://www.uvicorn.org/settings/) En cas d'absence de ces variables
> d'environnement, les valeurs par défaut respectives suivantes leur seront affectées: `localhost`,
> `5000` et `INFO`. De plus ces variables d'environnement ne seront prises en compte que lors du
> lancement du serveur de développement par la commande `andi-api`, et seront ignorées lors de
> l'utilisation d'un serveur ASGI externe.

**`AN4_ROME_SUGGEST_INDEX_DIR`** (facultatif en developpement mais vivement recommandé en production)

> Comme expliqué ci-avant, `andi-api` nécessite un index de recherche pour les suggestions de code
> ROME, index qui est construit de façon persistante dans un répertoire, créé pour l'occasion à un
> emplacement dans lequel l'utilisateur propriétaire du processus serveur dispose des droits
> d'écriture. Cette variable d'environnement permet de désigner un répertoire dans lequel cet index
> sera enregistré. Par défaut, ce répertoire sera `./rome-suggest-index/`.
>
> Exemple : `AN4_ROME_SUGGEST_INDEX_DIR=/var/run/an4-rome-suggest-index`.

**`AN4_LOG_FILE`** (facultatif)
> Si vous utilisez l'option de logging dans un fichier (le logging est effectué par défaut dans la
> console), ce fichier sera utilisé. Il faut bien entendu fournir un chemin absolu vers un fichier
> (existant ou non) dont le répertoire parent existe et autorise l'écriture à l'utilisateur
> exécutant l'application.
>
> Exemple : `AN4_LOG_FILE=/var/log/andi/andi.log`

**`AN4_CONFIG_FILE`** (facultatif)
> Comme décrit plus haut, l'ensemble des options peuvent être fournies à travers un fichier de
> configuration. Le cas échéant, vous devez fournir le chemin relatif ou absolu de ce fichier dans
> cette variable d'environnement.
>
> Exemple : `AN4_CONFIG_FILE=/home/moi/etc/andicustom.py`

**`AN4_NO_DB_CONNECTION`** (pour développeurs seulement)
> Si un développeur veut tester une fonctionnalité ne nécessitant pas de base de données PostgreSQL
> ou ne disposant pas d'une telle base de données, il est possible de placer cette variable
> d'environnement. Notez que le cas échéant, l'absence éventuelle de la variable d'environnement
> `AN4_PG_DSN` sera ignorée.
>
> Exemple : `AN4_NO_DB_CONNECTION=true`

**`AN4_RUN_CONNECTED_TESTS`** (pour développeurs seulement)
> Si votre poste dispose d'une connexion Internet et d'une connexion à une base de données réelle,
> vous pouvez exécuter les tests unitaires tirant parti de ces deux choses en exposant dette
> variable d'environnement avec la valeur `true`. Sans quoi les tests nécessitant une connexion
> Internet (exemple l'utilisation d'une API externe) et une base de données seront remplacés par des
> tests utilisant des mocks.
>
> Exemple en bash : `AN4_RUN_CONNECTED_TESTS=true pytest [ options ]`

**`HTTP_PROXY`**, **`HTTPS_PROXY`** et **`NO_PROXY`** (si nécessaire)
> `andi-api` nécessite l'accès à des ressources Restful externes sur le Web fournies par des
> services partenaires. Si l'accès à Internet nécessite la traversée d'un proxy HTTP(s), ces
> variables d'environnement doivent être fournies. Renseignez-vous auprès de votre support réseau
> pour ces variables d'environnement standard.
>
> Exemples : `HTTP_PROXY=http://mon.proxy.com:3218`, `HTTPS_PROXY=http://mon.proxy.com:3218`,
> `NO_PROXY=localhost,127.0.0.1,*.domaine-prive.fr`.

**`SSL_CERT_FILE`** (obligatoire en environnement serveur CDC)
> Les serveurs Linux installés pour le CDC sont installés avec un lot de certificats CA racine
> personnalisé installé dans un répertoire non standard. Comme pour toutes les autres applications
> qui nécessitent un accès HTTPs vers des ressources externes, il est nécessaire de placer dans
> cette variable le chemin absolu du fichier contenant ces certificats. Ce fichier a pour extension
> `.crt` ou `.pem` selon la sérialisation des certificats adoptée.
>
> Exemple : `SSL_CERT_FILE=/dn-serviceandi/ntiers/an4/ext/ssl/cacert.crt`

**`SCRIPT_NAME`** (obligatoire en production, inutile en développement)
> Les serveurs WSGI comme Gunicorn employé dans le chaîne de publication de `andi-matching` sont
> sensées tenir compte d'un certain nombre de [variables d'environnement définies
> ici](https://www.python.org/dev/peps/pep-3333/#environ-variables). Lorsqu'on souhaite publier
> derrière un proxy un service ailleurs qu'à la racine du site (exemple
> http://schtroumpf.csc.fr/andi/api), il faut placer le path dans la variable d'environnement
> `SCRIPT_NAME=/andi/api` (selon notre exemple) de sorte que la génération d'URLs par l'application
> soit conforme au path de base choisi. Un exemple est fourni en FAQ pour publier l'application avec une chaîne Apache(+ mod_proxy) -> Gunicorn -> Uvicorn -> application FastAPI.

**Autres variables d'environnement** : Si leur absence n'est à priori pas conséquente sur le
fonctionnement du service, vous pouvez noter que les logiciels sur lesquels il se base peuvent aussi
être paramètrés par des variables d'environnement:

- [Les variables d'environnement utilisées par
  Python](https://docs.python.org/3/using/cmdline.html#environment-variables)
- [Les variables d'environnement utilisées par Uvicorn](https://www.uvicorn.org/settings/)
- [Les variables d'environnement utilisées par le client standard
  PostgreSQL](https://www.postgresql.org/docs/11/libpq-envars.html)
- [Les variables d'environnement utilisées par le client Python
  PostgreSQL](https://magicstack.github.io/asyncpg/current/api/index.html)

Pour vous faciliter les choses, vous pouvez exposer ces variables d'environnement dans un fichier
**`.env`** figurant dans le répertoire depuis lequel le processus serveur est lancé, ou dans un de
ses répertoires parents. Reportez-vous à [cette
documentation](https://pypi.org/project/python-dotenv/) pour la syntaxe des fichiers `.env`.

Notez que les variables d'environnement préalablement existantes ne seront pas modifiées par
l'utilisation du fichier `.env`. Par exemple, il est inutile de redéfinir la variable `$HOME` dans
le fichier `.env`. Ça ne fonctionnera pas.

Le répertoire racine du dépôt contient un fichier `.env.example` qu'il vous suffira de copier dans
un fichier `.env` à un emplacement pertinent puis adapter à vos besoins.

L'autre façon complémentaire de personnaliser le fonctionnement de ce logiciel consiste à fournir un
**fichier de configuration personnalisé**. Cette façon de procéder permet en outre d'effectuer
certaines personnalisations hors de portée des simples variables d'environnement, comme le logging,
ou des options de pool de connexion PostgreSQL différentes.

La façon la plus simple de procéder consiste à :

- obtenir une **copie du fichier de configuration par défaut** dans un répertoire quelconque,

  ```console
  andi-api --dump-default-config > $HOME/etc/custom_andi_config.py  # Choix arbitraire
  ```

- modifier cette copie pour ne conserver et modifier que les options que vous voulez modifier, avec
  votre éditeur préféré,

  ```console
  $EDITOR $HOME/etc/custom_andi_config.py
  ```

- tester rapidement la syntaxe et ce fichier de configuration, vérifiant que la commande suivante ne
  provoque pas d'erreur,

  ```console
  python $HOME/etc/custom_andi_config.py
  ````

- inviter `andi-api` à utiliser ce fichier de configuration en exposant la variable d'environnement
  `AN4_CONFIG_FILE` contenant le chemin absolu d'accès à ce fichier de configuration. Ceci peut
  bien entendu se faire en modifiant le fichier `.env`. Vous pouvez également utiliser explicitement
  ce fichier de configuration  sans l'exposer `AN4_CONFIG_FILE`  en exécutant la commande
  `andi-api` avec l'option `-c` ou `--config-file`.

  ```console
  andi-api --config-file $HOME/etc/custom_andi_config.py
  ````

  Notez que dans ce dernier cas, l'éventuelle variable d'environnement `AN4_CONFIG_FILE` sera
  ignorée.

> **⚠️ Configuration en Python ! WTF ?**
>
> Oui, le fichier de configuration est en Python, et les responsables du déploiement de
> `andi-matching` peuvent avoir quelques inquiétudes légitimes. Voici de quoi les rassurer :
>
> - De nombreux frameworks utilisent cette possibilité (Flask, Django, ...)
> - Le niveau débutant Python est amplement suffisant pour comprendre ce fichier
> - Le modèle de configuration fourni par la commande `andi-api --dump-config` est amplement
>   commenté, les différentes options étant décrites en détail avec des liens de renvoi vers la
>   documentation s'il y a lieu.
> - Le fichier Python de configuration est exécuté dans un sandbox distinct de celui du logiciel
>   serveur (sorte de jail). Il ne peut y avoir de "live patch" accidentel sur l'application.
> - Seules les variables globales en MAJUSCULES sont exposées dans le namespace de configuration.
>   Les autres n'ont qu'une portée locale (variables intermédiaires)

Lancer le serveur avec soit la commande `andi-api` soit en utilisant l'infrastructure de déploiement
ASGI, à travers le fichier `main.asgi` à la racine de ce dépôt.


# Déploiement via Travis / Docker (/!\ obsolète et non maintenu)

Le déploiement de l'API Matching et de la librairie est détaillée dans le `DockerFile`. Celui-ci se
contente de définir les variables d'environnement requises, d'installer l'environnement Python, de
copier les fichiers nécessaires et de lancer l'API, qui sera fournie sur le port 9000 par défaut
(voir variables d'environnent du CI).

Le déploiement est assuré par Travis, et est détaillé dans le fichier `.travis.yml`.

# Socle technique

- Python 3.7+
- framework [FastAPI](https://github.com/tiangolo/fastapi) implémentant
  [OpenAPI](https://pydantic-docs.helpmanual.io/) et [JSON Schema](http://json-schema.org/),
  intégrant [Starlette](https://github.com/encode/starlette) (framework ASGI, support WebSocket,
  GraphQL, CORS, ...) et [pydantic](https://pydantic-docs.helpmanual.io/) (validation de données)
- documentation API auto-générée (via OpenAPi - ex-swagger)
- PostgreSQL (via asyncpg)
- Whoosh

## Cycles de développement

Les cycles de développement et de maintenance de ce logiciel seront effectués selon les règles du
workflow [Gitflow](https://www.atlassian.com/fr/git/tutorials/comparing-workflows/gitflow-workflow).

Quelques recommandations supplémentaires :

- Avant de clore une branche "feature/xxx":
  - Squashez les commits effectués sur la branche pour ne conserver que les plus significatifs
    (éviter de bruiter le log Git)
  - Vérifiez que les tests unitaires ne relèvent aucune erreur
- Après une fusion dans la branche "develop":
  - Vérifiez que les tests unitaires ne relèvent aucune erreur
  - Vérifiez que la version dans "VERSION.txt" soit la prochaine version planifiée et se termine par
    ".dev1". Exemple : "2.6.2.dev1". Corrigez et commitez directement dans la branche "develop" le
    cas échéant.
- Lors d'une nouvelle version (dans la branche "master")
  - Corriger la version figurant dans "VERSION.txt" si ce n'est déjà fait.
  - Ajouter dans la branche "master" un tag Git ayant la même valeur que le contenu que celui de
    "VERSION.txt"

## Tests et validation


Ils sont lancés comme suit depuis un prompt à la racine du projet :
```bash
# Tests unitaires
pytest

# Tests unitaires avec couverture
pytest --cov=andi.webservice

# Qualimétrie flake8
flake8 src

# Qualimétrie pylint
pylint --rcfile=setup.cfg src
```

### Sous **tox**

Tox est le nouvel outil recommandé par python pour tester (et déployer) les composants Python. Il
est utilisé ici pour tester l'outil sous plusieurs versions Python dans la CI.

```bash
# Pour lancer tox
tox

# Pour spécifier une version supportée par le composant:
tox -e [ py37 | py38 ]

# Attention, sous Windows, utilisez uniquement
tox -e py37
```

# FAQ

Foire Aux Questions diverses auxquelles les réponses sont fournies au fil de l'eau, sans ordre autre
que chronologique.

## Comment produire un fichier Swagger de spécification de l'API ?

Le framework FastAPI sur lequel l'application se base fournit les spécifications d'API au format
OpenAPI 3.0.x à la date de rédaction de cette note. Les opérateurs de production de la CDC ont
besoin de cette spécification à l'ancien format OpenAPI 2.0 (alias Swagger).

L'outil de conversion [api-spec-converter](https://www.npmjs.com/package/api-spec-converter) permet ceci.

Exemple d'utilisation :

- lancez `andi-api` sur votre poste de développement. Nous supposons qu'il écoute le port 5000.
  Adaptez selon le cas.
- Lancez la commande (en une seule ligne) :
```bash
api-spec-converter --from openapi_3 --to swagger_2 http://localhost:5000/openapi.json > andi-swagger.json
```

## Comment faire accepter un mot de passe du DSN PostgreSQL avec des caractères spéciaux ?

Rappel : le mot de passe de la base PostgreSQL peut être passé dans le DSN à travers la variable
d'environnement `AN4_PG_DSN` comme vu plus haut dans les considérations relatives à la
configuration. Il est possible que ce mot de passe inclue des caractères structurant dans une URL,
comme le `#` ou le `%`.

Par exemple : `AN4_PG_DSN=postgresql://dupont:xUty#5%ba@serveur.tld:4321/database`.

Si vous laissez la variable d'environnement en l'état, le démarrage "plantera", la dernière ligne du
(long) message d'erreur indiquera :

```
.../site-packages/asyncpg/connect_utils.py in _parse_hostlist(hostlist, port, unquote)

ValueError: invalid literal for int() with base 10: 'xUty'
```

Eh oui ! La présence du `#` dans le mot de passe a faussé le parsing du DSN, comme le ferait le `%`
si on inversait les deux caractères. Dans ce cas, il faut "URL encoder" le mot de passe, comme [il
est expliqué ici](https://fr.wikipedia.org/wiki/Percent-encoding).

Un outil d'encodage [tel que celui-ci](https://www.urlencoder.org/) permet donc d'encoder le mot de
passe `xUty#5%ba` en `xUty%235%25ba` et obtenir le DSN à fournir, c'est-à-dire :

```
AN4_PG_DSN=postgresql://dupont:xUty%235%25ba@serveur.tld:4321/database
```

## Sources de données

Vous remarquez dans l'arbre source de données les fichiers :

- `src/andi/webservice/referentiels/metiers_onisep.csv`
- `src/andi/webservice/referentiels/ogr_lbb.csv`
- `src/andi/webservice/referentiels/rome_lbb.csv`
- `src/andi/webservice/data_files/andi_rome2naf.csv`

Les trois premiers dans le répertoire `src/andi/webservice/referentiels/` permettent de constituer
l'index Whoosh de sélection de code ROME en fonction d'un extrait de nom de métier, index stocké
selon la variable d'environnement `AN4_ROME_SUGGEST_INDEX_DIR` comme expliqué plus haut dans cette
documentation.

Le dernier permet de trouver les codes NAF correspondant à un code ROME

Ces fichiers sont issus du projet "La bonne boite" et sont accessibles à partir de l'adresse :

https://github.com/StartupsPoleEmploi/labonneboite/tree/master/ROME_NAF/referentiels

## Comment publier andi-matching...

Avec la chaîne Apache -> Gunicorn -> Uvicorn -> Application FastAPI

Lorsqu'on publie une application ASGI (comme FastAPI) derrière une telle chaîne, et que
l'application n'est pas publiée à la racine du site (http://schtroumpf.csc.fr/) mais dans un path
dédié (par exemple http://schtroumpf.cdc.fr/andi/api/), il est nécessaire de faire savoir aux
applications Gunicorn, Uvicorn et FastAPI (andi-matching en l'occurrence) cette particularité en
plaçant dans la variable d'environnement `SCRIPT_NAME` sous peine de voir la génération d'UrLs
faussée.

Hélas, le worker standard d'Uvicorn pour Gunicorn ne respecte ni ne transmet cette variable
d'environnement. C'est la raison pour laquelle andi-matching fournit un worker ASGI qui tient compte
de cette particularité de publication, dans l'objet `andi.webservice.workers.UvicornWorker` qu'il
faudra utiliser en lieu et place de `uvicorn.workers.UvicornWorker` dans la commande de lancement du
serveur de l'application.

Ce qui suit est un exemple complet permettant la publication d'andi-matching à partir de l'URL
`http://schtroumpf.cdc.fr/andi/api`.

**Configuration Apache**

Nous supposons que vous avez activé les extensions `mod_proxy` et `mod_proxy_http`.

```
# ...
LoadModule proxy_module lib/apache2/modules/mod_proxy.so
LoadModule proxy_http_module lib/apache2/modules/mod_proxy_http.so
# ...
```

Il est supposé que vous utilisez un VirtualHost. Corrigez le cas échéant.

```
<VirtualHost *:80>
    ServerName schtroumpt.cdc.fr
    # ... autres options ad lib ...
    ProxyRequests Off
    # Ici nous supposons que Gunicorn écoute sur 127.0.0.1:8000
    ProxyPass        "/andi/api"  "http://127.0.0.1:8000"
    ProxyPassReverse "/andi/api"  "http://127.0.0.1:8000"
    <Location "/andi/api">
        Order allow,deny
        Allow from all
    </Location>
    # ... autres options ad lib ...
</VirtualHost>
```

Une fois les différentes options de configurations pour `andi-matching` mises en place, vous pouvez
lancer le serveur Gunicorn avec la commande suivante :

```
SCRIPT_NAME=/andi/api gunicorn -k andi.webservice.workers.UvicornWorker [autres options] \
  andi.webservice.asgi:app
```

Vous pouvez naviguer à `http://schtroumpf.cdc.fr/andi/api/docs` pour vérifier les URLs générées.
