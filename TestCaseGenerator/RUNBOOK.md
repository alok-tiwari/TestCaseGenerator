# Test Case Generator Runbook

## 1. Environment Setup

### 1.1 Prerequisites
- Python 3.11 or higher
- Virtual Environment
- Jira Account with API Access (optional - can use dummy mode)

### 1.2 Virtual Environment Setup
```bash
cd /Users/aloktiwari/Documents/visual-studio-code-base/llama-base/AgenticLegoLand/TestCaseGenerator
python -m venv py311-llm-venv
source py311-llm-venv/bin/activate
pip install -r requirements.txt
```

### 1.3 Environment Variables (Optional)
Create `.env` file for Jira integration:
```bash
# Jira Configuration
JIRA_BASE_URL=https://yourcompany.atlassian.net
JIRA_USERNAME=your-email@company.com
JIRA_API_TOKEN=your-api-token

# LLM Configuration (optional - defaults to Ollama)
OPENAI_API_KEY=your-openai-key
CUSTOM_ENDPOINT=your-custom-llm-endpoint
CUSTOM_API_KEY=your-custom-api-key
```

## 2. Running the Application

### 2.1 Local Mode (Recommended for Testing)
Generate test cases from local user story file (no API calls):
```bash
python main.py generate-from-jira --ticket-id SJP-2 --story-format raw --provider ollama --output test_cases.feature --mode local
```

### 2.2 Online Mode (Real Jira Integration)
Generate test cases from real Jira ticket:
```bash
python main.py generate-from-jira --ticket-id SJP-2 --story-format raw --provider ollama --output test_cases.feature --mode online
```

### 2.3 Available Options

#### Test Types
- `--types functional` (default) - Functional test cases
- `--types security` - Security test cases
- `--types api` - API test cases
- `--types ui` - UI test cases
- `--types performance` - Performance test cases
- `--types accessibility` - Accessibility test cases
- `--types edge` - Edge case test scenarios (boundary conditions, error cases)

#### Story Formats
- `--story-format raw` (default) - Parse unstructured text
- `--story-format gherkin` - Parse Gherkin format

#### Output Formats
- `--format gherkin` (default) - Gherkin/BDD format
- `--format playwright` - Playwright code skeleton
- `--format pytest` - Pytest code skeleton
- `--format cypress` - Cypress code skeleton
- `--format selenium` - Selenium code skeleton
- `--format junit` - JUnit code skeleton
- `--format human` - Human-readable format

#### Test Levels
- `--level unit` - Unit tests
- `--level integration` (default) - Integration tests
- `--level e2e` - End-to-end tests
- `--level system` - System tests

#### LLM Providers
- `--provider ollama` (default) - Local Ollama server
- `--provider openai` - OpenAI API
- `--provider custom` - Custom LLM endpoint

#### Modes
- `--mode local` - Read from local_user_story.txt file (no Jira API calls)
- `--mode online` (default) - Use real Jira API

### 2.4 Example Commands

#### Generate Functional Tests (Local Mode)
```bash
python main.py generate-from-jira --ticket-id SJP-2 --types functional --story-format raw --provider ollama --output functional_tests.feature --mode local
```

#### Generate Security Tests (Online Mode)
```bash
python main.py generate-from-jira --ticket-id SJP-2 --types security --story-format raw --provider ollama --output security_tests.feature --mode online
```

#### Generate Edge Case Tests (Local Mode)
```bash
python main.py generate-from-jira --ticket-id SJP-2 --types edge --story-format raw --provider ollama --output edge_tests.feature --mode local
```

#### Generate Multiple Test Types (Local Mode)
```bash
python main.py generate-from-jira --ticket-id SJP-2 --types functional --types security --types edge --story-format raw --provider ollama --output all_tests.feature --mode local
```

#### Generate Playwright Code (Local Mode)
```bash
python main.py generate-from-jira --ticket-id SJP-2 --types functional --format playwright --provider ollama --output test_spec.js --mode local
```

### 2.5 Troubleshooting

#### Common Issues
1. **"Jira config not available"** - Use `--mode local` for testing
2. **"LLM parsing failed"** - Check if Ollama is running locally
3. **"Invalid test type"** - Use only supported test types (functional, security, api, ui, performance, accessibility, edge)

#### Check Ollama Status
```bash
curl http://localhost:11434/api/tags
```

#### Test with Local Mode
```bash
python main.py generate-from-jira --ticket-id TEST-123 --mode local --output test.feature
```

## 3. Output Files

Generated test cases are saved to the specified output file:
- `.feature` - Gherkin format
- `.js` - Playwright/Cypress code
- `.py` - Pytest code
- `.java` - JUnit code
- `.txt` - Human-readable format

## 4. Integration with CI/CD

The generated test cases can be integrated into your CI/CD pipeline:
1. Generate test cases as part of your build process
2. Commit generated test files to version control
3. Run tests using the appropriate test runner
4. Use the generated code skeletons as starting points for actual test implementation