@fixture.matching_api
Feature: rome_suggest

  Scenario: Obtaining rome suggestions for a string
    Given the api is available
      When we submit "phil" to the rome_suggest endpoint
        Then we receive multiple responses
        And one of them is for rome code "K2401"

  Scenario: Empty result when search string is too short
    Given the api is available
      When we submit "pl" to the rome_suggest endpoint
        Then we receive an empty array response

  Scenario: Empty result when search string is empty
    Given the api is available
      When we submit an empty query to the rome_suggest endpoint
        Then we receive an empty array response


