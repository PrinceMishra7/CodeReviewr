# import ssl
# print(ssl.OPENSSL_VERSION)
from dotenv import load_dotenv
import os
import requests
import certifi
import json
import base64
from typing import Literal, Optional

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_URL = os.getenv("GITHUB_URL")


def get_decoded_content(encoded_content):
    decoded_bytes = base64.b64decode(encoded_content)
    return decoded_bytes.decode("utf-8")

def get_all_prs(owner: str, repo: str):
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "X-GitHub-Api-Version": "2026-03-10",
        "Accept": "application/vnd.github+json"
    }
    url = f"{GITHUB_URL}/repos/{owner}/{repo}/pulls"
    
    try:
        response = requests.get(url, headers=headers, verify=certifi.where())
        response.raise_for_status()
        pr_list = response.json()

        with open('github_prs.json', 'w', encoding='utf-8') as f:
            json.dump(pr_list, f, indent=2, ensure_ascii=False)

        if not pr_list:
            return "No active Pull Requests found."

        llm_output = [f"# Active Pull Requests in {owner}/{repo}\n"]
        
        for pr in pr_list:
            reviewers = [r.get('login') for r in pr.get('requested_reviewers', [])]
            assignees = [a.get('login') for a in pr.get('assignees', [])]
            
            pr_block = (
                f"## PR #{pr.get('number')}: {pr.get('title')}\n"
                f"- **State**: {pr.get('state')}\n"
                f"- **Creator**: {pr.get('user', {}).get('login')}\n"
                f"- **Branch**: `{pr.get('head').get('ref')}` -> `{pr.get('base').get('ref')}`\n"
                f"- **Assignees**: {', '.join(assignees) if assignees else 'None'}\n"
                f"- **Reviewers**: {', '.join(reviewers) if reviewers else 'None'}\n"
                f"- **Description**: {pr.get('body') or 'No description provided.'}\n"
                f"- **Link**: {pr.get('html_url')}\n"
            )
            llm_output.append(pr_block)

        return "\n---\n".join(llm_output)

    except requests.exceptions.RequestException as e:
        return f"Error fetching PRs from GitHub: {str(e)}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"


