Feature: Test Alert Delivery via Email
  As a user
  I want to perform the required actions
  So that achieve the desired functionality

  Background:
    Given the system is in a known state


  Scenario: Test Alert Delivery via Email
        Given I am logged into the EcoStruxure platform as a user
    When I set up an alert for abnormal behavior in my HVAC system
    Then I should receive an email with the alert details and recommended action within 5 minutes of the anomaly detection and Expected result achieved

  Scenario: Test Alert Delivery via Mobile Notifications
        Given I am logged into the EcoStruxure platform as a user
    When I set up an alert for abnormal behavior in my lighting system
    Then I should receive a mobile notification with the alert details and recommended action within 5 minutes of the anomaly detection and Expected result achieved

  Scenario: Test Alert Delivery via Dashboard Pop-ups
        Given I am logged into the EcoStruxure platform as a user
    When I set up an alert for abnormal behavior in my energy system
    Then I should receive a dashboard pop-up with the alert details and recommended action within 5 minutes of the anomaly detection and Expected result achieved

  Scenario Outline: Test Historical Alert Trends
        Given I am logged into the EcoStruxure platform as a user
    When I view the historical alerts for my HVAC system
    When I can filter the alerts by date range, equipment type, or location to analyze trends and patterns in my system's performance
    
    Examples:
      | data_1 | data_2 |
      | valid data | expected result 1 |
      | invalid data | expected result 2 |
      | boundary data | expected result 3 |

  Scenario: Test Predictive Analytics Updates
        Given I am logged into the EcoStruxure platform as a user
    When the 10-minute update cycle for predictive analytics has passed
    Given the system should have updated its predictions and recommendations based on new data, reflecting the latest trends and anomalies in my equipment's performance