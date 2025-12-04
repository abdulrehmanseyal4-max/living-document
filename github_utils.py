import datetime
from urllib.parse import urlparse
from github import Github, Auth, Repository


def extract_repo_path(url_or_path: str) -> str:
    """Cleans up the input URL to get 'owner/repo'."""
    if "github.com" not in url_or_path:
        return url_or_path.strip("/")
    parsed = urlparse(url_or_path)
    path = parsed.path.strip("/")
    if path.endswith(".git"):
        path = path[:-4]
    return path

def connect_to_github(token: str) -> Github:
    auth = Auth.Token(token)
    return Github(auth=auth)

def fetch_latest_commit_diff(repo: Repository.Repository):
    """Fetches the actual code changes (diff) for the Changelog."""
    try:
        latest_commit = repo.get_commits()[0]
        diff_data = ""
        for file in latest_commit.files:
            if file.patch:
                diff_data += f"\nFile: {file.filename}\nDiff:\n{file.patch}\n"
        return diff_data[:5000]
    except:
        return ""

def fetch_repo_file_structure(repo: Repository.Repository, limit_chars=20000):
    """
    Fetches ALL files as individual documents for the RAG system.
    Returns a list of dicts: [{'source': path, 'content': text}]
    """
    documents = []
    queue = list(repo.get_contents(""))
    
    files_processed = 0
    MAX_FILES = 200 
    
    allowed_extensions = {'.py', '.js', '.ts', '.md', '.txt', '.json', '.html', '.css', '.java', '.cpp'}

    while queue and files_processed < MAX_FILES:
        file_content = queue.pop(0)
        
        if file_content.type == "dir":
            queue.extend(repo.get_contents(file_content.path))
        else:
            _, ext = file_content.name.lower().rsplit('.', 1) if '.' in file_content.name else (None, '')
            ext = f".{ext}"
            
            if ext in allowed_extensions:
                try:
                    text = file_content.decoded_content.decode("utf-8")
                    documents.append({"source": file_content.path, "content": text})
                    files_processed += 1
                except:
                    pass 
            
    return documents

def create_multi_file_pr(repo: Repository.Repository, file_updates: list, title: str, body: str):
    """
    Creates a PR with MULTIPLE file changes (README + CHANGELOG).
    file_updates = [{'path': 'README.md', 'content': '...'}, {'path': 'CHANGELOG.md', ...}]
    """
    default_branch = repo.get_branch(repo.default_branch)
    branch_name = f"docs/update-{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}"
    
    repo.create_git_ref(ref=f"refs/heads/{branch_name}", sha=default_branch.commit.sha)
    
    for file in file_updates:
        try:
            contents = repo.get_contents(file['path'], ref=branch_name)
            repo.update_file(file['path'], f"Update {file['path']}", file['content'], contents.sha, branch=branch_name)
        except:
            repo.create_file(file['path'], f"Create {file['path']}", file['content'], branch=branch_name)
        
    pr = repo.create_pull(
        title=title,
        body=body,
        head=branch_name,
        base=repo.default_branch
    )
    return pr.html_url