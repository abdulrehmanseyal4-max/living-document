import os
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate

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

STRICT_SYSTEM_PROMPT = """You are a senior technical writer. Write professional documentation.
STRICT RULES:
1. Output raw Markdown ONLY.
2. No conversational filler.
3. Use proper headers (# Title, ## Section).
"""

AUDIT_PROMPT = """Compare 'Code Reality' vs 'Current README'.
Identify MAJOR features in code that are missing from README.
- If accurate, return ONLY: "NO_CHANGES"
- If missing, return a bulleted list of ONLY the missing items.
"""

INTEGRATION_PROMPT = """You are a documentation editor.
Task: Insert MISSING FEATURES into the CURRENT README's "Features" list.
1. Output the FULL README with changes.
2. Do NOT remove existing text.
3. Do NOT create a "Recent Updates" section. Just blend it in.
"""

REVIEW_PROMPT = """You are a Senior Editor. Polish this draft.
1. Fix typos/grammar.
2. Improve tone.
3. Return ONLY the polished markdown.
"""

CHANGELOG_PROMPT = """Summarize this git diff into a single one-line changelog entry.
Format: "- **[Category]** Description"
Example: "- **[Feature]** Added Stripe payment."
"""

CRITIQUE_PROMPT = """You are a Quality Assurance Auditor. 
Compare the GENERATED DRAFT against the CODE CONTEXT.

CHECKLIST:
1. Is the **Tech Stack** complete?
2. Are the **Key Features** accurate?
3. Is the **Installation** guide present?

OUTPUT:
- If everything is good, return strictly: "PERFECT"
- If something is missing, list the specific missing items.
"""

REVISION_PROMPT = """You are a Documentation Fixer.
Rewrite the DRAFT to incorporate the FEEDBACK.
Output the full, corrected Markdown file.
"""


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