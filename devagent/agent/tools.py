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
    Commits and pushes changes to a  branch.
    
    Args:
        local_path (str): Local repository path.
        branch_name (str): Name of the working branch.
        commit_message (str): Commit message.
    """
    repo = git.Repo(local_path)

    user_name = os.getenv("GIT_USER_NAME", "DevAgent")
    user_email = os.getenv("GIT_USER_EMAIL", "bobncharlie@mail")

    with repo.config_writer() as config:
        config.set_value("user", "name", user_name)
        config.set_value("user", "email", user_email)

        # Fetch GitHub Token from Environment Variable
    github_token = os.getenv("GITHUB_TOKEN")
    if not github_token:
        raise ValueError("GitHub token is missing. Set the GITHUB_TOKEN environment variable.")

    # Update remote URL to use the token for authentication
    origin_url = repo.remotes.origin.url
    if "@" not in origin_url:  # Ensure we don't add multiple times
        new_origin_url = origin_url.replace("https://", f"https://{github_token}@")
        repo.remotes.origin.set_url(new_origin_url)

    repo.git.checkout(branch_name)
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

@tool
def create_new_branch(local_path: str, branch_name: str) -> str:
    """
    Creates a new Git branch and switches to it.

    Args:
        local_path (str): Local repository path.
        branch_name (str): Name of the new branch.

    Returns:
        str: Status message.
    """
    repo = git.Repo(local_path)

    # Fetch latest updates from remote
    repo.git.fetch()

    # Check if the branch already exists
    if branch_name in repo.heads:
        repo.git.checkout(branch_name)
        print(f"Switched to existing branch: {branch_name}")
        return f"Switched to existing branch: {branch_name}"
    else:
        repo.git.checkout('-b', branch_name)
        print(f"Created and switched to new branch: {branch_name}")
        return f"Created and switched to new branch: {branch_name}"

@tool
def read_file(file_path: str) -> str:
    """
    Reads and returns the content of a file.

    Args:
        file_path (str): Path to the file.

    Returns:
        str: The file's content.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()
    
    print(f"Read file: {file_path}")
    return content

tool_list = [ read_file, read_azure_devops_user_story, create_new_branch, update_content_between_lines, insert_function, clone_repo, commit_and_push_changes, create_pull_request]