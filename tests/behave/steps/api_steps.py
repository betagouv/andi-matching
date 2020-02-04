# pylint: disable=function-redefined
import requests
from behave import when, given, then

TEST_UUID = 'ffffffff-1111-2222-3333-ffffffffffff'


@given(u'the api is available')
def step_impl(context):
    r = requests.get(f'http://{context.api_host}:{context.api_port}/')
    data = r.json()
    assert 'all_systems' in data
    assert data['all_systems'] == 'nominal'


@when(u'we submit "{query}" to the rome_suggest endpoint')
def step_impl(context, query):
    r = requests.get(
        f'http://{context.api_host}:{context.api_port}/rome_suggest',
        params={
            'q': query,
            '_sid': TEST_UUID,
            '_v': 1
        })
    context.raw_response = r


@when(u'we submit an empty query to the rome_suggest endpoint')
def step_impl(context):
    r = requests.get(
        f'http://{context.api_host}:{context.api_port}/rome_suggest',
        params={
            'q': '',
            '_sid': TEST_UUID,
            '_v': 1
        })
    context.raw_response = r


@then(u'we receive multiple responses')
def step_impl(context):
    data = context.raw_response.json()
    context.response_data = data
    assert len(data['data']) > 0


@then(u'we receive one response')
def step_impl(context):
    data = context.raw_response.json()
    context.response_data = data
    print(data)
    assert len(data['data']) == 1


@then(u'we receive an empty array response')
def step_impl(context):
    print(context.raw_response)
    full_data = context.raw_response.json()
    print(full_data)
    data = full_data.get('data')
    assert isinstance(data, list)
    assert len(data) == 0


@then(u'one of them is for rome code "{rome_code}"')
def step_impl(context, rome_code):
    found = False
    print(context.response_data)
    for result in context.response_data.get('data'):
        found = True if found else result.get('id') == rome_code
    assert found