def get_pr_details(owner: str, repo: str, pr_number: int):
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2026-03-10"
    }
    url = f"{GITHUB_URL}/repos/{owner}/{repo}/pulls/{pr_number}"
    
    try:
        response = requests.get(url, headers=headers, verify=certifi.where())
        response.raise_for_status()
        pr = response.json()

        # Log locally for your own debugging
        with open(f'pr_{pr_number}_details.json', 'w', encoding='utf-8') as f:
            json.dump(pr, f, indent=2, ensure_ascii=False)

        # Extraction logic
        reviewers = [r.get('login') for r in pr.get('requested_reviewers', [])]
        assignees = [a.get('login') for a in pr.get('assignees', [])]
        
        # Format a clean string for the LLM context
        # This structure allows the AI to quickly compare intent (body) with scale (stats)
        report = [
            f"# Pull Request Details: {pr.get('title')} (#{pr.get('number')})",
            f"- **Status**: {pr.get('state')} | **Mergeable**: {pr.get('mergeable_state')}",
            f"- **Author**: {pr.get('user', {}).get('login')}",
            f"- **Branch**: `{pr.get('head', {}).get('ref')}` -> `{pr.get('base', {}).get('ref')}`",
            f"- **Assignees**: {', '.join(assignees) if assignees else 'None'}",
            f"- **Reviewers**: {', '.join(reviewers) if reviewers else 'None'}",
            f"\n## Technical Stats",
            f"- **Files Changed**: {pr.get('changed_files')}",
            f"- **Commits**: {pr.get('commits')}",
            f"- **Line Changes**: +{pr.get('additions')} / -{pr.get('deletions')}",
            f"\n## Description",
            f"{pr.get('body') or 'No description provided.'}",
            f"\n## Links",
            f"- [View PR on GitHub]({pr.get('html_url')})",
            f"- [Raw Diff]({pr.get('diff_url')})"
        ]

        return "\n".join(report)

    except requests.exceptions.RequestException as e:
        return f"Error fetching PR #{pr_number}: {str(e)}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"
    


    
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
        commit_list = response.json()
        # Log locally for your own debugging
        with open(f'commits.json', 'w', encoding='utf-8') as f:
            json.dump(commit_list, f, indent=2, ensure_ascii=False)
        # print(json.dumps(commits, indent=2))
        commit_details = ["| SHA | Author | Date | Message |", "| :--- | :--- | :--- | :--- |"]
        
        for commit in commit_list:
            date = commit.get("commit", {}).get("author", {}).get("date").split('T')[0]
            message = commit.get('commit',{}).get('message').replace("\n"," ")
            author = commit.get('commit',{}).get('author').get('name')
            sha = commit.get('sha')[:7]
            commit_detail = f"| `{sha}` | {author} | {date} | {message} |"
            commit_details.append(commit_detail)  
        
        return "\n".join(commit_details)
    
    except requests.exceptions.RequestException as e:
        return f"Error fetching Commits for PR:#{pr_number}: {str(e)}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"



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
        file_list = response.json()
        with open(f'pr_files.json', 'w', encoding='utf-8') as f:
            json.dump(file_list, f, indent=2, ensure_ascii=False)
        # print(json.dumps(files, indent=2))
        files_detail = []
        summary = [f"# Files changed in PR #{pr_number}."]
        for file in file_list:
            summary.append(f"- `{file.get('filename')}` ({file.get('status')}) : +{file.get('additions')} / -{file.get('deletions')}")
        
        summary.append("\n## Detailed Code Diff\n")

        for file in file_list:
            patch = file.get('patch')
            summary.append(f"### File : `{file.get('filename')}`")
            summary.append(f"```diff\n{patch}\n```\n")

        return "\n".join(summary)

    except requests.exceptions.RequestException as e:
        return f"Error fetching PR files for PR:#{pr_number}: {str(e)}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"



def get_content_of_file(owner:str,repo:str,path:str,ref:str = None):
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
        # with open(f'file_content.json', 'w', encoding='utf-8') as f:
        #     json.dump(data, f, indent=2, ensure_ascii=False)
        encoded_content = data.get("content","")
        file_content = get_decoded_content(encoded_content)
        print(f"file content : {file_content}")

        report = [
            f"## File: {path}",
            f"**Version/Ref**: `{ref if ref else 'main'}`",
            f"**Size**: {data.get('size')} bytes",
            f"\n```{file_content}```\n"
        ]

        return "\n".join(report)

    except requests.exceptions.RequestException as e:
        return f"Error fetching File #{path}: {str(e)}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"



def get_readme(owner: str, repo: str, ref: str = None):
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "X-GitHub-Api-Version": "2026-03-10"
    }

    params = {}
    if ref:
        params["ref"] = ref

    url = f"{GITHUB_URL}/repos/{owner}/{repo}/readme"

    try:
        response = requests.get(url, params=params, headers=headers, verify=certifi.where())
        response.raise_for_status()
        data = response.json()
        
        # GitHub returns Readme content in Base64
        encoded_content = data.get("content", "")
        # Decode Base64 to bytes, then decode bytes to a UTF-8 string
        file_content = get_decoded_content(encoded_content)
        # Formatting for LLM visibility
        report = [
            f"# README for {owner}/{repo}",
            f"- **Source Branch/Ref**: {ref if ref else 'main'}",
            f"- **Format**: {data.get('encoding')}",
            f"\n--- CONTENT ---\n",
            file_content
        ]

        return "\n".join(report)

    except requests.exceptions.RequestException as e:
        return f"Error fetching README: {str(e)}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"
        



