"""
Tests de andi.webservice.match
"""
from asyncio import coroutine
from decimal import Decimal

import andi.webservice.match as target


def test_selected_nafs_from_romes():
    result, _ = target.selected_nafs_from_romes(["A1101"])
    assert result == {'0161Z': '5', '7731Z': '4', '0210Z': '3', '0114Z': '3', '0220Z': '3', '0141Z': '3', '0111Z': '2',
                      '1091Z': '1', '7830Z': '1', '4941B': '1', '4941A': '1', '4312A': '1', '0121Z': '1', '0146Z': '1',
                      '2365Z': '1'}


# ROME D1106 = Plombier
query = {
    '_query_id': '6e2993cc-e87b-4de1-a53b-8df893bba5ef',
    '_session_id': '5755f30c-51e6-43be-b6d0-e21762478f51',
    '_timestamp': '2020-08-08 21:42:50.433095+00:00',
    '_v': 1,
    'address': {'type': 'string', 'value': '16, rue de Lyon - 89200 Avallon'},
    'criteria': [{'distance_km': 1, 'name': 'distance', 'priority': 2},
                 {'exclude_naf': [],
                  'name': 'rome_codes',
                  'priority': 5,
                  'rome_list': [{'exclude': False,
                                 'id': 'D1106',
                                 'include': True}]}]}

# Réponse brute de laBD (transformée en liste de dicos)
expected_raw = [
    {
        'adresse': '10 Route de Paris 89200 Avallon',
        'commune': 'AVALLON',
        'departement': '89',
        'distance': Decimal('0.5'),
        'id': 10066191,
        'lat': Decimal('47.493522'),
        'lon': Decimal('3.906388'),
        'naf': '4322A',
        'nom': 'FRANCK LEGER',
        'phonenumber': None,
        'score_contact': 1,
        'score_geo': 3,
        'score_naf': 5,
        'score_size': 3,
        'score_total': 44,
        'score_welcome': 1,
        'sector': "Travaux d'installation d'eau et de gaz en tous locaux",
        'siret': '79078024100010',
        'taille': '3-5'},
    {
        'adresse': '1 Route de Chassigny 89200 Avallon',
        'commune': 'AVALLON',
        'departement': '89',
        'distance': Decimal('1.0'),
        'id': 10054623,
        'lat': Decimal('47.491337'),
        'lon': Decimal('3.923938'),
        'naf': '3600Z',
        'nom': 'VEOLIA EAU - COMPAGNIE GENERALE DES EAUX',
        'phonenumber': None,
        'score_contact': 1,
        'score_geo': 1,
        'score_naf': 2,
        'score_size': 5,
        'score_total': 29,
        'score_welcome': 1,
        'sector': "Captage, traitement et distribution d'eau",
        'siret': '57202552600300',
        'taille': '20-49'},
    {
        'adresse': '34 Route de Lormes 89200 Avallon',
        'commune': 'AVALLON',
        'departement': '89',
        'distance': Decimal('0.7'),
        'id': 10023626,
        'lat': Decimal('47.484699'),
        'lon': Decimal('3.909559'),
        'naf': '4321A',
        'nom': 'DEVOUCOUX MICHEL',
        'phonenumber': None,
        'score_contact': 1,
        'score_geo': 2,
        'score_naf': 2,
        'score_size': 3,
        'score_total': 27,
        'score_welcome': 1,
        'sector': "Travaux d'installation électrique dans tous locaux",
        'siret': '35032908200027',
        'taille': '3-5'},
    {
        'adresse': 'Impasse Derrière les Prés 89200 Avallon',
        'commune': 'AVALLON',
        'departement': '89',
        'distance': Decimal('0.9'),
        'id': 10044915,
        'lat': Decimal('47.498268'),
        'lon': Decimal('3.913825'),
        'naf': '3320B',
        'nom': 'SARL ID FROID',
        'phonenumber': None,
        'score_contact': 1,
        'score_geo': 1,
        'score_naf': 2,
        'score_size': 3,
        'score_total': 25,
        'score_welcome': 1,
        'sector': 'Installation de machines et équipements mécaniques',
        'siret': '40375901200020',
        'taille': '3-5'}]

expected = {'_query_id': '6e2993cc-e87b-4de1-a53b-8df893bba5ef',
            '_session_id': '5755f30c-51e6-43be-b6d0-e21762478f51',
            '_trace': 'not_implemented_yet',
            '_v': 1,
            'data': [{'activity': "Travaux d'installation d'eau et de gaz en tous locaux",
                      'address': '10 Route de Paris 89200 Avallon',
                      'city': 'AVALLON',
                      'coords': {'lat': 93.0, 'lon': 18.0},
                      'departement': '89',
                      'distance': 0.5,
                      'id': '10066191',
                      'naf': '4322A',
                      'name': 'FRANCK LEGER',
                      'phonenumber': None,
                      'score': 44,
                      'scoring': {'contact': 1, 'geo': 3, 'naf': 5, 'pmsmp': 1, 'size': 3},
                      'siret': '79078024100010',
                      'size': '3-5'},
                     {'activity': "Captage, traitement et distribution d'eau",
                      'address': '1 Route de Chassigny 89200 Avallon',
                      'city': 'AVALLON',
                      'coords': {'lat': 93, 'lon': 18},
                      'departement': '89',
                      'distance': 1.0,
                      'id': '10054623',
                      'naf': '3600Z',
                      'name': 'VEOLIA EAU - COMPAGNIE GENERALE DES EAUX',
                      'phonenumber': None,
                      'score': 29,
                      'scoring': {'contact': 1, 'geo': 1, 'naf': 2, 'pmsmp': 1, 'size': 5},
                      'siret': '57202552600300',
                      'size': '20-49'},
                     {'activity': "Travaux d'installation électrique dans tous locaux",
                      'address': '34 Route de Lormes 89200 Avallon',
                      'city': 'AVALLON',
                      'coords': {'lat': 93.0, 'lon': 18.0},
                      'departement': '89',
                      'distance': 0.7,
                      'id': '10023626',
                      'naf': '4321A',
                      'name': 'DEVOUCOUX MICHEL',
                      'phonenumber': None,
                      'score': 27,
                      'scoring': {'contact': 1, 'geo': 2, 'naf': 2, 'pmsmp': 1, 'size': 3},
                      'siret': '35032908200027',
                      'size': '3-5'},
                     {'activity': 'Installation de machines et équipements mécaniques',
                      'address': 'Impasse Derrière les Prés 89200 Avallon',
                      'city': 'AVALLON',
                      'coords': {'lat': 93.0, 'lon': 18.0},
                      'departement': '89',
                      'distance': 0.9,
                      'id': '10044915',
                      'naf': '3320B',
                      'name': 'SARL ID FROID',
                      'phonenumber': None,
                      'score': 25,
                      'scoring': {'contact': 1, 'geo': 1, 'naf': 2, 'pmsmp': 1, 'size': 3},
                      'siret': '40375901200020',
                      'size': '3-5'}]}


def test_match_route(client, mocker):
    target.conn_fetch = mocker.Mock(side_effect=coroutine(lambda *args: expected_raw))
    response = client.post("/match", json=query)
    assert response.status_code == 200
    result = response.json()
    del result["_timestamp"]  # On ne peut pas deviner...
    assert result == expected
