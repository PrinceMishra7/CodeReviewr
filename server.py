from fastmcp import FastMCP
import os
from dotenv import load_dotenv
import logging
load_dotenv()
from typing import Literal, Optional
import tools.github_tools as git_tools
import tools.jira_tools as jira_tools

logging.basicConfig(level=os.getenv("LOG_LEVEL"))

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
MCP_HOST = os.getenv("MCP_HOST")
MCP_PORT = int(os.getenv("MCP_PORT"))

mcp = FastMCP("Code-Reviewer")


@mcp.tool()
def get_pull_request_context(owner: str, repo: str, pr_number: int) -> str:
    """
    Retrieves core metadata, operational statuses, structural stats, and description 
    for a specific GitHub Pull Request.

    CRITICAL RULES FOR THE AI AGENT:
    1. READ BEFORE ACTING: Use this tool first before generating or modifying code reviews. It provides 
       the target base/head branch mapping and structural details necessary to contextualize changes.
    2. STATE MONITORING: Check the 'Mergeable' status in the output report to see if the PR has 
       active merge conflicts (`dirty`) or is ready to merge (`clean`).
    3. CHANGELOG OVERVIEW: Review the 'Technical Stats' section (additions, deletions, files changed) 
       to calibrate the scale and scope of the code review before pulling individual files.

    Args:
        owner (str): The account owner of the repository (case-insensitive).
        repo (str): The name of the repository without the '.git' extension (case-insensitive).
        pr_number (int): The numeric ID identifying the target pull request.

    Returns:
        str: A comprehensive markdown report summarizing status, branches, assignees, reviewers, 
             technical scope metrics, and the author's primary PR body description.
    """
    return git_tools.get_pr_details(owner, repo, pr_number)

@mcp.tool()
def list_pull_requests(owner: str, repo: str) -> str:
    """
    Lists all active (open) Pull Requests for a specified repository along with their core metadata.

    CRITICAL RULES FOR THE AI AGENT:
    1. DISCOVERY PHASE: Use this tool when you need an entry point or birds-eye view of what ongoing 
       work exists in a repository before focusing down on a specific pull request ID.
    2. ITERATION BEHAVIOR: It processes the payload as an array list. Keep in mind that by default, 
       this endpoint fetches only open pull requests.
    3. SCOPING REVIEWS: Pay close attention to the 'Branch' configuration (`head` -> `base`) for each 
       PR entry to understand which feature branch is attempting to merge into which target environment branch.

    Args:
        owner (str): The account owner of the repository (case-insensitive).
        repo (str): The name of the repository without the '.git' extension (case-insensitive).

    Returns:
        str: A comprehensive markdown report aggregating all active pull requests, details on 
             assigned developers, designated reviewers, and descriptions for downstream processing.
    """
    return git_tools.get_all_prs(owner, repo)

@mcp.tool()
def get_repository_readme(owner:str, repo:str, ref:str = None) -> str:
    """
    Fetches and decodes the primary README file of a repository to extract global project context.

    CRITICAL RULES FOR THE AI AGENT:
    1. ARCHITECTURAL ALIGNMENT: Run this tool early when onboarding onto a new repository. The README 
    frequently details deployment steps, technology stacks, linting configurations, and coding conventions 
    that your review comments must adhere to.
    2. REF / BRANCH SCOPING: If analyzing changes specific to an unmerged feature branch, pass that branch 
    name to the 'ref' parameter to see if the developer updated the project documentation alongside their code.
    3. INLINE COMPLIANCE: Use the instructions found within the README body text to flag any implementation 
    patterns in the pull request that violate the project's stated contribution standards.

    Args:
        owner (str): The account owner of the repository (case-insensitive).
        repo (str): The name of the repository without the '.git' extension (case-insensitive).
        ref (str, optional): The name of the commit/branch/tag ref to target. Defaults to the default branch (usually 'main').

    Returns:
        str: A markdown report presenting structural metadata and the fully decoded text content of the README.
    """
    return git_tools.get_readme(owner, repo, ref)


