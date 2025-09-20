Feature: Test Alert Delivery via Email
  As a user
  I want to perform the required actions
  So that achieve the desired functionality

  Background:
    Given the system is in a known state


  Scenario: Test Alert Delivery via Email
        Given I am logged into the EcoStruxure platform as a user
    When I set up an alert for low energy consumption in a specific room
    Then I should receive an email with recommended actions and expected risk levels within 5 minutes of the threshold being breached and Expected result achieved

  Scenario: Test Alert Delivery via Mobile Notifications
        Given I am logged into the EcoStruxure platform as a user
    When I set up an alert for high temperature in a specific HVAC unit
    Then I should receive a mobile notification with recommended actions and expected risk levels within 10 minutes of the threshold being breached and Expected result achieved

  Scenario: Test Alert History and Filtering
        Given I am logged into the EcoStruxure platform as a user
    When I view my alert history for a specific piece of equipment
    Given I should see all historical alerts, including those that have been resolved and those that are still active, with options to filter by equipment type or location

  Scenario: Test Predictive Analytics Updates
        Given I am logged into the EcoStruxure platform as a user
    When I wait for 10 minutes without any new data being uploaded
    Then the predictive analytics should update with new insights and trends based on the latest sensor data and Expected result achieved

  Scenario: Test Alert Response and Resolution
        Given I am logged into the EcoStruxure platform as a user and have set up an alert for low energy consumption in a specific room
    Then I receive the alert and take recommended actions to resolve the issue and Action completed
    Then the alert should be marked as resolved, and I should see historical data indicating that the issue was resolved within a reasonable timeframe. and Expected result achieved