def build_tree(github_tree_data):
    """
    Processes raw GitHub API 'tree' data and returns an ASCII representation.
    """
    root_nodes = {}
    
    # Common directories to ignore to save LLM context/tokens
    ignore_list = {'.git', 'node_modules', '__pycache__', '.venv', '.idea', '.vscode'}

    for item in github_tree_data:
        path_parts = item['path'].split('/')
        # Skip items in ignored directories
        if any(part in ignore_list for part in path_parts):
            continue
            
        current_level = root_nodes
        for i, part in enumerate(path_parts):
            is_last_part = (i == len(path_parts) - 1)
            if part not in current_level:
                is_dir = True
                if is_last_part:
                    is_dir = (item['type'] == 'tree')
                
                current_level[part] = {
                    "is_dir": is_dir,
                    "children": {}
                }
            current_level = current_level[part]["children"]

    lines = ["."]
    def walk(current_dict, prefix=""):
        items = sorted(current_dict.keys())
        for i, name in enumerate(items):
            node = current_dict[name]
            is_last = (i == len(items) - 1)
            connector = "└── " if is_last else "├── "
            display_name = f"{name}/" if node["is_dir"] else name
            lines.append(f"{prefix}{connector}{display_name}")
            new_prefix = prefix + ("    " if is_last else "│   ")
            walk(node["children"], new_prefix)

    walk(root_nodes)
    return "\n".join(lines)


def get_project_structure(owner: str, repo: str, branch: str = "main"):
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "X-GitHub-Api-Version": "2026-03-10"
    }
    params = {"recursive": 1}
    url = f"{GITHUB_URL}/repos/{owner}/{repo}/git/trees/{branch}"

    try:
        response = requests.get(url, params=params, headers=headers, verify=certifi.where())
        response.raise_for_status()
        
        tree_data = response.json().get("tree", [])
        if not tree_data:
            return f"No files found for branch '{branch}'."

        formatted_tree = build_tree(tree_data)
        
        return f"## Project Structure for {owner}/{repo} ({branch})\n```\n{formatted_tree}\n```"

    except requests.exceptions.RequestException as e:
        return f"Error fetching project structure: {str(e)}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"




def put_pr_review_comment(
        owner:str,
        repo:str,
        pr_number:int,
        body:str,
        commit_id:str,
        path:str,
        subject_type: Literal["file","line"] = "line",
        line:Optional[int] = None,
        side:Optional[Literal["LEFT","RIGHT"]] = "RIGHT",
        start_line:Optional[int] = None,
        start_side:Optional[Literal["LEFT","RIGHT"]] = None,
        in_reply_to:Optional[int] = None
        )->str:

    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "X-GitHub-Api-Version": "2026-03-10"
    }

    payload = {
        "body":body
    }

    if in_reply_to is not None:
        payload["in_reply_to"] = in_reply_to
    else:
        payload.update({
            "commit_id" : commit_id,
            "path":path,
            "subject_type": subject_type
        })

        if subject_type == "line":
            if line is None:
                return "## Error: 'line' parameter is required when subject_type is 'line' ."
            payload["line"] = line
            payload["side"] = side
        
        if start_line is not None:
            if start_side is None:
                return "## Error: 'start_side' must be provided if 'start_line' is defined for multi-line targets."
            payload["start_line"] = start_line
            payload["start_side"] = start_side

    url = f"{GITHUB_URL}/repos/{owner}/{repo}/pulls/{pr_number}/comments"
    
    try:
        response = requests.post(url,headers=headers,json=payload,verify=certifi.where())
        response.raise_for_status()
        data = response.json()
        # Extracting variables accurately from the top-level keys of your sample payload
        comment_id = data.get("id")
        html_url = data.get("html_url")
        path = data.get("path")
        line = data.get("line")
        reply_to_id = data.get("in_reply_to_id")  # In response, it uses 'in_reply_to_id'

        # Build a robust response markdown report based on what actually came back
        report = ["## PR Review Comment Posted Successfully"]
        report.append(f"**Comment ID**: `{comment_id}`")
        
        if reply_to_id:
            report.append(f"**Context**: Thread reply to Comment ID `{reply_to_id}`")
        else:
            report.append(f"**File**: `{path}` (Line {line})")
            
        if html_url:
            report.append(f"**Link**: [View Comment on GitHub]({html_url})")

        return "\n".join(report)
    except requests.exceptions.HTTPError as http_err:
        # Safely extract GitHub's custom validation messages if they exist
        error_details = ""
        try:
            error_details = f"\nGitHub API Message: {http_err.response.json().get('message')}"
        except Exception:
            pass
        return f"HTTP error occurred while creating comment: {http_err}{error_details}"


