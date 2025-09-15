#!/usr/bin/env python3
"""Fetch Jira Stories and Generate Test Cases with plain description - Fixed imports."""

import asyncio
import os
import sys
from pathlib import Path

# Add project root to Python path to fix import issues
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Now import with absolute paths
try:
    from TestCaseGenerator.integrations.jira_client import JiraClient
    from TestCaseGenerator.config.settings import get_jira_config, get_llm_config
    from TestCaseGenerator.generators.functional_test_generator import FunctionalTestGenerator
    from TestCaseGenerator.integrations.llm_client import LLMClient
    from TestCaseGenerator.formatters.gherkin_formatter import GherkinFormatter
    from TestCaseGenerator.models.input_models import TestCaseRequest, AcceptanceCriteria, TestSpecification
except ImportError as e:
    print(f"Import error: {e}")
    print("Some modules may be missing. Trying alternative approach...")
    sys.exit(1)

# Convert Jira rich-text (doc) to plain string
def jira_doc_to_text(doc):
    if not doc:
        return ""
    if isinstance(doc, str):
        return doc
    lines = []
    for block in doc.get("content", []):
        block_type = block.get("type")
        if block_type == "paragraph":
            paragraph_text = "".join(
                c.get("text", "") for c in block.get("content", []) if c.get("type") == "text"
            )
            lines.append(paragraph_text)
        elif block_type in ["orderedList", "bulletList"]:
            for li in block.get("content", []):
                for c in li.get("content", []):
                    if c.get("type") == "paragraph":
                        text = "".join(cc.get("text", "") for cc in c.get("content", []) if cc.get("type") == "text")
                        lines.append(f"- {text}")
    return "\n".join(lines)


