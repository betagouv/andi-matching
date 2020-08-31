# Futur - à planifier

- Placer le SQL et les méthodes / fonctions y accédant dans le logiciel `an4.andidb`.
- Renommer les endpoints et méthodes HTTP conformément à la norme CDC.

## Mise en conformité normes CDC des APIs

- versionner l'API, ce qui n'est pas fait, pour exposer http://le-serveur.cdc.fr/v1/endpoint" (...)
  et donc réorganiser le code pour permettre des "smooth upgrade" et des alias plus faciles.

- le nommage n'est pas conforme, donc je propose, en conformité avec les diapos 22 et 23 :
    - (futur) rechercherROMEs : GET /1.0/romes (actuellement GET /rome_suggest)
    - (futur) rechercherEntreprises : GET /1.0/entreprises (actuellement POST /match)

Par contre, vu la complexité des paramètres de recherche d'une entreprise (voir
http://serviceandi-an4-in.cloud.cdc.fr/docs#/public/matching_match_post), il me semble exclu de
passer ces paramètres dans les paramètres de l'URL. Si FastAPI permet maintenant de prendre en
charge des requêtes http GET avec un payload JSON, ceci fait-il partie des aptitudes Angular ?

Dans tous les cas de figure, ceci entrainera - forcément - une révision adéquate de l'appli front
qui dans l'état actuel n'est bien évidemment pas compatible avec cette modification.

Je propose en outre de laisser tomber les métadonnées échangées dans tous les endpoints, à savoir le
bloc :

    "_v": 1, (fixe)
    "_timestamp": "2020-07-24 08:16:46.389075+00:00", (exemple)
    "_query_id": "d2f95067-87f7-4197-8733-f560978162ee", (exemple)
    "_session_id": "f7783b52-6a41-43c9-996a-1ea23d85a8c2", (exemple)

Le "_v" (version d'API) se trouvant dans l'URL dorénavant - source potentielle d'ambigïté / conflit
-, les autres infos ne sont pas exploitées ni enregistrées (rappel: le tracking interne est
abandonné).

## Table ROME -> NAF

- Quelle est son origine ? (OpenData ?)
- Y a-t-il une API qui fournit la même chose ?
- Pourquoi n'est-elle pas dans la base de données ?
- Seules les colonnes "rome", "naf", et "score" nous intéressent. Les autres ne servent que de
  "commentaires".
- La lecture d'un .csv à la volée n'est pas performante.

## Réduire la base de données (table "entreprises")

Il est possible d'obtenir nombre de données provenant actuellement de la table "entreprises" en les
récupérant par une API de l'INSEE, connaissant le SIRET des entreprises retenues par la requête
"/match".

L'API en question :
https://api.insee.fr/catalogue/site/themes/wso2/subthemes/insee/pages/item-info.jag?name=Sirene&version=V3&provider=insee#tab3
, plus particulièrement le endpoint "/siret/{siret}"

La définition des données fournies par l'API : https://www.sirene.fr/sirene/public/static/liste-variables

Avantages:

- Base de données plus compacte, donc plus rapide à construire, dupliquer, ...
- Disponibilité de données à jour (INSEE)

Inconvénients:

- Performances en retrait, quoiqu'il soit possible d'exécuter en simultanéïté les requêtes à l'API
  INSEE. -> Évaluer les performances sur un prototype
- Nécessite un token d'API - donc une inscription
- Risques liés à la non disponibilité de l'API (maintenance, ...)
- Risques liés aux droits d'utilisation
  https://api.insee.fr/catalogue/site/themes/wso2/subthemes/insee/pages/item-info.jag?name=Sirene&version=V3&provider=insee#tab3

Travaux d'évaluation :

- Enumérer les colonnes de la table "entreprises" pouvant être ainsi supprimées
- Un prototype pour valider le concept et les performances

