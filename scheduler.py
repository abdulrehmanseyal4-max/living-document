import time
import os
import sys
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import utils.github_utils as github_utils
import main 

load_dotenv()

CHECK_INTERVAL_HOURS = 0.0833  # 5 Minutes
STATE_FILE = ".agent_memory" 

def get_last_processed_sha():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return f.read().strip()
    return None

def save_current_sha(sha):
    with open(STATE_FILE, "w") as f:
        f.write(sha)

def automation_loop():
    print("---Living Documentation Scheduler Started ---")
    
    token = os.getenv("GITHUB_TOKEN")
    if not token: return print("❌ Error: GITHUB_TOKEN missing.")
    
    try:
        g = github_utils.connect_to_github(token)
    except Exception as e:
        return print(f"❌ Connection Failed: {e}")
    
    raw_input = input("Enter GitHub repo to monitor: ")
    repo_name = github_utils.extract_repo_path(raw_input)
    
    print(f"Watching: {repo_name}")
    print(f"Check Interval: {CHECK_INTERVAL_HOURS} hours")
    print("---------------------------------------------------")

    while True:
        try:
            print(f"\n[{time.strftime('%H:%M:%S')}] Checking for updates...")
            
            repo = g.get_repo(repo_name)
            current_sha = github_utils.get_current_commit_sha(repo)
            last_sha = get_last_processed_sha()

            print(f"   Current SHA: {current_sha[:7]}")
            print(f"   Last SHA:    {last_sha[:7] if last_sha else 'None'}")

            if current_sha == last_sha:
                print("No changes detected. Sleeping...")
            else:
                if github_utils.should_ignore_commit(repo):
                    print("Commit ignored (Docs/Skip-CI). Updating memory to skip...")
                    save_current_sha(current_sha)
                else:
                    print("NEW CODE DETECTED! Waking up Agent...")
                    
                    os.environ["GITHUB_REPOSITORY"] = repo_name
                    
                    main.run_agent()
                    
                    save_current_sha(current_sha)
                    print("   ✅ Documentation synced. Memory updated.")

        except KeyboardInterrupt:
            print("\n🛑 Scheduler stopped by user.")
            break
        except Exception as e:
            print(f"❌ Error in scheduler loop: {e}")

        time.sleep(CHECK_INTERVAL_HOURS * 3600)

if __name__ == "__main__":
    automation_loop()