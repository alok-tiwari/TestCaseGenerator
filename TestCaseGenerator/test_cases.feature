Feature: Test Alert Delivery via Email
  As a user
  I want to perform the required actions
  So that achieve the desired functionality

  Background:
    Given the system is in a known state


  Scenario: Test Alert Delivery via Email
        Given I am logged into the EcoStruxure platform as a user
    When I set up an email alert for a piece of equipment with high temperature thresholds
    Then I should receive an email notification with recommended actions and expected risk levels when the equipment's temperature exceeds the threshold and Expected result achieved

  Scenario: Test Alert Delivery via Mobile Notifications
        Given I am logged into the EcoStruxure platform as a user
    When I set up a mobile notification alert for a piece of equipment with low energy consumption thresholds
    Then I should receive a push notification on my mobile device with recommended actions and expected risk levels when the equipment's energy consumption falls below the threshold and Expected result achieved

  Scenario: Test Alert History and Filtering
        Given I am logged into the EcoStruxure platform as a user
    When I view the alert history for a piece of equipment
    Then I should see all previous alerts, including those with recommended actions and expected risk levels, filtered by date and equipment type and Expected result achieved

  Scenario: Test Predictive Analytics Updates
        Given I am logged into the EcoStruxure platform as a user
    When I wait 10 minutes for the predictive analytics to update
    Given the system should have updated its predictions on equipment performance based on real-time sensor data

  Scenario: Test Alert Response with Recommended Actions
        Given I am logged into the EcoStruxure platform as a user and have set up an alert for a piece of equipment with malfunctioning air conditioning
    Then I receive the alert notification and Action completed
    Then I should see recommended actions to resolve the issue, such as scheduling maintenance or contacting a technician, along with expected risk levels and Expected result achieved