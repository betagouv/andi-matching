@fixture.matching_api
Feature: rome_suggest

  Scenario: Obtaining rome suggestions for a string
    Given the api is available
      When we submit "phil" to the rome_suggest endpoint
        Then we receive multiple responses
        And one of them is for rome code "K2401"

  Scenario: Obtaining rome suggestions for a hairdresser
    Given the api is available
      When we submit "coiff" to the rome_suggest endpoint
        Then we receive multiple responses
        And one of them is for rome code "D1202"
       When we submit "Coiffure" to the rome_suggest endpoint
        Then we receive multiple responses
        And one of them is for rome code "D1202"


  Scenario: Obtaining rome suggestions long queries
    Given the api is available
      When we submit "Vente en articles de sport et loisirs" to the rome_suggest endpoint
        Then we receive one response
        And one of them is for rome code "D1211"

  Scenario: Empty result when search string is too short
    Given the api is available
      When we submit "pl" to the rome_suggest endpoint
        Then we receive an empty array response

  Scenario: Empty result when search string is empty
    Given the api is available
      When we submit an empty query to the rome_suggest endpoint
        Then we receive an empty array response


