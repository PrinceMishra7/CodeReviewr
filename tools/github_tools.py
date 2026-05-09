# import ssl
# print(ssl.OPENSSL_VERSION)
# github_tools.py
from dotenv import load_dotenv
import os
import requests
import certifi
import json
import base64

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_URL = os.getenv("GITHUB_URL")


def get_decoded_content(encoded_content):
    print(f"type of encoded content : {type(encoded_content)}")
    decoded_bytes = base64.b64decode(encoded_content)
    return decoded_bytes.decode("utf-8")

def get_all_prs(owner:str, repo :str):
    headers = {
    "Authorization" : f"Bearer {GITHUB_TOKEN}",
    "X-GitHub-Api-Version" : "2026-03-10"
    }
    headers["Accept"]="application/vnd.github+json"
    url = f"{GITHUB_URL}/repos/{owner}/{repo}/pulls"
    try:
        response = requests.get(url,headers=headers,verify=certifi.where())
        response.raise_for_status()
        # print(response.json())
        pr_list = response.json()
        print(json.dumps(pr_list, indent=2))
    except Exception as e:
        print(f"Error : {e}")

def get_pr_details(owner:str, repo:str, pr_number:int):
    headers = {
    "Authorization" : f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version" : "2026-03-10"
    }
    url = f"{GITHUB_URL}/repos/{owner}/{repo}/pulls/{pr_number}"
    try:
        response = requests.get(url,headers=headers,verify=certifi.where())
        response.raise_for_status()
        pr_details = response.json()
        print(json.dumps(pr_details,indent=2))
    except Exception as e:
        print(f"Error : {e}")

def get_commits_in_pr(owner:str, repo:str,pr_number:int):
    headers = {
        "Authorization" : f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2026-03-10"
    }
    url = f"{GITHUB_URL}/repos/{owner}/{repo}/pulls/{pr_number}/commits"

    try:
        response = requests.get(url,headers=headers,verify=certifi.where())
        response.raise_for_status()
        commits = response.json()
        print(json.dumps(commits, indent=2))
    except Exception as e:
        print(f"Error : {e}")

def get_pr_files(owner:str, repo:str, pr_number:int):
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization" : f"Bearer {GITHUB_TOKEN}",
        "X-GitHub-Api-Version" : "2026-03-10"
    }

    url = f"{GITHUB_URL}/repos/{owner}/{repo}/pulls/{pr_number}/files"

    try:
        response = requests.get(url,headers=headers,verify=certifi.where())
        response.raise_for_status()
        files = response.json()
        print(json.dumps(files, indent=2))
    except Exception as e:
        print(f"Error : {e}")

def get_content_of_file(owner:str,repo:str,path:str = "",ref:str = None):
    headers = {
        "Accept": "application/vnd.github.object",
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "X-GitHub-Api-Version": "2026-03-10"
    }
    params={}
    if ref:
        params["ref"]=ref

    url = f"{GITHUB_URL}/repos/{owner}/{repo}/contents/{path}"

    try:
        response = requests.get(url,headers=headers,params=params,verify=certifi.where())
        response.raise_for_status()
        data = response.json()
        # print(json.dumps(data,indent=2))
        encoded_content = data.get("content","")

        file_content = get_decoded_content(encoded_content)
        print(f"file content : {file_content}")

    except Exception as e:
        print(f"Error: {e}")

def get_readme(owner:str,repo:str,ref:str=None):

    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "X-GitHub-Api-Version": "2026-03-10"
    }

    params={}
    if ref:
        params["ref"]=ref

    url =  f"{GITHUB_URL}/repos/{owner}/{repo}/readme"

    try:
        response = requests.get(url,params=params,headers=headers,verify=certifi.where())
        response.raise_for_status()
        data = response.json()
        encoded_content = data["content"]

        file_content = get_decoded_content(encoded_content)
        print(f"Readme :\n {file_content}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # get_all_prs("PrinceMishra7", "CodeReviewr")
    # get_pr_details("PrinceMishra7", "CodeReviewr",1)
    # get_commits_in_pr("PrinceMishra7", "CodeReviewr",1)
    # get_pr_files("PrinceMishra7", "CodeReviewr",1)
    # get_content_of_file("PrinceMishra7", "CodeReviewr","tools/github_tools.py","github_tools")
    get_readme("PrinceMishra7", "CodeReviewr")



