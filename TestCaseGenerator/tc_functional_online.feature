Feature: Test Alert Delivery via Email
  As a user
  I want to perform the required actions
  So that achieve the desired functionality

  Background:
    Given the system is in a known state


  Scenario: Test Alert Delivery via Email
        Given I am logged into the EcoStruxure platform as a user
    When I set up an alert for abnormal temperature readings in the HVAC system
    When I should receive an email with recommended actions and expected risk levels within 5 minutes of the alert being triggered

  Scenario: Test Alert Delivery via Mobile Notifications
        Given I am logged into the EcoStruxure platform as a user
    When I set up an alert for abnormal lighting usage in a specific location
    When I should receive a mobile notification with recommended actions and expected risk levels within 5 minutes of the alert being triggered

  Scenario: Test Alert Delivery via Dashboard Pop-ups
        Given I am logged into the EcoStruxure platform as a user
    When I set up an alert for abnormal energy consumption in the building
    When I should receive a dashboard pop-up with recommended actions and expected risk levels within 5 minutes of the alert being triggered

  Scenario Outline: Test Historical Alert Trending
        Given I am logged into the EcoStruxure platform as a user
    When I view the historical alerts for the HVAC system
    Then I can filter the alerts by date range, equipment type, and location to see trends in abnormal behavior
    
    Examples:
      | data_1 | data_2 |
      | valid data | expected result 1 |
      | invalid data | expected result 2 |
      | boundary data | expected result 3 |

  Scenario: Test Predictive Analytics Updates
        Given I am logged into the EcoStruxure platform as a user
    When the 10-minute predictive analytics update period has passed
    Given the system should have updated its models with new data, and I can view the updated predictions on the dashboard