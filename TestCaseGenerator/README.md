# Test Case Generator Agent

A robust yet simple, extensible Python framework for generating high-quality software test cases using LLMs. It supports multiple providers (OpenAI, Ollama, custom), multiple test generators (functional, security, API, UI, performance, accessibility), multiple output formats (Gherkin, code skeletons, human-readable), and provides both a CLI and a REST API via FastAPI.

## Features
- Configurable LLM providers (OpenAI, Ollama, custom) with environment variables
- Retry, rate limiting, and async I/O for performance and reliability
- Jira integration with real API or dummy data fallback
- Multiple test generators: functional, security, API, UI, performance, accessibility
- Output formatters: Gherkin, code skeletons (Playwright, Pytest, Cypress, Selenium, JUnit), human-readable docs
- CLI and FastAPI REST API
- Dummy mode for testing without Jira access
- Well-structured code for reusing the pattern to build more agents

## Project Structure
```
testcase_generator/
├── config/
│   ├── __init__.py
│   ├── settings.py          # Configuration management
│   └── llm_config.yaml      # LLM endpoint configurations
├── models/
│   ├── __init__.py
│   ├── input_models.py      # Pydantic models for input data
│   ├── test_models.py       # Test case data models
│   └── jira_models.py       # Jira integration models
├── parsers/
│   ├── __init__.py
│   ├── acceptance_criteria_parser.py
│   ├── user_story_parser.py
│   └── system_context_parser.py
├── generators/
│   ├── __init__.py
│   ├── base_generator.py
│   ├── functional_test_generator.py
│   ├── edge_case_generator.py
│   └── security_test_generator.py
├── formatters/
│   ├── __init__.py
│   ├── gherkin_formatter.py
│   ├── code_skeleton_formatter.py
│   └── human_readable_formatter.py
├── integrations/
│   ├── __init__.py
│   ├── llm_client.py        # Configurable LLM integration
│   └── jira_client.py       # Jira REST API integration
├── main.py                  # CLI and FastAPI app
├── requirements.txt
└── README.md
```

Note: In your workspace this lives under `TestCaseGenerator/`.

## Requirements
Python 3.10+

Install dependencies:
```bash
pip install -r requirements.txt
```

Optionally create a virtualenv first.

## Configuration
Primary config lives in `config/llm_config.yaml`. Environment variables can override placeholders.

### Dummy Mode vs Real Jira Mode
The system supports two modes:

1. **Dummy Mode**: Uses synthetic data for development and testing without Jira access
2. **Real Jira Mode**: Uses real Jira API for production use

To use dummy mode, add the `--dummy` flag:
```bash
# Use dummy mode (no Jira API calls)
python main.py generate-from-jira --ticket-id SJP-2 --dummy --output test_cases.feature

# Use real Jira mode (requires Jira credentials)
python main.py generate-from-jira --ticket-id SJP-2 --output test_cases.feature
```

Example `config/llm_config.yaml`:
```yaml
llm_providers:
  openai:
    api_key: "${OPENAI_API_KEY}"
    base_url: "https://api.openai.com/v1"
    model: "gpt-4"
    temperature: 0.3
    max_tokens: 2000
  anthropic:
    api_key: "${ANTHROPIC_API_KEY}"
    base_url: "https://api.anthropic.com"
    model: "claude-3-sonnet-20240229"
    temperature: 0.3
    max_tokens: 2000
  ollama:
    api_key: ""
    base_url: "http://localhost:11434"
    model: "llama2"
  custom:
    api_key: "${CUSTOM_API_KEY}"
    base_url: "${CUSTOM_ENDPOINT}"
    model: "custom-model"

jira:
  base_url: "${JIRA_BASE_URL}"
  username: "${JIRA_USERNAME}"
  api_token: "${JIRA_API_TOKEN}"
```

Environment variables supported:
- OPENAI_API_KEY, ANTHROPIC_API_KEY, CUSTOM_API_KEY, CUSTOM_ENDPOINT
- JIRA_BASE_URL, JIRA_USERNAME, JIRA_API_TOKEN

## Running the API
Start the FastAPI server:
```bash
cd TestCaseGenerator
python main.py serve --host 0.0.0.0 --port 8000 --reload
```

Health check:
```bash
curl http://localhost:8000/health
```

