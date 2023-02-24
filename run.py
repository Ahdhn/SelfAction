import os
import stat
import time
import shutil
from github import Github

def remove_readonly(func, path, _):
    "Clear the readonly bit and reattempt the removal"
    os.chmod(path, stat.S_IWRITE)
    func(path)


# Set up Github API credentials
g = Github()

# Set up repository information
repo_owner = "Ahdhn"
repo_name = "CUDATemplate"
repo_branch = "master"

# Set up clone path
clone_path = "./build"

# Set up delay time in seconds between checks
delay = 5

# Initialize last commit SHA to None
last_commit_shas = {}

while True:
    # Get the repository object
    repo = g.get_repo(f"{repo_owner}/{repo_name}")

    # Get the list of all branches and pull requests
    branches = [branch for branch in repo.get_branches()]
    pull_requests = [pr for pr in repo.get_pulls(state='all', sort='updated', base='master')]

    # Iterate over all branches and pull requests
    for branch in branches + pull_requests:
        branch_name = branch.name

        # Get the latest commit SHA for the branch
        commit_sha = branch.commit.sha

        # If the latest commit SHA is different from the previous one, clone and build the updated code
        if not bool(last_commit_shas) or commit_sha != last_commit_shas[branch_name]:
            # Delete the existing clone folder for this branch
            branch_clone_path = os.path.join(clone_path, branch_name)
            if os.path.exists(branch_clone_path):
                shutil.rmtree(branch_clone_path, onerror=remove_readonly)

            # Clone the repository for this branch to the specified folder
            os.makedirs(branch_clone_path, exist_ok=True)
            os.system(f"git clone --branch {branch_name} https://github.com/{repo_owner}/{repo_name}.git {branch_clone_path}")

            # Build the code for this branch as needed
            os.makedirs(os.path.join(branch_clone_path, "build"))
            os.system(f"cd {branch_clone_path}/build && cmake .. && cmake --build . --clean-first --config Release -j 4")

        # Store the new commit SHA for this branch
        last_commit_shas[branch_name] = commit_sha

    # Wait for the specified delay time before checking again
    time.sleep(delay)