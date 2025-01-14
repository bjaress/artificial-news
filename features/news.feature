
Feature: speaking the news

  Background: Dependencies
    Given Spreaker is available
    Given Google is available
    Given Wikipedia is available
    Given the app is running

  Scenario: one simple news item
    Given there is a simple news item about frogs
    When it is time to generate news
    Then headlines are retrieved from Wikipedia
    And the episode list from Spreaker is retrieved
    And Wikipedia articles about frogs are retrieved
    And a script about frogs is sent for text-to-speech processing
    And an episode about frogs is uploaded to Spreaker
