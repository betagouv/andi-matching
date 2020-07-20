# pylint: skip-file
"""
Modèle des données en sortie pour le service matching

Prototype convenu:
```json
{
    '_v': 1,
    '_timestamp': 123125412,
    '_query_id': 'efb7afcf-836b-4029-a3ce-f7c0b4b3499b',
    '_session_id': 'efb7afcf-836b-4029-a3ce-f7c0b4b3499b',
    '_trace': 'aweofuiiu9274083',
    'data':
        [
            {
                'id': '12',
                'name': 'Pains d\'Amandine',
                'address': 'ADDRESSE',
                'departement': '29'
                'city': 'Cergy',
                'coords': {'lat': 93.123, 'lon': 83.451},
                'size': 'pme',
                'naf': '7711A',
                'siret': '21398102938',
                'distance': 54,
                'scoring': {'geo': 3, 'size': 4, 'contact': 2, 'pmsmp': 3, 'naf': 5},
                'score': 53,
                'activity': 'Boulangerie',
            },
        ]
}
```
"""


