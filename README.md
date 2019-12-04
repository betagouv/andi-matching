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


## Notes diverses
### Python, pipenv, PEP 582
Le composant matching utilise `pipenv` pour gérer les environnements virtuels de développement et de déploiement. Les outils tels que `pipenv` et `poetry` visent à mettre en place des flux de travail _souhaitables_, inspirés des meilleures pratiques et approches d'autres environnements, avec les moyens qu'offre Python.

Dans l'état actuel des chôses, cela signifie combiner _virtualenv_ et _pip_ pour obtenir des environnements définis, stables et reproductibles. Prochainement, la même fonctionnalité pourra être offerta par la proposition PEP 582 - _Python local packages directory_, toujours en développement.
