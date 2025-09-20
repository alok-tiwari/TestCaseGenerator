Feature: Test Alert Delivery via Email
  As a user
  I want to perform the required actions
  So that achieve the desired functionality

  Background:
    Given the system is in a known state


  Scenario: Test Alert Delivery via Email
        Given I am logged into the EcoStruxure platform as a user
    When I set up an alert for abnormal temperature readings in the HVAC system
    Then I receive an email with the alert details, including recommended actions and expected risk levels and Expected result achieved

  Scenario: Test Alert Delivery via Mobile Notifications
        Given I am logged into the EcoStruxure platform as a user
    When I enable mobile notifications for alerts on my device
    Then I receive a push notification with the alert details, including recommended actions and expected risk levels and Expected result achieved

  Scenario: Test Alert Delivery via Dashboard Pop-ups
        Given I am logged into the EcoStruxure platform as a user
    Given I have enabled dashboard pop-up notifications for alerts
    Then I see a pop-up window with the alert details, including recommended actions and expected risk levels and Expected result achieved

  Scenario Outline: Test Historical Alerts and Trends
        Given I am logged into the EcoStruxure platform as a user
    When I view historical alerts for the HVAC system
    Then I can filter the alerts by date range and equipment type, and see trends in alert frequency over time
    
    Examples:
      | data_1 | data_2 |
      | valid data | expected result 1 |
      | invalid data | expected result 2 |
      | boundary data | expected result 3 |

  Scenario: Test Predictive Analytics Updates
        Given I am logged into the EcoStruxure platform as a user
    When the 10-minute predictive analytics update cycle completes
    When the system has updated its predictions for equipment performance, including any new alerts or recommendations