@mcp.tool()
def get_file_tree(owner:str,repo:str,branch:str = "main") -> str:
    """
    Generates an ASCII directory tree representing the project's file structure on a specific branch.

    CRITICAL RULES FOR THE AI AGENT:
    1. REPO ORIENTATION: Use this tool immediately after discovering a repository to map out the codebase layout. 
    It helps you identify where source files, configuration settings, tests, and documentation live.
    2. TOKEN CONSERVATION: This tool automatically filters out high-noise environment folders (like node_modules, 
    .venv, and .git). Do not worry about running out of context window space from large baseline directory trees.
    3. CONTEXT REASONING: Use the visual tree to understand structural patterns (e.g., locating components vs utilities) 
    before utilizing file-fetching tools to pull specific file contents for code reviews.

    Args:
        owner (str): The account owner of the repository (case-insensitive).
        repo (str): The name of the repository without the '.git' extension (case-insensitive).
        branch (str, optional): The branch name to target for the tree snapshot. Defaults to "main".

    Returns:
        str: A text-based markdown report containing an ASCII directory tree visualization of the repository.
    """
    return git_tools.get_project_structure(owner,repo,branch)


@mcp.tool()
def get_commits_of_pr(owner:str,repo:str,pr_number:int) -> str:
    """
    Lists all commits associated with a specific pull request in a structured markdown table format.

    CRITICAL RULES FOR THE AI AGENT:
    1. REVIEW HISTORY: Use this tool to trace the evolutionary timeline of a pull request. Examining individual 
    commit messages helps you understand the developer's step-by-step logic and the intent behind major changes.
    2. SHA TRACKING: This tool provides full-length SHAs. Use these SHAs when you need to target a 
    specific point in the PR's history or cross-reference individual changes within your review feedback.
    3. CONTEXT EXTENSION: Reviewing the commit message log allows you to catch context that might be missing 
    from the high-level PR description, such as references to issue tickets, bug fixes, or mid-development refactors.

    Args:
        owner (str): The account owner of the repository (case-insensitive).
        repo (str): The name of the repository without the '.git' extension (case-insensitive).
        pr_number (int): The numeric ID identifying the target pull request.

    Returns:
        str: A markdown table displaying the SHA, author name, timestamp (YYYY-MM-DD), and commit message for each entry.
    """
    return git_tools.get_commits_in_pr(owner,repo,pr_number)


@mcp.tool()
def get_pr_code_changes(owner:str,repo:str,pr_number:int)->str:
    """
    Lists all files modified in a pull request and retrieves their unified diff patches.

    CRITICAL RULES FOR THE AI AGENT:
    1. CODE REVIEW CORE: Use this tool as your primary source of truth for the actual code modifications 
    needing review. It outputs both a summary of changes and the raw Git patch hunks.
    2. FILE TRACKING STATUS: Pay attention to the status of each file (e.g., 'modified', 'added', 'removed', 'renamed') 
    and its change density (+additions/-deletions) to structure your analytical priorities.
    3. INLINE LINE MATCHING: The `patch` string contains standard unified diff headers (e.g., @@ -line,count +line,count @@). 
    Carefully parse these hunk headers to pinpoint the exact destination line numbers (`line` and `side`) 
    before attempting to place automated review comments.

    Args:
        owner (str): The account owner of the repository (case-insensitive).
        repo (str): The name of the repository without the '.git' extension (case-insensitive).
        pr_number (int): The numeric ID identifying the target pull request.

    Returns:
        str: A comprehensive markdown report summarizing modified file names/statuses, followed by 
            individual syntax-highlighted diff text blocks for every file.
    """
    return git_tools.get_pr_files(owner,repo,pr_number)


@mcp.tool()
def get_file_content(owner:str,repo:str,path:str,ref:str=None)->str:
    """
    Fetches and decodes the full text content of a specific file from a repository at a designated branch or commit ref.

    CRITICAL RULES FOR THE AI AGENT:
    1. TARGETED INSPECTION: Use this tool when a pull request diff (`get_pr_files`) does not provide enough surrounding 
    context. It allows you to read an entire file to better understand global imports, helper functions, and class definitions.
    2. BRANCH SCOPING: Always match the 'ref' parameter to the target feature branch or specific commit SHA you are actively 
    reviewing to ensure you aren't accidentally reading outdated code from the default branch.
    3. LARGE FILE CAUTION: Be mindful of file sizes (`size` key in response metadata). Reading exceptionally large source 
    files (e.g., massive legacy modules or data configurations) can rapidly exhaust your available context window tokens.

    Args:
        owner (str): The account owner of the repository (case-insensitive).
        repo (str): The name of the repository without the '.git' extension (case-insensitive).
        path (str): The relative repository path to the target file (e.g., 'src/models/user.py').
        ref (str, optional): The name of the commit/branch/tag ref to fetch from. Defaults to the default branch (usually 'main').

    Returns:
        str: A markdown report indicating the file path, source reference, file size, and the fully decoded raw text contents.
    """
    return git_tools.get_content_of_file(owner,repo,path,ref)
    pass


