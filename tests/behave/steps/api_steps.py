import requests
from behave import when, given, then


@given(u'the api is available')
def step_impl(context):
    r = requests.get(f'http://{context.api_host}:{context.api_port}/')
    data = r.json()
    assert 'all_systems' in data
    assert data['all_systems'] == 'nominal'


@when(u'we submit "{query}" to the rome_suggest endpoint')
def step_impl(context, query):
    raise NotImplementedError(u'STEP: When we submit "phil" to the rome_suggest endpoint')


@then(u'we receive multiple responses')
def step_impl(context):
    raise NotImplementedError(u'STEP: Then we receive multiple responses')


@then(u'one of them is for rome code "{rome_code}"')
def step_impl(context, rome_code):
    raise NotImplementedError(u'STEP: Then one of them is for rome code "K1204"')
