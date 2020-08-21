"""
Tests de la route /rome_suggest
"""
import pytest
from andi.webservice.schemas.romes import RomeSuggestion


def test_romes_boulanger(client):
    response = client.get("/1.0/romes", params={"q": "boulanger"})
    assert response.status_code == 200
    response_body = response.json()
    results = [RomeSuggestion.parse_obj(item) for item in response_body]
    assert len(results) == 5
    assert {result.id for result in results} == {"D1502", "H2102", "D1507", "D1102", "D1106"}
    for result in results:
        assert "boulanger" in result.label


@pytest.mark.parametrize(
    "term,exp_code",
    (("phil", "K2401"),
     ("coiff", "D1202"),
     ("Coiffure", "D1202"),
     ("Vente en articles de sport et loisirs", "D1211"),
     ("conseiller en", "A1301"),
     )
)
def test_answered_romes(client, term, exp_code):
    response = client.get("/1.0/romes", params={"q": term})
    assert response.status_code == 200
    response_body = response.json()
    results = [RomeSuggestion.parse_obj(item) for item in response_body]
    assert exp_code in {result.id for result in results}


@pytest.mark.parametrize(
    "term",
    ("", "pl")
)
def test_too_short_querty_romes(client, term):
    response = client.get("/1.0/romes", params={"q": term})
    assert response.status_code == 200
    response_body = response.json()
    results = [RomeSuggestion.parse_obj(item) for item in response_body]
    assert results == []
