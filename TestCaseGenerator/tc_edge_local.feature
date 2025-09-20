Feature: I want to monitor equipment performance in real-time
  As a facility manager
  I want to monitor equipment performance in real-time
  So that I can prevent equipment failures and optimize energy usage

  Background:
    Given the system is in a known state


  Scenario: "Facility Manager Monitors Equipment Performance with No Valid Permissions"
        When a facility manager user from local_user_story.txt without any permissions
    When they attempt to monitor equipment performance in real-time
    Given an error message is displayed indicating that they do not have valid access

  Scenario: "Real-Time Monitoring with Zero Data"
        Given the system is in a known state with no data available for monitoring
    When the facility manager user attempts to view real-time equipment performance data
    Given an empty graph or table is displayed, indicating no data is available

  Scenario Outline: "Facility Manager Monitors Equipment Performance with Invalid Input"
        When a facility manager user from local_user_story.txt with invalid input (e.g. non-numeric values)
    When they attempt to monitor equipment performance in real-time
    Then an error message is displayed, indicating that the input is invalid
    
    Examples:
      | data_1 | data_2 |
      | valid data | expected result 1 |
      | invalid data | expected result 2 |
      | boundary data | expected result 3 |

  Scenario: "System Failure due to Network Connection Loss"
        When the system is connected to a network and experiencing high latency
    When the facility manager user attempts to view real-time equipment performance data
    Then the system fails to respond or displays an error message, indicating a network connection loss and Expected result achieved

  Scenario: "Facility Manager Monitors Equipment Performance with Maximum Allowed Data"
        When a facility manager user from local_user_story.txt with maximum allowed data (e.g. 1000 devices)
    When they attempt to monitor equipment performance in real-time
    Given the system displays all available data, but with limitations on display or filtering options due to data overload