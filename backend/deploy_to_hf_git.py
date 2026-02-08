"""
Deploy backend to Hugging Face Spaces using Git
Usage: python deploy_to_hf_git.py <HF_TOKEN>
"""
import os
import sys
import shutil
import subprocess
from pathlib import Path

def run_command(cmd, cwd=None):
    """Run a shell command and return output"""
    print(f"[*] Running: {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[-] Error: {result.stderr}")
        return False, result.stderr
    return True, result.stdout

def deploy_to_hf_space(space_name: str, hf_token: str):
    """
    Deploy the backend to a Hugging Face Space using Git.
    """
    print(f"[*] Deploying to Hugging Face Space: {space_name}")

    backend_dir = Path(__file__).parent
    temp_dir = backend_dir / "temp_hf_deploy"

    # Clean up temp directory if it exists
    if temp_dir.exists():
        shutil.rmtree(temp_dir)

    # Create temp directory
    temp_dir.mkdir()

    try:
        # Clone the space
        space_url = f"https://huggingface.co/spaces/{space_name}"
        clone_url = f"https://oauth2:{hf_token}@huggingface.co/spaces/{space_name}"

        print(f"[*] Cloning space from {space_url}")
        success, output = run_command(f'git clone {clone_url} "{temp_dir}"')
        if not success:
            print("[!] Space doesn't exist yet, creating new repository...")
            temp_dir.mkdir(exist_ok=True)
            run_command(f'git init', cwd=temp_dir)
            run_command(f'git remote add origin {clone_url}', cwd=temp_dir)

        # Copy necessary files
        print("[*] Copying files...")
        files_to_copy = {
            "src": temp_dir / "src",
            "Dockerfile": temp_dir / "Dockerfile",
            "requirements.txt": temp_dir / "requirements.txt",
            "pyproject.toml": temp_dir / "pyproject.toml",
            "app.py": temp_dir / "app.py",
            ".env.example": temp_dir / ".env.example",
        }

        for src, dst in files_to_copy.items():
            src_path = backend_dir / src
            if src_path.exists():
                if src_path.is_dir():
                    if dst.exists():
                        shutil.rmtree(dst)
                    shutil.copytree(src_path, dst)
                else:
                    shutil.copy2(src_path, dst)
                print(f"  [+] Copied {src}")

        # Create README.md from README_HF.md
        readme_hf = backend_dir / "README_HF.md"
        readme_space = temp_dir / "README.md"
        if readme_hf.exists():
            shutil.copy2(readme_hf, readme_space)
            print("  [+] Copied README.md")

        # Create .gitignore
        gitignore_content = """
.env
__pycache__/
*.pyc
*.pyo
*.log
.DS_Store
.venv/
venv/
*.egg-info/
"""
        (temp_dir / ".gitignore").write_text(gitignore_content)
        print("  [+] Created .gitignore")

        # Git operations
        print("[*] Committing changes...")
        run_command('git config user.email "deploy@huggingface.co"', cwd=temp_dir)
        run_command('git config user.name "HF Deploy Bot"', cwd=temp_dir)
        run_command('git add .', cwd=temp_dir)
        run_command('git commit -m "Deploy backend to Hugging Face Spaces"', cwd=temp_dir)

        # Push to Hugging Face
        print("[*] Pushing to Hugging Face...")
        success, output = run_command('git push origin main', cwd=temp_dir)
        if not success:
            # Try master branch if main doesn't work
            run_command('git branch -M main', cwd=temp_dir)
            success, output = run_command('git push -u origin main', cwd=temp_dir)

        if success:
            space_url = f"https://huggingface.co/spaces/{space_name}"
            print(f"\n[+] Deployment successful!")
            print(f"[*] Space URL: {space_url}")
            print(f"[*] API Docs: {space_url}/docs")
            print(f"\n[*] Next steps:")
            print(f"   1. Go to {space_url}/settings")
            print(f"   2. Add environment variables as Secrets:")
            print(f"      - database_url")
            print(f"      - llm_provider")
            print(f"      - llm_model")
            print(f"      - llm_api_key")
            print(f"      - llm_base_url")
            print(f"      - BETTER_AUTH_SECRET")
            print(f"   3. Wait for the Space to build (may take 5-10 minutes)")
            print(f"   4. Test your API at {space_url}/docs")
        else:
            print("[-] Push failed")
            return False

    except Exception as e:
        print(f"[-] Error during deployment: {e}")
        return False
    finally:
        # Clean up
        if temp_dir.exists():
            print("[*] Cleaning up temporary files...")
            shutil.rmtree(temp_dir)

    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python deploy_to_hf_git.py <HF_TOKEN>")
        hf_token = os.environ.get("HF_TOKEN")
        if not hf_token:
            print("Error: No Hugging Face token provided")
            sys.exit(1)
    else:
        hf_token = sys.argv[1]

    space_name = "MSK9218/HackPhase-4"

    if deploy_to_hf_space(space_name, hf_token):
        sys.exit(0)
    else:
        sys.exit(1)
