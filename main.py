import os
import github_utils
import graph  # <--- Import our new Graph

def run_agent():
    print("--- 🤖 Living Documentation Agent (Reflexion Edition) ---")
    
    token = os.getenv("GITHUB_TOKEN")
    if not token: return print("❌ Error: GITHUB_TOKEN missing.")
    
    g = github_utils.connect_to_github(token)
    raw_input = input("Enter GitHub repo (e.g. username/project): ")
    repo_name = github_utils.extract_repo_path(raw_input)
    
    try:
        repo = g.get_repo(repo_name)
    except:
        return print("❌ Repo not found.")

    # Initialize State
    initial_state = {
        "repo": repo,
        "retriever": None,
        "latest_diff": "",
        "current_readme": "",
        "code_reality": "",
        "missing_features": "",
        "draft_content": "",
        "final_readme": "",
        "changelog_entry": "",
        "file_updates": [],
        
        # New Reflection Fields
        "critique_feedback": "",
        "revision_count": 0
    }

    app = graph.build_graph()
    app.invoke(initial_state)

if __name__ == "__main__":
    run_agent()