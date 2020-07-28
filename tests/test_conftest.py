"""
Test des fixtures
"""
import json
import pytest
from aiohttp import ClientSession


def test_source_tree(source_tree):
    assert (source_tree / "setup.py").is_file()


def test_data_directory(data_directory):
    assert data_directory.is_dir()


@pytest.mark.asyncio
async def test_mocked_aiohttp(mocker, mocked_aiohttp_response):
    async def function_under_test():
        url = "http://fake-api/schtroumpf"
        params = {"any": "parameter"}
        async with ClientSession() as session:
            async with session.get(url, params=params) as response:
                return await response.json()
    expected = {"anything": "does the job"}
    fake_json_response = mocked_aiohttp_response(json.dumps(expected), 200)
    mocker.patch("aiohttp.ClientSession.get", return_value=fake_json_response)
    out = await function_under_test()
    assert out == expected
