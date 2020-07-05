"""
Traitement des critères du matching.

Chaque fonction de traitement retourne l'accumulateur mis à jour.

Exemple de contenu de l'accumulateur (paramètres de la librarie matching):
```
{
    'max_distance': 6,
    'romes': ['H2207'],
    'includes': [],
    'excludes': [],
    'sizes': ['pme'],
    'multipliers': {
        'fg': 5
    },
}
```

Codes multiplicateurs:
 - fg: multiplicatateur force geo (distance)
 - fn: multiplicateur force naf (rome/naf)
 - ft: multiplicateur force taille
 - fw: multiplicateur force bienvenue
 - fc: multiplicateur force contact
"""


def distance(data, acc):
    acc['max_distance'] = data.distance_km
    acc['multipliers']['fg'] = data.priority
    return acc


def rome_codes(data, acc):
    # FIXME add rome include / exclude rule
    romelist = []
    for rome in data.rome_list:
        if rome.include:
            romelist.append(rome.id)
    acc['romes'] = romelist
    acc['multipliers']['fn'] = data.priority
    return acc
