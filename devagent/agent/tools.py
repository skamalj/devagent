import os
import git
import requests
import base64
from typing import Dict
from langchain_core.tools import tool

@tool
def clone_repo(repo_url: str, local_path: str) -> git.Repo:
    """
    Clones a GitHub repository to the local system.
    
    Args:
        repo_url (str): URL of the GitHub repository.
        local_path (str): Local path to clone the repository.
    
    Returns:
        git.Repo: The cloned repository object.
    """
    if os.path.exists(local_path):
        repo = git.Repo(local_path)
        repo.remotes.origin.pull()
    else:
        repo = git.Repo.clone_from(repo_url, local_path)
    print("Repository cloned")
    return repo

@tool
def insert_function(file_path: str, function_code: str) -> None:
    """
    Inserts a function into a given Python file.
    
    Args:
        file_path (str): Path to the Python file.
        function_code (str): Code of the function to insert.
    """
    print("Adding tool to file")
    with open(file_path, 'a') as f:
        f.write('\n' + function_code + '\n')

@tool
def update_content_between_lines(file_path: str, start_line, end_line, new_content: str):
    """
    Replace content between the specified line numbers in a file.
    
    :param file_path: Path to the file.
    :param start_line: Line number (1-based) where replacement starts (inclusive).
    :param end_line: Line number (1-based) where replacement ends (inclusive).
    :param new_content: List of new lines to insert (each string should end with a newline character if needed).
    """
    print(f"Updating {new_content} to file {file_path}")
    with open(file_path, 'r') as file:
        lines = file.readlines()
    
    if start_line < 1 or end_line > len(lines) or start_line > end_line:
        raise ValueError("Invalid start or end line number.")
    
    # Replace the lines in the specified range
    lines[start_line - 1:end_line] = new_content
    
    with open(file_path, 'w') as file:
        file.writelines(lines)

@tool
def commit_and_push_changes(local_path: str, branch_name: str, commit_message: str) -> str:
    """
    Commits and pushes changes to a new branch.
    
    Args:
        local_path (str): Local repository path.
        branch_name (str): Name of the new branch.
        commit_message (str): Commit message.
    """
    repo = git.Repo(local_path)
    repo.git.checkout('-b', branch_name)
    repo.git.add(A=True)
    repo.git.commit('-m', commit_message)
    repo.git.push('--set-upstream', 'origin', branch_name)
    print("New tool created and pushed")
    return "Tool created and pushed"
    

@tool
def create_pull_request(repo_owner: str, repo_name: str, branch_name: str, base_branch: str, pr_title: str, pr_body: str) -> Dict:
    """
    Creates a pull request on GitHub.
    
    Args:
        repo_owner (str): GitHub repository owner.
        repo_name (str): Name of the repository.
        branch_name (str): Name of the new branch.
        base_branch (str): Base branch to merge into.
        pr_title (str): Title of the pull request.
        pr_body (str): Description of the pull request.
    
    Returns:
        Dict: JSON response from the GitHub API.
    """
    github_token = os.getenv("GITHUB_TOKEN")
    
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/pulls"
    headers = {"Authorization": f"token {github_token}", "Accept": "application/vnd.github.v3+json"}
    data = {"title": pr_title, "body": pr_body, "head": branch_name, "base": base_branch}
    response = requests.post(url, json=data, headers=headers)
    print("Pull Request Created")
    return response.json()

@tool
def read_azure_devops_user_story(story_id):
    """
    Retrieves the details of an Azure DevOps user story by its ID.

    :param story_id: The ID of the user story to fetch.
    :return: The JSON response containing the user story details.
    """
    
    az_token = os.getenv("AZ_DEVOPS_PAT")
    
    if not az_token:
        print("Failed to retrieve Azure DevOps PAT from environment variables.")
        return None
    
    auth_header = base64.b64encode(f"'':{az_token}".encode()).decode()
    
    # Azure DevOps API Call
    url = f"https://dev.azure.com/skamalj-org/agent-loki/_apis/wit/workitems/{story_id}?api-version=7.1"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Basic {auth_header}"
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        print("Story details fetched")
        return response.json()
    else:
        print(f"Failed to retrieve user story {story_id}: {response.text}")
        return None


tool_list = [read_azure_devops_user_story, clone_repo, update_content_between_lines, insert_function, clone_repo, commit_and_push_changes, create_pull_request]