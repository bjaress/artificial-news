
Feature: speaking the news
  Scenario: one simple news item
    Given there is a simple news item about frogs
    When it is time to generate news
    Then headlines are retrieved from Wikipedia
