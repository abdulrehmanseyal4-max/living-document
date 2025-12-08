import datetime
from typing import TypedDict, List, Any
from langgraph.graph import StateGraph, END

from utils import github_utils
from utils import rag_utils
from agents import agents
from agents.state import AgentState


def setup_node(state: AgentState):
    print("--- 📡 Node: Setup ---")
    repo = state['repo']
    documents = github_utils.fetch_repo_file_structure(repo)
    if not documents: return {"file_updates": []}
    
    retriever = rag_utils.index_codebase(documents)
    diff = github_utils.fetch_latest_commit_diff(repo)
    try:
        readme = repo.get_readme().decoded_content.decode("utf-8")
    except:
        readme = ""
        
    return {
        "retriever": retriever, 
        "latest_diff": diff, 
        "current_readme": readme,
        "revision_count": 0,
        "file_updates": []
    }

def audit_node(state: AgentState):
    print("--- 🔍 Node: Audit ---")
    retriever = state['retriever']
    readme = state['current_readme']
    
    code_reality = rag_utils.query_rag(retriever, "What is the purpose of this project? What problem does it solve? List Tech Stack, Main Features, and Installation steps.")
    
    if not readme.strip():
        return {"missing_features": "CREATE_FRESH", "code_reality": code_reality}
    
    missing = agents.audit_readme(readme, code_reality)
    return {"code_reality": code_reality, "missing_features": missing}

def writer_node(state: AgentState):
    print("--- ✍️ Node: Writer ---")
    if state.get('draft_content'):
        return {} 

    missing = state['missing_features']
    readme = state['current_readme']
    code_reality = state['code_reality']
    
    draft = ""
    if missing == "CREATE_FRESH":
        draft = agents.draft_fresh_readme(code_reality)
    elif "NO_CHANGES" not in missing:
        draft = agents.integrate_changes(readme, missing)
    else:
        return {"draft_content": None}

    return {"draft_content": draft}

def reflection_node(state: AgentState):
    print("--- 🤔 Node: Reflection ---")
    draft = state.get('draft_content')
    if not draft: return {"critique_feedback": "PERFECT"}
    
    feedback = agents.reflect_on_draft(draft, state['code_reality'])
    return {"critique_feedback": feedback}

def reviser_node(state: AgentState):
    print("--- 🔧 Node: Reviser ---")
    draft = state['draft_content']
    feedback = state['critique_feedback']
    new_draft = agents.revise_draft(draft, feedback)
    return {"draft_content": new_draft, "revision_count": state['revision_count'] + 1}

def historian_node(state: AgentState):
    print("--- 📜 Node: Historian ---")
    diff = state['latest_diff']
    entry = agents.generate_changelog(diff)
    return {"changelog_entry": entry}

def packaging_node(state: AgentState):
    print("--- 📦 Node: Packaging ---")
    draft = state.get('draft_content')
    final_text = None
    
    if draft:
        final_text = agents.review_content(draft)
        
    updates = []
    if final_text:
        updates.append({"path": "README.md", "content": final_text})
        
    if state.get('changelog_entry'):
        repo = state['repo']
        try:
            current_log = repo.get_contents("CHANGELOG.md").decoded_content.decode("utf-8")
        except:
            current_log = "# Changelog\n\n"
        import datetime
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        new_log = current_log.replace("# Changelog", f"# Changelog\n\n## {today}\n{state['changelog_entry']}")
        updates.append({"path": "CHANGELOG.md", "content": new_log})
        
    return {"file_updates": updates}

def pr_node(state: AgentState):
    print("--- 🚀 Node: Publisher ---")
    updates = state['file_updates']
    if updates:
        url = github_utils.create_multi_file_pr(state['repo'], updates, "docs: Update", "Agent Update")
        print(f"✅ Success! PR: {url}")
    else:
        print("💤 No updates.")
    return {}

def should_revise(state: AgentState):
    feedback = state.get('critique_feedback', '')
    count = state.get('revision_count', 0)
    # Stop if Perfect OR if we tried 1 time already
    if "PERFECT" in feedback or count >= 1:
        return "continue"
    return "revise"

def build_graph():
    workflow = StateGraph(AgentState)
    
    workflow.add_node("setup", setup_node)
    workflow.add_node("audit", audit_node)
    workflow.add_node("writer", writer_node)
    workflow.add_node("reflection", reflection_node)
    workflow.add_node("reviser", reviser_node)
    workflow.add_node("historian", historian_node)
    workflow.add_node("packager", packaging_node)
    workflow.add_node("publisher", pr_node)
    
    workflow.set_entry_point("setup")
    
    # 1. Start with Audit (Linear Flow)
    workflow.add_edge("setup", "audit")
    
    # 2. Then Writer
    workflow.add_edge("audit", "writer")
    
    # 3. Then Reflection
    workflow.add_edge("writer", "reflection")
    
    # 4. Loop Logic:
    # If "revise" -> go to Reviser -> loop back to Reflection
    # If "continue" -> go to HISTORIAN (This ensures Writer finishes first!)
    workflow.add_conditional_edges(
        "reflection", 
        should_revise, 
        {
            "revise": "reviser",
            "continue": "historian" # <--- Critical Fix: Points to Historian
        }
    )
    workflow.add_edge("reviser", "reflection")
    
    # 5. Finish Line
    workflow.add_edge("historian", "packager")
    workflow.add_edge("packager", "publisher")
    workflow.add_edge("publisher", END)
    
    return workflow.compile()