@mcp.tool()
def get_jira_issue_detail(issue_key:str)->str:
    """
    Retrieves comprehensive tracking context, requirements, and user stories from a specific Jira issue ticket.

    CRITICAL RULES FOR THE AI AGENT:
    1. SPECIFICATION CROSS-REFERENCE: Use this tool to bridge business requirements with code implementations. 
    Compare the implementation details found in a pull request directly against the 'Description' and 
    'Acceptance Criteria' extracted from this ticket to verify completeness.
    2. SCOPING ALIGNMENT: Check the ticket's current 'Status' and 'Priority' to ensure the codebase modifications 
    align with the planned business sprint goals and deployment expectations.
    3. CONTEXTUAL AWARENESS: Review the 'Recent Discussions' section to catch edge cases, scope changes, or 
    architectural decisions agreed upon by engineering and product teams that may not be formally updated 
    in the core ticket description.

    Args:
        issue_key (str): The unique identifier for the Jira issue ticket (e.g., 'PROJ-123' or 'BUG-456').

    Returns:
        str: A structured text report compiling the issue summary, operational status, priority tier, 
            functional description, business acceptance criteria, and formatted comment threads.
    """
    return jira_tools.get_full_jira_context(issue_key)

@mcp.tool()
def put_review_comment_on_pr(
    owner: str,
    repo: str,
    pr_number: int,
    body: str,
    commit_id: Optional[str] = None,
    path: Optional[str] = None,
    line: Optional[int] = None,
    side: Optional[Literal["LEFT", "RIGHT"]] = "RIGHT",
    start_line: Optional[int] = None,
    start_side: Optional[Literal["LEFT", "RIGHT", "side"]] = None,
    in_reply_to: Optional[int] = None
) -> str:
    """
    Creates a review comment on the diff of a specified Pull Request.

    USAGE MODES — pick exactly one:

    1. REPLY TO EXISTING COMMENT:
       - Required: body, in_reply_to
       - All other parameters (commit_id, path, line, etc.) are ignored by GitHub.

    2. FILE-LEVEL COMMENT (no specific line):
       - Required: body, commit_id, path
       - Do NOT pass line, start_line, side, or start_side.

    3. SINGLE-LINE COMMENT:
       - Required: body, commit_id, path, line
       - Optional: side (default "RIGHT")
       - Do NOT pass start_line or start_side.

    4. MULTI-LINE COMMENT:
       - Required: body, commit_id, path, line, side, start_line, start_side
       - line = last line of the range; start_line = first line of the range.

    PARAMETER RULES:
    - commit_id: MUST be the full 40-character SHA (not abbreviated). Required for modes 2, 3, 4.
    - path: Relative file path (e.g., 'src/utils/helpers.py'). Required for modes 2, 3, 4.
    - side: LEFT = deleted lines (red). RIGHT = added or context lines (green/white). Defaults to RIGHT.
    - start_side: Can be LEFT, RIGHT, or "side". Required if start_line is provided.
    - in_reply_to: When set, GitHub ignores all parameters except body.
    - Do NOT pass subject_type — it conflicts with GitHub's request schema and will cause a 422 error.

    Args:
        owner (str): REQUIRED. Repository owner (case-insensitive).
        repo (str): REQUIRED. Repository name without '.git' (case-insensitive).
        pr_number (int): REQUIRED. The numeric PR ID.
        body (str): REQUIRED. Markdown text of the review comment.
        commit_id (str, optional): Full 40-char SHA of the commit. Required unless using in_reply_to.
        path (str, optional): Relative file path being commented on. Required unless using in_reply_to.
        line (int, optional): Last (or only) line of the comment range. Required for line-level comments.
        side (Literal["LEFT", "RIGHT"], optional): Diff side for the line. Defaults to "RIGHT".
        start_line (int, optional): First line for multi-line comments.
        start_side (Literal["LEFT", "RIGHT", "side"], optional): Diff side for start_line. Required if start_line is set.
        in_reply_to (int, optional): ID of comment to reply to. When set, all other params except body are ignored.

    Returns:
        str: Markdown-formatted confirmation or error diagnostics.
    """
    return git_tools.put_pr_review_comment(
        owner, repo, pr_number, body, commit_id, path,
        line, side, start_line, start_side, in_reply_to
    )
     

