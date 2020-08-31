"""
Tests de la route /rome_suggest
"""
import pytest
from andi.webservice.schemas.romesuggest import RomeResponseModel


def test_rome_suggest_boulanger(client):
    response = client.get("/rome_suggest", params={"q": "boulanger"})
    assert response.status_code == 200
    response_body = response.json()
    results = RomeResponseModel.parse_obj(response_body).data
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
def test_answered_rome_suggest(client, term, exp_code):
    response = client.get("/rome_suggest", params={"q": term})
    assert response.status_code == 200
    response_body = response.json()
    results = RomeResponseModel.parse_obj(response_body).data
    assert exp_code in {result.id for result in results}


@pytest.mark.parametrize(
    "term",
    ("", "pl")
)
def test_too_short_querty_rome_suggest(client, term):
    response = client.get("/rome_suggest", params={"q": term})
    assert response.status_code == 200
    response_body = response.json()
    results = RomeResponseModel.parse_obj(response_body).data
    assert results == []
