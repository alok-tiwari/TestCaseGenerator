Feature: Test Alert Delivery via Email
  As a user
  I want to perform the required actions
  So that achieve the desired functionality

  Background:
    Given the system is in a known state


  Scenario: Test Alert Delivery via Email
        Given I am logged into the EcoStruxure platform as a user
    When I set up an alert for abnormal HVAC system performance
    When I should receive an email notification with recommended actions and expected risk levels within 5 minutes of the alert being triggered

  Scenario: Test Alert History and Filtering
        Given I am logged into the EcoStruxure platform as a user
    When I view my alert history for a specific piece of equipment
    Then I should be able to filter the alerts by equipment type (e.g. HVAC, lighting) or location (e.g. building A, floor 3) and Expected result achieved

  Scenario: Test Predictive Analytics Updates
        When The system detects abnormal behavior in a piece of energy system equipment
    When The predictive analytics update interval has passed (10 minutes)
    Given The system should have updated its predictive model to reflect the new data and provide more accurate recommendations for maintenance.

  Scenario: Test Recommended Actions and Risk Levels
        Given I am logged into the EcoStruxure platform as a user
    When I receive an alert for abnormal lighting system performance
    Then I should see a recommended action (e.g. replace bulb, adjust dimmer) and expected risk level (e.g. low, moderate, high) displayed in the alert notification. and Expected result achieved

  Scenario: Test Alert Delivery via Mobile Notifications
        Given I am logged into the EcoStruxure platform as a user
    When I set up an alert for abnormal energy system performance
    When I should receive a mobile notification with recommended actions and expected risk levels within 2 minutes of the alert being triggered.