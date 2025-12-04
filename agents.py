import os
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from prompts import (
    STRICT_SYSTEM_PROMPT,
    AUDIT_PROMPT,
    INTEGRATION_PROMPT,
    REVIEW_PROMPT,
    CHANGELOG_PROMPT,
    CRITIQUE_PROMPT,
    REVISION_PROMPT
)

load_dotenv()

llm = ChatOllama(model="llama3.1:latest", temperature=0.1)

def run_stream(chain, inputs):
    """Runs the chain with live terminal output, returning final string."""
    full_response = ""
    print("\033[96m   > \033[0m", end="", flush=True) 
    
    for chunk in chain.stream(inputs):
        content = chunk.content
        print(content, end="", flush=True)
        full_response += content
        
    print("\n")
    return full_response


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

def reflect_on_draft(draft, code_context):
    print("Reflection: Checking for missing tech/features...")
    prompt = ChatPromptTemplate.from_messages([
        ("system", CRITIQUE_PROMPT),
        ("human", "DRAFT:\n{draft}\n\nCODE CONTEXT:\n{context}")
    ])
    chain = prompt | llm
    return run_stream(chain, {"draft": draft, "context": code_context})

def revise_draft(draft, feedback):
    print("Reviser: Fixing draft based on feedback...")
    prompt = ChatPromptTemplate.from_messages([
        ("system", REVISION_PROMPT),
        ("human", "DRAFT:\n{draft}\n\nFEEDBACK:\n{feedback}")
    ])
    chain = prompt | llm
    return run_stream(chain, {"draft": draft, "feedback": feedback})