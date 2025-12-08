import datetime
from urllib.parse import urlparse
from github import Github, Auth, Repository, GithubException

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
        return diff_data[:5000] # Limit size
    except:
        return ""

def fetch_repo_file_structure(repo: Repository.Repository, limit_chars=20000):
    """
    Fetches ALL text-based files recursively.
    Includes smart filtering to skip massive lockfiles and binaries.
    """
    documents = []
    queue = list(repo.get_contents(""))
    
    files_processed = 0
    MAX_FILES = 300
    
    ignored_extensions = {
        '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.pdf', '.zip', '.tar', '.gz',
        '.exe', '.dll', '.so', '.bin', '.pyc', '.class', '.jar',
        '.map', '.log', '.lock' 
    }
    
    ignored_files = {
        'package-lock.json', 'yarn.lock', 'pnpm-lock.yaml', 'poetry.lock', 'uv.lock',
        '.DS_Store', '.gitignore', '.env', 'LICENSE', 'Dockerfile'
    }
    
    ignored_dirs = {
        'node_modules', 'venv', 'env', 'dist', 'build', 'target', 
        '__pycache__', '.git', '.github', '.vscode', '.idea'
    }

    while queue and files_processed < MAX_FILES:
        file_content = queue.pop(0)
        
        if file_content.type == "dir":
            if file_content.name in ignored_dirs or file_content.name.startswith('.'):
                continue
            queue.extend(repo.get_contents(file_content.path))
        else:
            if file_content.name in ignored_files:
                continue
            
            _, ext = file_content.name.lower().rsplit('.', 1) if '.' in file_content.name else (None, '')
            ext = f".{ext}" if ext else ""
            
            if ext in ignored_extensions:
                continue

            try:
                text = file_content.decoded_content.decode("utf-8")
                if not text.strip() or len(text) > 100000:
                    continue
                documents.append({"source": file_content.path, "content": text})
                files_processed += 1
            except UnicodeDecodeError:
                pass 
            except Exception:
                pass
            
    return documents

def create_multi_file_pr(repo: Repository.Repository, file_updates: list, title: str, body: str):
    """
    Creates a PR with MULTIPLE file changes (README + CHANGELOG).
    Includes verbose logging and safe error handling.
    """
    default_branch = repo.get_branch(repo.default_branch)
    branch_name = f"docs/update-{datetime.datetime.now().strftime('%Y-%m-%d-%H%M%S')}"
    
    print(f"   🔹 Creating branch: {branch_name}...", flush=True)
    repo.create_git_ref(ref=f"refs/heads/{branch_name}", sha=default_branch.commit.sha)
    
    for file in file_updates:
        print(f"   🔹 Committing: {file['path']}...", flush=True)
        try:
            contents = repo.get_contents(file['path'], ref=branch_name)
            repo.update_file(file['path'], f"Update {file['path']}", file['content'], contents.sha, branch=branch_name)
            print(f"      ✓ Updated existing file")
        except GithubException as e:
            if e.status == 404:
                repo.create_file(file['path'], f"Create {file['path']}", file['content'], branch=branch_name)
                print(f"      ✓ Created new file")
            else:
                print(f"❌ Error committing {file['path']}: {e}")
                raise e 
        except Exception as e:
            print(f"❌ Unexpected error committing {file['path']}: {e}")
            raise e
        
    print("   🔹 Opening Pull Request...", flush=True)
    pr = repo.create_pull(
        title=title,
        body=body,
        head=branch_name,
        base=repo.default_branch
    )
    return pr.html_url

def get_current_commit_sha(repo):
    branch = repo.get_branch(repo.default_branch)
    return branch.commit.sha

def should_ignore_commit(repo):
    """
    Returns True if the latest commit should NOT trigger an update.
    Criteria:
    1. Message contains '[skip ci]'
    2. Message starts with 'docs:' (Agent's own commits)
    3. The commit ONLY modified .md files
    """
    latest_commit = repo.get_commits()[0]
    message = latest_commit.commit.message.lower()
    
    if "[skip ci]" in message or message.startswith("docs:"):
        print("Ignoring commit: Marked as docs/skip-ci.")
        return True
        
    try:
        is_docs_only = all(f.filename.endswith('.md') for f in latest_commit.files)
        if is_docs_only:
            print("Ignoring commit: Only documentation changed.")
            return True 
    except:
        pass
        
    return False