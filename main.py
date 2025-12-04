import os
import sys
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils import github_utils
import graph 

load_dotenv()

def run_agent():
    print("---Living Documentation Agent (Final Production Build) ---")
    
    token = os.getenv("GITHUB_TOKEN")
    if not token: 
        return print("❌ Error: GITHUB_TOKEN missing. Check your .env file.")
    
    try:
        g = github_utils.connect_to_github(token)
    except Exception as e:
        return print(f"❌ Connection Failed: {e}")

    if os.getenv("GITHUB_REPOSITORY"):
        repo_name = os.getenv("GITHUB_REPOSITORY")
        print(f"Automation detected. Target: {repo_name}")
    else:
        raw_input = input("Enter GitHub repo (e.g. username/project): ")
        repo_name = github_utils.extract_repo_path(raw_input)
    
    print(f"🔍 Locating {repo_name}...")
    try:
        repo = g.get_repo(repo_name)
    except:
        return print(f"❌ Repo '{repo_name}' not found or token lacks permissions.")

    print("🚀 Initializing Agent State...")
    initial_state = {
        "repo": repo,
        "retriever": None,
        "latest_diff": "",
        "current_readme": "",
        "code_reality": "",
        "missing_features": "",
        "draft_content": "",
        "critique_feedback": "",
        "revision_count": 0,
        "final_readme": "",
        "changelog_entry": "",
        "file_updates": []
    }

    print("⚡ Starting Workflow...")
    app = graph.build_graph()
    app.invoke(initial_state)
    print("Workflow Finished Successfully.")

if __name__ == "__main__":
    run_agent()