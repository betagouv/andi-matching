# Futur - à planifier

- Suppression de la commande `andi-matching` et de ses dépendances.
- Placer le SQL et les méthodes / fonctions y accédant dans le logiciel `an4.andidb`.
- Renommer les endpoints et méthodes HTTP conformément à la norme CDC.

## Mise en conformité normes CDC

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