async def fetch_and_generate_tests():
    print("🚀 Fetching Jira Stories and Generating Test Cases")
    print("=" * 60)

    # Check environment variables
    jira_username = os.getenv("JIRA_USERNAME")
    jira_token = os.getenv("JIRA_API_TOKEN")
    jira_url = os.getenv("JIRA_BASE_URL")
    
    if not jira_username or not jira_token:
        print("❌ Please set JIRA_USERNAME and JIRA_API_TOKEN environment variables")
        print("Available environment variables:")
        for key, value in os.environ.items():
            if key.startswith('JIRA'):
                print(f"  {key}={'*' * len(value) if value else 'NOT SET'}")
        
        print("\n🔄 Using dummy data instead...")
        use_dummy = True
    else:
        print(f"✅ Found Jira credentials for: {jira_username}")
        print(f"   Base URL: {jira_url}")
        use_dummy = False
        
        # Verify connection works before proceeding
        try:
            auth_str = f"{jira_username}:{jira_token}"
            headers = {
                "Authorization": "Basic " + base64.b64encode(auth_str.encode()).decode(),
                "Accept": "application/json"
            }
            async with httpx.AsyncClient(headers=headers) as session:
                test_url = f"{jira_url}/rest/api/3/issue/SJP-2"
                test_resp = await session.get(test_url)
                test_resp.raise_for_status()
        except Exception as e:
            print(f"❌ Jira connection test failed: {e}")
            print("🔄 Using dummy data instead...")
            use_dummy = True

    # Get configuration
    try:
        if not use_dummy:
            jira_config = get_jira_config()
            if not jira_config:
                print("❌ Jira configuration not found, switching to dummy mode")
                use_dummy = True
        
        if use_dummy:
            # Create a minimal jira config for dummy mode
            from config.settings import JiraConfig
            jira_config = JiraConfig(
                base_url="https://dummy.atlassian.net",
                username="dummy@example.com", 
                api_token="dummy_token"
            )
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return

    # Initialize Jira client
    try:
        jira_client = JiraClient(jira_config)
        print("✅ Jira client created")
    except Exception as e:
        print(f"❌ Failed to create Jira client: {e}")
        return

    tickets_to_fetch = ["SJP-2"]

    for ticket_id in tickets_to_fetch:
        print(f"\n📋 Fetching ticket: {ticket_id}")
        print("-" * 40)
        try:
            # Fetch the ticket (dummy or real)
            if use_dummy:
                print("📝 Using dummy ticket data...")
                ticket = jira_client.generate_dummy_ticket(ticket_id)
            else:
                ticket = await jira_client.fetch_ticket(ticket_id)

            # Convert description to string if needed
            if hasattr(ticket.issue, 'description'):
                if isinstance(ticket.issue.description, dict):
                    ticket.issue.description = jira_doc_to_text(ticket.issue.description)
                elif ticket.issue.description is None:
                    ticket.issue.description = ""

            print(f"✅ Ticket fetched: {ticket.issue.summary}")
            print(f"   Status: {ticket.issue.status['name']}")
            
            if hasattr(ticket.issue, 'assignee') and ticket.issue.assignee:
                assignee_name = ticket.issue.assignee.display_name if hasattr(ticket.issue.assignee, 'display_name') else str(ticket.issue.assignee)
                print(f"   Assignee: {assignee_name}")
            else:
                print(f"   Assignee: Unassigned")

            # Acceptance Criteria
            if hasattr(ticket, 'acceptance_criteria') and ticket.acceptance_criteria:
                print(f"   Acceptance Criteria: {len(ticket.acceptance_criteria)} items")
                for i, criteria in enumerate(ticket.acceptance_criteria[:3], 1):
                    print(f"     {i}. {criteria}")
                if len(ticket.acceptance_criteria) > 3:
                    print(f"     ... and {len(ticket.acceptance_criteria) - 3} more")
            else:
                print(f"   Acceptance Criteria: None found")

            # Generate test cases
            print(f"\n🧪 Generating test cases for {ticket_id}...")
            try:
                ollama_config = get_llm_config("ollama")
                if not ollama_config:
                    print("❌ Ollama configuration not found")
                    continue
                    
                llm_client = LLMClient(ollama_config)
                test_generator = FunctionalTestGenerator(llm_client)

                # Get acceptance criteria
                if hasattr(ticket, 'acceptance_criteria') and ticket.acceptance_criteria:
                    criteria_list = ticket.acceptance_criteria
                else:
                    # Fallback criteria
                    criteria_list = [
                        "Given a user accesses the system",
                        "When they perform the required action", 
                        "Then the system responds appropriately"
                    ]

                ac_type = ticket.get_acceptance_criteria_type() if hasattr(ticket, 'get_acceptance_criteria_type') else "gherkin"
                ac = AcceptanceCriteria(criteria_type=ac_type, criteria_list=criteria_list)

                spec = TestSpecification(
                    test_types=["functional"],
                    test_level="integration",
                    output_format="gherkin",
                    priority="high"
                )

                request = TestCaseRequest(
                    acceptance_criteria=ac,
                    test_specification=spec,
                    jira_ticket_id=ticket_id
                )

                test_cases = await test_generator.generate(request)
                print(f"✅ Generated {len(test_cases)} test cases")

                formatter = GherkinFormatter()
                formatted_output = formatter.format_test_cases(test_cases, request)

                filename = f"test_cases_{ticket_id}.feature"
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(formatted_output)

                print(f"💾 Test cases saved to: {filename}")
                print(f"\n📄 Preview of generated test cases:")
                print("-" * 40)
                for line in formatted_output.split("\n")[:20]:
                    print(line)
                if len(formatted_output.split("\n")) > 20:
                    print("... (truncated)")

            except Exception as e:
                print(f"❌ Error generating test cases: {e}")
                import traceback
                traceback.print_exc()

        except Exception as e:
            print(f"❌ Error processing {ticket_id}: {e}")
            import traceback
            traceback.print_exc()
            continue

    try:
        await jira_client.close()
    except:
        pass
        
    print("\n✅ Process completed!")


if __name__ == "__main__":
    # Ensure we're in the right directory
    os.chdir(Path(__file__).parent)
    asyncio.run(fetch_and_generate_tests())