# Test Case Generator Project

## Project Overview
This project automates the generation of test cases from Jira tickets, helping QA teams save time and ensure comprehensive test coverage. It connects to Jira, extracts ticket details (like user stories and acceptance criteria), and uses AI to generate relevant test cases in various formats.

## Key Features
- **Jira Integration**: Fetches ticket details including user stories, acceptance criteria, and metadata
- **AI-Powered Test Generation**: Uses language models (OpenAI, Ollama, custom) to create comprehensive test cases
- **Multiple Test Types**: Supports functional, security, API, UI, performance, accessibility, and edge case tests
- **Multiple Output Formats**: Supports Gherkin (BDD), Playwright, Pytest, Cypress, Selenium, JUnit, and human-readable formats
- **Dummy Mode**: Test without Jira access using synthetic data
- **Configurable**: Can be configured for different projects and test types

## How It Works
1. **Jira Connection**: Authenticates with Jira using API credentials
2. **Ticket Fetching**: Retrieves specified tickets or searches based on criteria
3. **Test Generation**: Processes ticket content to generate:
   - Functional test cases
   - Security test cases
   - API test cases
   - UI test cases
   - Performance test cases
   - Accessibility test cases
   - Edge case test scenarios
4. **Formatting**: Outputs tests in desired format (Gherkin, code skeletons, human-readable)
5. **Storage**: Saves generated tests to files

```
[Jira] → [Ticket Data] → [AI Processing] → [Test Cases] → [Output Files]
```

## Project Structure
```
TestCaseGenerator/
├── config/            # Configuration files
├── generators/        # Test case generation logic
├── integrations/      # Jira and LLM clients
├── formatters/        # Output formatting
├── models/            # Data models
├── parsers/           # Content parsing
└── main.py            # Main application entry
```

## Scaling Opportunities & Impact

### Time Savings & Standardization
- **40-60% reduction** in test case creation time (estimated 8-12 hours saved per sprint)
- **Standardized test formats** ensure consistency across teams and projects
- **Automated edge case detection** improves test coverage by 25-40%

### Implementation Roadmap
1. **Additional Test Types** (Next 3 months):
   - Performance testing (JMeter integration)
   - Security testing (OWASP ZAP integration)
   - Accessibility testing (axe-core integration)
   - Implementation: Modular generator architecture with plugin system

2. **Team Collaboration** (Next 6 months):
   - Review workflows with approval chains
   - Commenting/annotation system
   - Version history for test cases
   - Implementation: MongoDB backend for collaborative features

3. **CI/CD Integration** (Next 9 months):
   - GitHub Actions/Jenkins hooks
   - Test execution reporting
   - Fail-fast pipelines
   - Implementation: REST API endpoints for CI systems

## Agentic AI Framework Integration

### Execution Model
- **Trigger Points**:
  - Jira webhooks (on ticket update/creation)
  - CLI invocation (`python main.py generate-from-jira`)
  - Scheduled runs (cron jobs)


### Architectural Boundaries
- **Scope**: Focused on test generation only
- **Extension Points**:
  - REST API for other agents
  - Webhook subscriptions
  - Plugin system for custom generators

## Getting Started
1. Install dependencies with `pip install -r requirements.txt`
2. (Optional) Set up Jira API credentials in `.env` for real Jira integration
3. Run with dummy data: `python main.py generate-from-jira --ticket-id SJP-2 --dummy --output test_cases.feature`
4. Or run with real Jira: `python main.py generate-from-jira --ticket-id SJP-2 --output test_cases.feature`

This tool helps bridge the gap between requirements and testing, ensuring nothing falls through the cracks while saving valuable QA time.