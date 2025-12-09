import os
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate

from agents.prompts import (
    STRICT_SYSTEM_PROMPT,
    AUDIT_PROMPT,
    INTEGRATION_PROMPT,
    REVIEW_PROMPT,
    CHANGELOG_PROMPT
)

load_dotenv()

llm = ChatOllama(model="llama3.1:latest", temperature=0.1)

def clean_response(text):
    """
    Aggressively removes conversational filler from start AND end.
    """
    lines = text.strip().split('\n')
    
    start_index = 0
    for i in range(min(3, len(lines))):
        line_lower = lines[i].lower()
        if "here is" in line_lower or "sure," in line_lower or "i have" in line_lower:
            start_index = i + 1
            
    lines = lines[start_index:]
    
    filler_phrases = [
        "I've made the following changes",
        "Here is the updated",
        "I have updated",
        "Changes made:",
        "Summary of changes:",
        "Here is the polished",
        "I have fixed",
        "Here is the code",
        "Let me know if"
    ]
    
    clean_lines = []
    found_filler = False
    
    for line in lines:
        for phrase in filler_phrases:
            if phrase.lower() in line.lower() and len(line) < 100:
                found_filler = True
                break
        
        if found_filler:
            break 
            
        clean_lines.append(line)
        
    return "\n".join(clean_lines).strip()

def run_stream(chain, inputs):
    """Runs the chain with live terminal output, returning cleaned string."""
    full_response = ""
    print("\033[96m   > \033[0m", end="", flush=True) 
    
    for chunk in chain.stream(inputs):
        content = chunk.content
        print(content, end="", flush=True)
        full_response += content
        
    print("\n")
    return clean_response(full_response)

# --- AGENT FUNCTIONS ---

def draft_fresh_readme(context):
    print("Agent: Drafting fresh README...")
    prompt = ChatPromptTemplate.from_messages([
        ("system", STRICT_SYSTEM_PROMPT),
        ("human", "Context:\n{context}\n\nTask: Write full README.")
    ])
    chain = prompt | llm
    return run_stream(chain, {"context": context})

def audit_readme(current_readme, code_reality):
    print("Agent: Auditing for gaps...")
    prompt = ChatPromptTemplate.from_messages([
        ("system", AUDIT_PROMPT),
        ("human", "README:\n{readme}\n\nCODE:\n{code}")
    ])
    chain = prompt | llm
    return run_stream(chain, {"readme": current_readme, "code": code_reality})

def integrate_changes(current_readme, missing_features):
    print("Agent: Integrating new features...")
    prompt = ChatPromptTemplate.from_messages([
        ("system", INTEGRATION_PROMPT),
        ("human", "README:\n{readme}\n\nMISSING:\n{missing}")
    ])
    chain = prompt | llm
    return run_stream(chain, {"readme": current_readme, "missing": missing_features})

def review_content(text):
    print("Reviewer: Polishing text...")
    prompt = ChatPromptTemplate.from_messages([
        ("system", REVIEW_PROMPT),
        ("human", "Draft:\n{draft}")
    ])
    chain = prompt | llm
    return run_stream(chain, {"draft": text})

def generate_changelog(diff_text):
    if not diff_text: return None
    print("Historian: summarizing diff...")
    prompt = ChatPromptTemplate.from_messages([
        ("system", CHANGELOG_PROMPT),
        ("human", "DIFF:\n{diff}")
    ])
    chain = prompt | llm
    return run_stream(chain, {"diff": diff_text})
