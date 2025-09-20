Feature: Test Alert Delivery via Email
  As a user
  I want to perform the required actions
  So that achieve the desired functionality

  Background:
    Given the system is in a known state


  Scenario: Test Alert Delivery via Email
        When I am a user with email notification enabled
    When I log into the EcoStruxure platform and equipment performance deviates from normal operational thresholds
    Then I should receive an email with a maintenance alert, including recommended actions and expected risk levels and Expected result achieved

  Scenario: Test Alert Delivery via Mobile Notifications
        Given I have mobile notifications enabled on my device
    When I log into the EcoStruxure platform and equipment performance deviates from normal operational thresholds
    Then I should receive a push notification with a maintenance alert, including recommended actions and expected risk levels and Expected result achieved

  Scenario: Test Alert Delivery via Dashboard Pop-ups
        Given I have dashboard pop-up notifications enabled on my device
    When I log into the EcoStruxure platform and equipment performance deviates from normal operational thresholds
    Then I should receive a pop-up notification with a maintenance alert, including recommended actions and expected risk levels and Expected result achieved

  Scenario Outline: Test Alert History and Filtering
        Given I have viewed multiple alerts for different equipment types
    When I log into the EcoStruxure platform and filter by equipment type or location
    When I can view historical alerts for the selected equipment type or location
    
    Examples:
      | data_1 | data_2 |
      | valid data | expected result 1 |
      | invalid data | expected result 2 |
      | boundary data | expected result 3 |

  Scenario: Test Predictive Analytics Updates
        When The system has not updated predictive analytics in 10 minutes
    When The system detects abnormal behavior in a piece of equipment
    Then The predictive analytics should update every 10 minutes to maintain accuracy, and I should receive an alert with recommended actions and Expected result achieved