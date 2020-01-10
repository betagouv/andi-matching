Feature: rome_suggest

  @fixture.matching_api
  Scenario: Obtaining rome suggestions for a string
    Given the api is available
      When we submit "phil" to the rome_suggest endpoint
        Then we receive multiple responses
        And one of them is for rome code "K1204"
