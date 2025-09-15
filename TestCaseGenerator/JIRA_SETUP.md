# 🚀 Jira Integration Setup

## 📋 What We're Setting Up

- **Jira URL**: https://itsaihere.atlassian.net
- **Epic**: SJP-1 
- **User Story**: SJP-2
- **LLM Provider**: Ollama (llama3.2)

## 🔑 Step 1: Set Your Jira Credentials

### Option A: Environment Variables (Recommended)
```bash
# Set your Jira username (your email)
export JIRA_USERNAME='your_email@domain.com'

# Set your Jira API token
export JIRA_API_TOKEN='jiraapitoken'
```

### Option B: Create .env File
Create a `.env` file in the TestCaseGenerator directory:
```bash
JIRA_USERNAME=your_email@domain.com
JIRA_API_TOKEN=jiraapitoken
```

## 🧪 Step 2: Test the Connection

```bash
# Test if Jira connection works
python test_jira.py
```

You should see:
- ✅ Jira client created successfully
- ✅ All environment variables are set

## 📋 Step 3: Fetch Your Tickets

```bash
# Fetch SJP-1 (Epic) and SJP-2 (User Story) and generate test cases
python fetch_jira_tickets.py
```

This will:
1. Fetch both tickets from Jira
2. Extract acceptance criteria
3. Generate test cases using Ollama
4. Save them as `.feature` files

## 🔧 Step 4: Start Ollama

Make sure Ollama is running with llama3.2:
```bash
ollama run llama3.2
```

## 📁 Expected Output

After running `fetch_jira_tickets.py`, you'll get:
- `test_cases_SJP-1.feature` - Test cases for the Epic
- `test_cases_SJP-2.feature` - Test cases for the User Story

## 🚨 Troubleshooting

### "Jira client created successfully" but fetch fails
- Check if your API token has read permissions
- Verify the ticket IDs exist in your Jira instance

### "Ollama connection failed"
- Make sure Ollama is running: `ollama run llama3.2`
- Check if the model is downloaded

### "Environment variables not set"
- Make sure you've set both `JIRA_USERNAME` and `JIRA_API_TOKEN`
- Try creating a `.env` file instead

## 🎯 What Happens Next

1. **Test cases are generated** based on your Jira acceptance criteria
2. **Output is in Gherkin format** (Given-When-Then)
3. **Files are saved locally** for review and use
4. **You can modify the prompts** in the generator files if needed

## 🔄 Alternative: Use the Main CLI

You can also use the main CLI tool:
```bash
# Generate from specific Jira ticket
python main.py generate-from-jira --ticket-id SJP-2 --types functional --format gherkin --provider ollama
```

That's it! Your Jira integration is ready to go! 🎉
