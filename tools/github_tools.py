# import ssl
# print(ssl.OPENSSL_VERSION)
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
        prs = []
        for pr in pr_list:
            print(pr.get('number'))
            print(pr.get('state'))
            print(pr.get('title'))
            print(pr.get('user',{}).get('login'))
            reviewers = []
            for reviewer in pr.get('requested_reviewers',[]):
                reviewers.append(reviewer.get('login'))
            print(reviewers)
            print(pr.get('head').get('ref'))
            print(pr.get('head').get('repo').get('name'))
            # print(pr.get('_links',{}))
            print(pr.get('base').get('ref'))

        # print(json.dumps(pr_list, indent=2))
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
        title = pr_details.get('title','No title found')
        body = pr_details.get('body','No description found')
        labels = []
        for label in pr_details.get('labels',[]):
            
            labels.append({
                "name": label.get("name"),
                "description": label.get("description")
            })
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
        

def build_tree(github_tree_data):
    """
    Processes raw GitHub API 'tree' data and prints an ASCII representation.
    Each node stores its type (blob/tree) to handle empty folders correctly.
    """
    # 1. Build the nested dictionary with metadata
    # Structure: { "name": {"is_dir": bool, "children": {}} }
    root_nodes = {}

    for item in github_tree_data:
        path_parts = item['path'].split('/')
        current_level = root_nodes
        
        for i, part in enumerate(path_parts):
            is_last_part = (i == len(path_parts) - 1)
            
            if part not in current_level:
                # If it's the last part of the path, use the actual API type
                # Otherwise, it's an intermediate parent, so it must be a directory
                is_dir = True
                if is_last_part:
                    is_dir = (item['type'] == 'tree')
                
                current_level[part] = {
                    "is_dir": is_dir,
                    "children": {}
                }
            
            current_level = current_level[part]["children"]
    # 2. Recursive function to format and print
    lines = ["."]

    def walk(current_dict, prefix=""):
        # Sort so folders/files appear alphabetically
        items = sorted(current_dict.keys())
        
        for i, name in enumerate(items):
            node = current_dict[name]
            is_last = (i == len(items) - 1)
            
            # Visual logic
            connector = "└── " if is_last else "├── "
            display_name = f"{name}/" if node["is_dir"] else name
            lines.append(f"{prefix}{connector}{display_name}")
            
            # Prefix for the next level
            new_prefix = prefix + ("    " if is_last else "│   ")
            
            # Recurse into children
            walk(node["children"], new_prefix)

    walk(root_nodes)
    return "\n".join(lines)


def get_project_struct(owner:str,repo:str,branch:str):
    headers={
        "Accept":"application/vnd.github+json",
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "X-GitHub-Api-Version": "2026-03-10"
    }
    params={
        "recursive":1
    }
    url = f"{GITHUB_URL}/repos/{owner}/{repo}/git/trees/{branch}"

    try:
        response = requests.get(url,params=params,headers=headers,verify=certifi.where())
        response.raise_for_status()
        data = response.json()
        # print(json.dumps(data,indent=2))
        tree = data.get("tree",[])
        files = []
        for item in tree:
            path = item.get("path")
            type = item.get("type")
            files.append({"path":path,"type":type})
        tree_str = build_tree(files)
        print(f"Project Structure :{chr(10)}{tree_str}")
        return tree_str
    except Exception as e:
        print(f"Error : {e}")




if __name__ == "__main__":
    get_all_prs("PrinceMishra7", "CodeReviewr")
    # get_pr_details("PrinceMishra7", "CodeReviewr",1)
    # get_commits_in_pr("PrinceMishra7", "CodeReviewr",1)
    # get_pr_files("PrinceMishra7", "CodeReviewr",1)
    # get_content_of_file("PrinceMishra7", "CodeReviewr","tools/github_tools.py","github_tools")
    # get_readme("PrinceMishra7", "CodeReviewr")
    get_project_struct("PrinceMishra7","CodeReviewr","folder_struct")