def update_pull_request_review_comment(owner:str,repo:str,comment_id:str,body:str)->str:
    headers = {
        "Accept": "application/vnd.github+json",
        "authorization": f"Bearer {GITHUB_TOKEN}",
        "X-GitHub-Api-Version": "2026-03-10"
    }

    url = f"{GITHUB_URL}/repos/{owner}/{repo}/pulls/comments/{comment_id}"

    payload = {
        "body":body
    }

    try:
        response = requests.patch(url,headers=headers,json=payload,verify=certifi.where())
        response.raise_for_status()
        data = response.json()
        html_url = data.get("html_url")
        path = data.get("path")
        line = data.get("line")
        report = [
            "## PR Review Comment Updated Successfully",
            f"**Comment ID**: `{comment_id}`"
        ]

        if path:
            # If it's a line comment, include the line number. If it's a file comment, just show the path.
            location = f"`{path}` (Line {line})" if line else f"`{path}` (File-level)"
            report.append(f"**File Context**: {location}")
        else:
            report.append("**Context**: Thread reply comment")

        if html_url:
            report.append(f"**Link**: [View Updated Comment on GitHub]({html_url})")
        

        return "\n".join(report)

    except requests.exceptions.HTTPError as http_err:
        error_details = ""
        try:
            error_details = f"\nGitHub API Message: {http_err.response.json().get('message')}"
        except Exception:
            pass
        return f"HTTP error occurred while updating comment {comment_id}: {http_err}{error_details}"
    except Exception as err:
        return f"An unexpected error occurred: {err}"


def delete_pull_request_review_comment(owner:str,repo:str,comment_id:int)->str:
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization":f"Bearer {GITHUB_TOKEN}",
        "X-GitHub-Api-Version": "2026-03-10"
        }
    
    url = f"{GITHUB_URL}/repos/{owner}/{repo}/pulls/comments/{comment_id}"
    try:
        response = requests.delete(url,headers=headers,verify=certifi.where())
        response.raise_for_status()
        report = [
            "## PR Review Comment Deleted Successfully",
            f"**Repository**: `{owner}/{repo}`",
            f"**Comment ID**: `{comment_id}`",
            "**Status Code**: `204 No Content` (The resource was successfully removed from GitHub)."
        ]
        return "\n".join(report)

    except requests.exceptions.HTTPError as http_err:
        error_msg = f"HTTP error occurred while trying to delete comment {comment_id}: {http_err}"
        if http_err.response.status_code == 404:
            error_msg += "\n*Note: The comment may have already been deleted or the ID is incorrect.*"
        return error_msg
    except Exception as err:
        return f"An unexpected error occurred while trying to delete comment {comment_id}: {err}"


