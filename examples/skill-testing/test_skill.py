import os
from pathlib import Path

# Note: This is a standalone script to demonstrate skill testing.
# Querying a model requires the 'openai' package (pip install openai) and OPENAI_API_KEY. To
# query another OpenAI-compatible server, set OPENAI_API_KEY to its key and OPENAI_BASE_URL to
# its address. The package is imported only to query a model, so pytest, which collects files
# named test_*.py, can import this module without it.

REPO_ROOT = Path(__file__).parent.parent.parent
ROLES_DIR = REPO_ROOT / ".agent" / "roles" # Adjust path based on actual repo structure if needed
SKILLS_DIR = REPO_ROOT / ".agent" / "skills"

def load_file(path: Path) -> str:
    """Reads content from a file."""
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    return path.read_text(encoding="utf-8")

def build_isolated_prompt(role_name: str, skill_names: list[str], task_description: str) -> str:
    """
    Assembles a prompt by combining the base role, selected skills, and the task.
    This simulates how the Orchestrator builds prompts but for a single interaction.
    """
    # 1. Load Role (Persona)
    # Note: In the actual system, roles might be in System/Agents or .agent/roles
    # For this example, we assume we might test a system agent or a specific role file.
    # Let's try to look in System/Agents first as per the project structure.
    system_agents_dir = REPO_ROOT / "System" / "Agents"
    role_path = system_agents_dir / role_name
    
    if not role_path.exists():
        # Fallback for the sake of the example if the user uses a different path
        role_path = Path(role_name)
    
    print(f"Loading role from: {role_path}")
    role_content = load_file(role_path)
    
    # 2. Load Skills
    skills_content = ""
    for skill in skill_names:
        skill_path = SKILLS_DIR / f"{skill}.md"
        # If skill doesn't exist in .agent/skills, maybe it's full path
        if not skill_path.exists():
             skill_path = SKILLS_DIR / skill / "SKILL.md" # Support folder structure
        
        print(f"Loading skill from: {skill_path}")
        try:
            content = load_file(skill_path)
            skills_content += f"\n### SKILL: {skill}\n{content}\n"
        except FileNotFoundError:
             print(f"Warning: Skill {skill} not found at {skill_path}")

    # 3. Assemble Prompt
    prompt = f"""
{role_content}

### ACTIVE SKILLS (For Testing)
{chr(10).join(f"- {s}" for s in skill_names)}

{skills_content}

### TEST TASK
{task_description}

IMPORTANT: Analyze the task using your skills and provide the response.
"""
    return prompt

def query_model(prompt: str, model: str = "gpt-4o"):
    """Sends the prompt to the server of OPENAI_BASE_URL, with the key of OPENAI_API_KEY."""
    # A key goes only to the server named beside it, so no other key is read (TASK 123)
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1") 
    
    if not api_key:
        print("Warning: OPENAI_API_KEY is not set. For another OpenAI-compatible server, set it "
              "to that server's key and OPENAI_BASE_URL to its address.")
        print("Model query will perform a dry run (printing prompt length).")
        print("--- PROMPT PREVIEW ---")
        print(prompt[:500] + "\n...[truncated]...")
        return "Dry run complete."

    try:
        import openai
    except ImportError:
        print("Error: 'openai' package not found. Please install it using: pip install openai")
        raise SystemExit(1)

    client = openai.OpenAI(api_key=api_key, base_url=base_url)
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error querying model: {e}"

if __name__ == "__main__":
    # --- CONFIGURATION ---
    # Change these values to test different variations
    ROLE_FILE = "08_developer_prompt.md"
    TARGET_SKILLS = ["tdd-stub-first", "documentation-standards"]
    TEST_TASK = """
    Implement a Python function `calculate_fibonacci(n: int) -> int` 
    that returns the nth Fibonacci number. 
    Use the Stub-First approach.
    """
    
    print("--- 1. Building Prompt ---")
    full_prompt = build_isolated_prompt(ROLE_FILE, TARGET_SKILLS, TEST_TASK)
    
    print(f"Prompt constructed ({len(full_prompt)} characters).")
    
    print("\n--- 2. Querying Model ---")
    result = query_model(full_prompt)
    
    print("\n--- MODEL RESPONSE ---\n")
    print(result)
