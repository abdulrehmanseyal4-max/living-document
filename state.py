from typing import TypedDict, List, Any


class AgentState(TypedDict):
    repo: Any
    retriever: Any
    latest_diff: str
    current_readme: str
    
    code_reality: str
    missing_features: str
    draft_content: str
    
    critique_feedback: str
    revision_count: int
    
    final_readme: str
    changelog_entry: str
    file_updates: List[dict]
