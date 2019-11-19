<p align="center">
  <a href="https://andi.beta.gouv.fr">
    <img alt="Début description. Marianne. Fin description." src="https://upload.wikimedia.org/wikipedia/fr/3/38/Logo_de_la_R%C3%A9publique_fran%C3%A7aise_%281999%29.svg" width="90" />
  </a>
</p>
<h1 align="center">
  andi.beta.gouv.fr
</h1>

[ANDi](https://andi.beta.gouv.fr) est une service numérique en développement visant à faciliter l'immersion professionnelle des personnes en situation de handicap.

# andi-matching
Outil "matching" entre profils PSH et DB Entreprises. En partant des critères de recherches spécifiques à une PSH, l'outil permet de retrouver les entreprises qui y répondent tout en nuancant les résultats, permettant de limiter certains biais de sélection (effet de primauté, ...)

## Socle technique

- Requête SQL utilisant le méthode [RFM](https://en.wikipedia.org/wiki/RFM_(customer_value\)) qui génère des ensembles de résultat, en fonction du score différencié sur les critères employés
- Python 3.7+
- Pipenv / docker


## Service web
API permettant l'interrogation du service via REST (GraphQL envisagé)
### Socle technique
- Python 3.7+
- framework [FastAPI](https://github.com/tiangolo/fastapi) implémentant [OpenAPI](https://pydantic-docs.helpmanual.io/) et [JSON Schema](http://json-schema.org/), intégrant [Starlette](https://github.com/encode/starlette) (framework ASGI, support WebSocket, GraphQL, CORS, ...) et [pydantic](https://pydantic-docs.helpmanual.io/) (validation de données)
- documentation API auto-générée (via OpenAPi - ex-swagger)

