# Test Case Generator Runbook

## 1. Environment Setup
   ### 1.1 Prerequisites
   - Python 3.11 or higher
   - Virtual Environment
   - Jira Account with API Access

   ### 1.2 Virtual Environment Setup
   ```bash
   cd /Users/aloktiwari/Documents/visual-studio-code-base/llama-base/AgenticLegoLand/TestCaseGenerator
   python -m venv py311-llm-venv
   source py311-llm-venv/bin/activate
   pip install -r requirements.txt

   ## 3. Running the Application
### 3.1 Test Jira Connection
```bash
python -m TestCaseGenerator.test_jira_simple
 ```

### 3.2 Generate Test Cases
```bash
python -m TestCaseGenerator.fetch_jira_tickets
 ```