def get_pull_request_review_comment(owner:str,repo:str,comment_id:str)->str:
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "X-GitHub-Api-Version": "2026-03-10"
    }

    url = f"{GITHUB_URL}/repos/{owner}/{repo}/pulls/comments/{comment_id}"

    try:
        response = requests.get(url, headers=headers, verify=certifi.where())
        response.raise_for_status()
        data = response.json()
        author_login = data.get("user", {}).get("login", "Unknown")
        body_content = data.get("body", "")
        html_url = data.get("html_url")
        path = data.get("path")
        line = data.get("line")
        reply_to_id = data.get("in_reply_to_id")
        report = [
            f"## Details for PR Review Comment #{comment_id}",
            f"**Author**: `{author_login}`"
        ]
        if path:
            location = f"`{path}` (Line {line})" if line else f"`{path}` (File-level)"
            report.append(f"**Location**: {location}")
            
        if reply_to_id:
            report.append(f"**Thread Context**: In reply to Comment ID `{reply_to_id}`")
            
        if html_url:
            report.append(f"**Link**: [View Comment on GitHub]({html_url})")
            
        report.append(f"\n### Comment Body:\n> {body_content}\n")

        return "\n".join(report)
    except requests.exceptions.HTTPError as http_err:
        error_msg = f"HTTP error occurred while fetching comment {comment_id}: {http_err}"
        if http_err.response.status_code == 404:
            error_msg += "\n*Note: The resource could not be found. Verify that the comment_id, owner, and repo parameters are correct.*"
        return error_msg
    except Exception as err:
        return f"An unexpected error occurred while fetching comment {comment_id}: {err}"



def list_pull_request_review_comments(owner:str,repo:str,pr_number:int,sort:Optional[Literal["created", "updated"]] = "created",
                    direction: Optional[Literal["asc", "desc"]] = "asc",since: Optional[str] = None,
                    per_page: int = 30,page: int = 1)->str:
    
    headers = {
        "Accept" : "application/vnd.github+json",
        "Authorization" : f"Bearer {GITHUB_TOKEN}",
        "X-GitHub-Api-Version" : "2026-03-10"
    }

    params = {
        "sort":sort,
        "direction":direction,
        "per_page":page,
        "page":page
    }

    if since:
        params["since"]=since
    
    url = f"{GITHUB_URL}/repos/{owner}/{repo}/pulls/{pr_number}/comments"

    try:
        response = requests.get(url,headers=headers,params=params,verify=certifi.where())
        response.raise_for_status()

        comments_list = response.json()

        if not comments_list:
            return f"## PR #{pr_number} Review Comments\nNo review comments found on this pull request."
        
        report = [
            f"## Review Comments Found on PR #{pr_number}",
            f"Showing {len(comments_list)} comment(s) (Page {page}, Sorted by {sort} {direction.upper()}).",
            "---"
        ]

        for comment in comments_list:
            comment_id = comment.get("id")
            author_login = comment.get("user",{}).get("login","Unknown")
            path = comment.get("path","Unknown file")
            line = comment.get("line")
            body = comment.get("body","")
            reply_to_id = comment.get("in_reply_to_id")

            location = f"Line {line}" if line else "File-level/General"
            context_string = f"**File**: `{path}` ({location})"

            if reply_to_id:
                context_string += f" | *Reply to Comment ID `{reply_to_id}`*"
            
            comment_entry = (
                f"### Comment ID: `{comment_id}` | Author: `{author_login}`\n"
                f"{context_string}\n"
                f"> {body}\n"
            )
            report.append(comment_entry)
        
        return "\n".join(report)

    except requests.exceptions.HTTPError as http_err:
        return f"HTTP error occurred while listing review comments: {http_err}"
    except Exception as err:
        return f"An unexpected error occurred: {err}"    


if __name__ == "__main__":
    # get_all_prs("PrinceMishra7", "CodeReviewr")
    # get_pr_details("PrinceMishra7", "CodeReviewr",3)
    # commits = get_commits_in_pr("PrinceMishra7", "CodeReviewr",3)
    # get_pr_files("PrinceMishra7", "CodeReviewr",3)
    result = get_content_of_file("PrinceMishra7", "CodeReviewr","tools/jira_tools.py","main")
    print(result)
    # get_readme("PrinceMishra7", "CodeReviewr")
    # get_project_struct("PrinceMishra7","CodeReviewr","folder_struct")



