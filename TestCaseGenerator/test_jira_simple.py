#!/usr/bin/env python3
import asyncio
import aiohttp
import base64
import os
from dotenv import load_dotenv

# Load .env variables
load_dotenv()

JIRA_USERNAME = os.getenv("JIRA_USERNAME")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
JIRA_BASE_URL = os.getenv("JIRA_BASE_URL")
EPIC_FIELD_ID = "customfield_10014"  # Replace with your “Epic Link” custom field ID

async def fetch_story(story_key: str, epic_key: str):
    auth_str = f"{JIRA_USERNAME}:{JIRA_API_TOKEN}"
    headers = {
        "Authorization": "Basic " + base64.b64encode(auth_str.encode()).decode(),
        "Accept": "application/json"
    }

    async with aiohttp.ClientSession(headers=headers) as session:
        url = f"{JIRA_BASE_URL}/rest/api/3/issue/{story_key}"
        async with session.get(url) as resp:
            if resp.status != 200:
                text = await resp.text()
                raise Exception(f"Failed to fetch {story_key}: {resp.status} {text}")

            issue = await resp.json()
            fields = issue["fields"]

            # Get Epic Link custom field
            epic_value = fields.get(EPIC_FIELD_ID)
            if epic_value != epic_key:
                print(f"Story {story_key} is NOT under Epic {epic_key}")
                return

            # Safe assignee check
            assignee_field = fields.get("assignee")
            assignee = assignee_field.get("displayName") if assignee_field else "Unassigned"

            summary = fields.get("summary", "No summary")
            status = fields.get("status", {}).get("name", "Unknown")

            print(f"{story_key} | {summary} | Status: {status} | Assignee: {assignee} | Epic: {epic_key}")

if __name__ == "__main__":
    # Replace with your story and epic keys
    asyncio.run(fetch_story("SJP-2", "SJP-1"))