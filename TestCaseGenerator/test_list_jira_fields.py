#!/usr/bin/env python3
"""List all Jira fields to find the Epic Link custom field."""

import asyncio
import aiohttp
import base64
from dotenv import load_dotenv
import os

load_dotenv()

async def list_fields():
    email = os.getenv("JIRA_EMAIL")
    token = os.getenv("JIRA_API_TOKEN")
    base_url = os.getenv("JIRA_BASE_URL")

    auth_str = f"{email}:{token}"
    auth_bytes = base64.b64encode(auth_str.encode("utf-8")).decode("utf-8")
    headers = {
        "Authorization": f"Basic {auth_bytes}",
        "Accept": "application/json"
    }

    async with aiohttp.ClientSession(headers=headers) as session:
        url = f"{base_url}/rest/api/3/field"
        async with session.get(url) as resp:
            data = await resp.json()
            for f in data:
                print(f"{f['id']}: {f['name']}")

asyncio.run(list_fields())