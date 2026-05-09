import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
import json
import os
import certifi

load_dotenv()

JIRA_DOMAIN = os.getenv("JIRA_DOMAIN")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")

def extract_and_split_criteria(adf):
    full_text = extract_text_from_adf(adf) # Use your existing parser
    
    # Simple split logic
    marker = "Acceptance Criteria"
    if marker.lower() in full_text.lower():
        # Find the index regardless of case
        start_idx = full_text.lower().find(marker.lower())
        description_part = full_text[:start_idx].strip()
        criteria_part = full_text[start_idx + len(marker):].strip()
        return description_part, criteria_part
    
    return full_text, "None provided"

def extract_text_from_adf(adf):
    """Helper to pull plain text out of Jira's nested ADF format"""
    if not adf or 'content' not in adf:
        return ""
    text_blocks = []
    for node in adf['content']:
        if node.get('type') == 'paragraph' and 'content' in node:
            for part in node['content']:
                if part.get('type') == 'text':
                    text_blocks.append(part.get('text', ''))
                elif part.get('type') == 'mention':
                    text_blocks.append(part.get('attrs', {}).get('text', ''))
    return " ".join(text_blocks)

def get_full_jira_context(issue_key:str):
    base_url = f"https://{JIRA_DOMAIN}/rest/api/3/issue/{issue_key}"
    auth = HTTPBasicAuth(JIRA_EMAIL, JIRA_API_TOKEN)
    headers = {"Accept": "application/json"}

    try:
        issue_res = requests.get(base_url, headers=headers, auth=auth, verify=certifi.where())
        issue_res.raise_for_status()
        issue_details = issue_res.json()
        print(f"Issue details for {issue_key}:")
        # print(json.dumps(issue_details, indent=2))
        fields = issue_details.get('fields',{})
        summary = fields.get('summary','No summary found')
        desc, criteria = extract_and_split_criteria(fields.get('description'))
        status = fields.get('status', {}).get('name')
        priority = fields.get('priority', {}).get('name')
        comments = []
        for c in fields.get('comment', {}).get('comments', []):
            author = c['author']['displayName']
            body = extract_text_from_adf(c['body'])
            comments.append(f"{author}: {body}")
        context_for_ai = f"""
                    Jira Context for {issue_key}:
                    - Summary: {summary}
                    - Status: {status}
                    - Priority: {priority}
                    - Description: {desc}
                    - Acceptance Criteria: {criteria}
                    - Recent Discussions:
                    {chr(10).join(['  * ' + c for c in comments])}
                    """
        return context_for_ai
    except Exception as e:
        print(f"Error fetching issue details: {e}")

context = get_full_jira_context("SCRUM-5")
print(context)
