import os
import git
import requests
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
    return repo

@tool
def insert_function(file_path: str, function_code: str) -> None:
    """
    Inserts a function into a given Python file.
    
    Args:
        file_path (str): Path to the Python file.
        function_code (str): Code of the function to insert.
    """
    with open(file_path, 'a') as f:
        f.write('\n' + function_code + '\n')

@tool
def commit_and_push_changes(local_path: str, branch_name: str, commit_message: str) -> None:
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

@tool
def create_pull_request(repo_owner: str, repo_name: str, branch_name: str, base_branch: str, pr_title: str, pr_body: str, github_token: str) -> Dict:
    """
    Creates a pull request on GitHub.
    
    Args:
        repo_owner (str): GitHub repository owner.
        repo_name (str): Name of the repository.
        branch_name (str): Name of the new branch.
        base_branch (str): Base branch to merge into.
        pr_title (str): Title of the pull request.
        pr_body (str): Description of the pull request.
        github_token (str): GitHub personal access token for authentication.
    
    Returns:
        Dict: JSON response from the GitHub API.
    """
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/pulls"
    headers = {"Authorization": f"token {github_token}", "Accept": "application/vnd.github.v3+json"}
    data = {"title": pr_title, "body": pr_body, "head": branch_name, "base": base_branch}
    response = requests.post(url, json=data, headers=headers)
    return response.json()
