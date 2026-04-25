from dotenv import load_dotenv
import os
import requests

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_URL = os.getenv("GITHUB_URL")

headers = {
    "Authorization" : f"Bearer {GITHUB_TOKEN}",
    "X-GitHub-Api-Version" : "2026-03-10"
}


def list_pr():
    headers["Accept"]="application/vnd.github+json"
    url = f"{GITHUB_URL}/{owner}/{repo}/pulls"
    pass

