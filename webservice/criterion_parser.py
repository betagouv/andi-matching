
"""
Traitement des critères du matching.

Chaque fonction de traitement retourne l'accumulateur mis à jour
"""


def distance(data, acc):
    acc['max_distance'] = data.distance_km
    return acc


def rome_codes(data, acc):
    # FIXME add rome include / exclude rule
    romelist = []
    for rome in data.rome_list:
        if rome.include:
            romelist.append(rome.id)
    acc['romes'] = romelist
    return acc
