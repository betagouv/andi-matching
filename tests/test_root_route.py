"""
Tests de la route /
"""
import pytest
import andi.webservice.routers.root as target


@pytest.mark.parametrize(
    "value,expected",
    (("postgresql://hostname/database?que=ry&str=ing", None),
     ("postgresql://username@host.name/database", None),
     ("postgresql://username@host.name:5432/database", None),
     ("postgresql://username:passw@hostname/database", "postgresql://username:<censored>@hostname/database")
     )
)
def test_censored_url(value, expected):
    result = target.censored_url(value)
    if expected is None:
        # Ne doit pas être modifiée (pas de MDP dans l'URL)
        assert result == value
    else:
        assert result == expected


def test_root_route(client):
    response = client.get("/")
    assert response.status_code == 200
    response_body = response.json()
    assert len(response_body) == 11
    assert set(response_body) == {
        "all_systems", "timestamp", "start_time", "uptime", "api_version", "configuration",
        "database", "software_version", "base_url", "doc_urls", "openapi_url"
    }