List synthetic features:
```bash
curl http://localhost:8000/features
```

Get feature details:
```bash
curl http://localhost:8000/features/SE-001
```

Generate via API:
```bash
curl -X POST http://localhost:8000/generate \
  -H 'Content-Type: application/json' \
  -d '{
    "acceptance_criteria": {
      "criteria_type": "given-when-then",
      "criteria_list": [
        "Given a user is logged in, When they click logout, Then they are logged out"
      ]
    },
    "user_story": {
      "persona": "As a registered user",
      "action": "I want to log out",
      "value": "So that my session is secure"
    },
    "test_specification": {
      "test_types": ["functional", "security"],
      "test_level": "integration",
      "output_format": "gherkin",
      "priority": "high"
    },
    "provider": "openai"
  }'
```

## Local Mode with Synthetic Data
When running in local mode, the system uses synthetic data for Schneider Electric's EcoStruxure™ platform features.

### Demo and Exploration
```bash
# Run the demo to see available features
python demo_local_mode.py

# List all synthetic features
python main.py list-features

# Get details about a specific feature
python main.py generate-from-feature SE-001 --format gherkin
```

### Available Synthetic Features
- **SE-001**: Real-Time Energy Consumption Dashboard
- **SE-002**: Predictive Maintenance Alerts  
- **SE-003**: Energy Efficiency Analytics

Each feature includes:
- Complete user stories with acceptance criteria
- System context (tech stack, data types, constraints)
- Given/When/Then scenarios
- Company-specific domain knowledge

## Using the CLI
From `TestCaseGenerator/`:

Generate from inline inputs:
```bash
python main.py generate \
  --criteria-type given-when-then \
  --criteria "Given a user is logged in, When they click logout, Then they are logged out" \
  --persona "As a registered user" \
  --action "I want to log out" \
  --value "So that my session is secure" \
  --types functional --types security \
  --level integration \
  --format gherkin \
  --priority high \
  --provider openai
```

Generate from Jira (real or dummy):
```bash
# With dummy data (recommended for testing)
python main.py generate-from-jira \
  --ticket-id SJP-2 \
  --types functional --level integration \
  --format gherkin \
  --provider ollama \
  --dummy \
  --output test_cases.feature

# With real Jira (requires credentials)
python main.py generate-from-jira \
  --ticket-id SJP-2 \
  --types functional --level integration \
  --format gherkin \
  --provider ollama \
  --output test_cases.feature
```

Generate from synthetic features (local mode):
```bash
# List available features
python main.py list-features

# Generate from specific feature
python main.py generate-from-feature SE-001 \
  --types functional --types security \
  --level integration \
  --format gherkin \
  --provider ollama
```

Write formatted output to a file:
```bash
python main.py generate ... --output out.feature
```

## Architecture Overview
- `integrations/llm_client.py`: Unified LLM client with providers (OpenAI, Anthropic, Ollama, custom), retries, and prompts.
- `integrations/jira_client.py`: Async Jira client with caching and dummy fallback.
- `generators/`: Base and specific generators. Extend by adding a new generator and wiring it in `_build_generators`.
- `formatters/`: Render test cases as Gherkin, code skeletons, or human docs. Extend by adding a new formatter and branching in `_get_formatter`.
- `parsers/`: Extract structure from acceptance criteria, user stories, and system context.
- `models/`: Strongly-typed Pydantic models for inputs and outputs.

## Extending the Framework
- Add a new LLM provider: implement a `LLMProvider` subclass and hook into `LLMClient._create_provider`.
- Add a new generator: create file under `generators/` and add to `_build_generators` in `main.py`.
- Add a new formatter: create under `formatters/` and add a branch in `_get_formatter`.
- Add new integrations (e.g., TestRail): create under `integrations/` and use in CLI/API.

## Development
Run unit tests (skeleton):
```bash
pytest -q
```

Linting is not enforced here, but the code follows Pydantic v2 and async httpx patterns.

## Notes
- Ensure the appropriate provider API keys are set. If no valid provider is configured, generation will fail.
- For Ollama, run an Ollama server locally and ensure the model exists.
- Jira integration requires valid Jira Cloud credentials unless `--dummy` is used.
- **Supported test types**: functional, security, api, ui, performance, accessibility
- **Note**: Edge case generator exists but is not currently integrated due to model validation constraints