@mcp.tool()
def update_pull_request_review_comment(owner:str,repo:str,comment_id:str,body:str)->str:
    """
    Edits/Updates the markdown body text of an existing review comment on a pull request.
    
    CRITICAL RULES FOR THE AI AGENT:
    1. OWNERSHIP CHECK: This tool will automatically verify if the comment belongs to the AI before updating. You cannot edit comments left by human developers.
    2. OVERWRITE WARNING: Providing a new body will completely replace the old text of the comment. If you want to append information, you must read the comment first or construct a complete text.

    Args:
        owner (str): The account owner of the repository (case-insensitive).
        repo (str): The name of the repository without the '.git' extension (case-insensitive).
        comment_id (int): The unique identifier of the comment you wish to update.
        body (str): The new markdown text that will completely replace the existing comment body.

    Returns:
        str: A markdown-formatted report detailing the updated comment info, or an error log.
    """
    return git_tools.update_pull_request_review_comment(owner,repo,comment_id,body)


@mcp.tool()
def delete_pull_request_review_comment(owner:str,repo:str,comment_id:int)->str:
    """
    Deletes a specific review comment from a pull request diff or timeline.
    
    CRITICAL WARNING FOR THE AI AGENT:
    - DO NOT DELETE OTHER USERS' COMMENTS. 
    - This tool performs a destructive action without verification. Only execute this 
      command on a comment_id that you (the AI) explicitly generated or are authorized to manage.
    - Double-check the comment_id before execution to prevent data loss for human developers.

    Args:
        owner (str): The account owner of the repository (case-insensitive).
        repo (str): The name of the repository without the '.git' extension (case-insensitive).
        comment_id (int): The unique identifier of the comment to be permanently deleted.

    Returns:
        str: A markdown-formatted string confirming the deletion status.
    """
    return git_tools.delete_pull_request_review_comment(owner,repo,comment_id)

@mcp.tool()
def get_pull_request_review_comment(owner:str,repo:str,comment_id:str)->str:
    """
    Retrieves information and content for a specific review comment on a pull request.
    
    Args:
        owner (str): The account owner of the repository (case-insensitive).
        repo (str): The name of the repository without the '.git' extension (case-insensitive).
        comment_id (int): The unique identifier of the review comment to fetch.

    Returns:
        str: A markdown-formatted report containing the comment text, author, and location context.
    """
    return git_tools.get_pull_request_review_comment(owner,repo,comment_id)


@mcp.tool()
def list_pull_request_review_comments(
    owner:str,
    repo:str,
    pr_number:int,
    sort: Optional[Literal["created","updated"]] = "created",
    direction: Optional[Literal["asc","desc"]] = "asc",
    since: Optional[str] = None,
    per_page: Optional[int] = 30,
    page: int = 1
    ) ->str:
    """
    Lists all review comments for a specified pull request.
    
    Args:
        owner (str): The account owner of the repository (case-insensitive).
        repo (str): The name of the repository without the '.git' extension (case-insensitive).
        pr_number (int): The number that identifies the pull request.
        sort (Literal["created", "updated"]): The property to sort the results by. Defaults to "created".
        direction (Literal["asc", "desc"]): The direction to sort results. Ignored without 'sort'. Defaults to "asc".
        since (str, optional): Only show results last updated after this time (ISO 8601 format: YYYY-MM-DDTHH:MM:SSZ).
        per_page (int): The number of results per page (max 100). Defaults to 30.
        page (int): The page number of the results to fetch. Defaults to 1.

    Returns:
        str: A markdown-formatted summary list of all review comments found.
    """
    return git_tools.list_pull_request_review_comments(owner,repo,pr_number,sort,direction,since,per_page,page)



if __name__ == "__main__":
    mcp.run(transport="streamable-http",host=MCP_HOST,port=MCP_PORT,path="/code-reviewer",stateless_http=True)

# npx @modelcontextprotocol/inspector

