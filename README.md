<h1 align="center">
  andi-matching
</h1>

[ANDi](https://andi.beta.gouv.fr) est une service numérique en développement visant à faciliter
l'immersion professionnelle des personnes en situation de handicap. **andi-matching** est le serveur
backend motorisant cette application.

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

**`AN4_UVICORN_HOST`**, **`AN4_UVICORN_PORT`**, **`AN4_UVICORN_LOG_LEVEL`** (facultatif)
> Les paramètres d'initialisation du serveur de développement **Uvicorn** intégré. Voir la
> [documentation Uvicorn](https://www.uvicorn.org/settings/) En cas d'absence de ces variables
> d'environnement, les valeurs par défaut respectives suivantes leur seront affectées: `localhost`,
> `5000` et `INFO`. De plus ces variables d'environnement ne seront prises en compte que lors du
> lancement du serveur de développement par la commande `andi-api`, et seront ignorées lors de
> l'utilisation d'un serveur ASGI externe.

**`HTTP_PROXY`**, **`HTTPS_PROXY`** et **`NO_PROXY`** (si nécessaire)
> `andi-api` nécessite l'accès à des ressources Restful externes sur le Web fournies par des
> services partenaires. Si l'accès à Internet nécessite la traversée d'un proxy HTTP(s), ces
> variables d'environnement doivent être fournies. Renseignez-vous auprès de votre support réseau
> pour ces variables d'environnement standard.
>
> Exemples : `HTTP_PROXY=http://mon.proxy.com:3218`, `HTTPS_PROXY=http://mon.proxy.com:3218`,
> `NO_PROXY=localhost,127.0.0.1,*.domaine-prive.fr`.

**`AN4_ROME_SUGGEST_INDEX_DIR`** (facultatif)

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

## Outil CLI matching

> **⚠️ Attention**
>
> Cette partie de l'application **n'est plus maintenue !** La documentation relative à la commande
> `andi-matching` n'est fournie qu'à titre indicatif. **Aucun** constat de dysfonctionnement ou
> demande d'évolution ne seront pris en compte.

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

# Déploiement via Travis / Docker (obsolète et non maintenu)

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

Le lancement des tests et outils de validation (flake8, pylint, pytest) sont définis dans le
`MakeFile`. Pour en disposer, il faut que vous ayez préalablement installé le package en mode "pour
développeur".

> **Windows**
>
> Les commandes évoquées ci-dessous nécessitent un poste sous Linux ou MacOS, Windows n'ayant ni
> `make` ni l'aptitude native d'exécuter les différentes commandes du `Makefile`. Il faudra aux
> mainteneurs travaillant sous Windows lire le fichier `Makefile` et adapter les commandes à leur
> environnement.
>
> Si ces commandes s'avèrent nécessaire, le remplacement de `make` par `invoke` sera envisagé.

Ils sont lancés comme suit:
```bash
# Tous (utilisé par le CLI):
make tests

# Uniquement l'un d'eux
make [flake8 | pylint | unittests]

```
Note: la commande `tests` fait passer `pylint` pour autant que le score dépasse 9.5 (cf. `MakeFile`
=> `pylint-fail-under`)

### Sous **tox**

Tox est le nouvel outil recommandé par python pour tester (et déployer) les composants Python. Il
est utilisé ici pour tester l'outil sous plusieurs versions Python dans le CI de Travis.

```bash
# Pour lancer tox
tox

# Pour spécifier une version supportée par le composant:
tox -e [ py37 | py38 ]
```

### Travis

> **Note**
>
> L'utilisation de Travis étant liée à l'hébergement du dépôt Git par **Github**, bientôt abandonné,
> cette partie ne sera pas maintenue et tout aucun dysfonctionnement ou demande d'évolution de
> l'utilisation de Travis ne sera pris en compte.
> 

Le fichier `.travis.yml` détaille les procédures de test et de validation automatisées, ainsi que le
_build_ et le déploiement.
