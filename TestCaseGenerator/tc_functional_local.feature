Feature: I want to monitor equipment performance in real-time
  As a facility manager
  I want to monitor equipment performance in real-time
  So that I can prevent equipment failures and optimize energy usage

  Background:
    Given the system is in a known state


  Scenario: Test Real-time Equipment Performance Monitoring
        When a facility manager with valid permissions to access equipment monitoring feature
    When they interact with the system by clicking on "Monitor Equipment" button
    When they should see real-time performance data of all equipment in the facility

  Scenario: Test Equipment Failure Prevention
        When a facility manager with valid permissions to access equipment monitoring feature and an equipment failure is simulated
    Then they receive alerts for failed equipment and take corrective action and Action completed
    Then they should be able to prevent further equipment failures and optimize energy usage and Expected result achieved

  Scenario: Test System Response to User Interaction
        When the system is in a known state (i.e., all equipment is online)
    When a facility manager interacts with the system by clicking on "Monitor Equipment" button
    When the system should respond by displaying real-time performance data of all equipment

  Scenario: Test Valid Permissions for Feature Access
        When a user without valid permissions to access equipment monitoring feature
    When they attempt to access the feature
    Given they should be denied access and receive an error message indicating that they do not have sufficient permissions

  Scenario: Test Equipment Data Accuracy
        When a facility manager with valid permissions to access equipment monitoring feature
    When they view real-time performance data of an equipment
    Then the system should display accurate and up-to-date data, including current status, temperature, and energy consumption and Expected result achieved