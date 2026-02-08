"""
Deploy backend to Hugging Face Spaces
Usage: python deploy_to_hf.py <HF_TOKEN>
"""
import os
import sys
import shutil
from pathlib import Path
from huggingface_hub import HfApi, create_repo, upload_folder

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def deploy_to_hf_space(space_name: str, hf_token: str):
    """
    Deploy the backend to a Hugging Face Space.

    Args:
        space_name: Name of the space (e.g., 'MSK9218/HackPhase-4')
        hf_token: Hugging Face API token
    """
    print(f"[*] Deploying to Hugging Face Space: {space_name}")

    # Initialize HF API
    api = HfApi(token=hf_token)

    # Create or get the space
    try:
        print("[*] Creating/verifying space...")
        create_repo(
            repo_id=space_name,
            token=hf_token,
            repo_type="space",
            space_sdk="docker",
            exist_ok=True
        )
        print("[+] Space created/verified successfully")
    except Exception as e:
        print(f"[!] Space creation: {e}")
        print("Continuing with deployment...")

    # Prepare files for upload
    print("[*] Preparing files for upload...")
    backend_dir = Path(__file__).parent

    # Files to upload
    files_to_upload = [
        "src",
        "Dockerfile",
        "requirements.txt",
        "pyproject.toml",
        "app.py",
        ".env.example"
    ]

    # Copy README_HF.md as README.md for the space
    readme_hf = backend_dir / "README_HF.md"
    readme_space = backend_dir / "README.md"

    # Backup original README if it exists
    if readme_space.exists():
        shutil.copy(readme_space, backend_dir / "README_ORIGINAL.md")
        print("[*] Backed up original README.md")

    # Copy HF README
    shutil.copy(readme_hf, readme_space)
    print("[*] Using Hugging Face README")

    try:
        # Upload the entire backend folder
        print("[*] Uploading files to Hugging Face Space...")
        api.upload_folder(
            folder_path=str(backend_dir),
            repo_id=space_name,
            repo_type="space",
            token=hf_token,
            ignore_patterns=[
                ".git*",
                "__pycache__",
                "*.pyc",
                ".venv",
                "venv",
                ".env",
                "*.log",
                "tests",
                "docs",
                ".claude",
                "*.egg-info",
                "uv.lock",
                "README_ORIGINAL.md",
                "README_HF.md",
                "deploy_to_hf.py"
            ]
        )
        print("[+] Upload completed successfully!")

        # Print the space URL
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

    except Exception as e:
        print(f"[-] Upload failed: {e}")
        raise
    finally:
        # Restore original README if it existed
        if (backend_dir / "README_ORIGINAL.md").exists():
            shutil.move(backend_dir / "README_ORIGINAL.md", readme_space)
            print("[*] Restored original README.md")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python deploy_to_hf.py <HF_TOKEN>")
        print("Or set HF_TOKEN environment variable")
        hf_token = os.environ.get("HF_TOKEN")
        if not hf_token:
            print("Error: No Hugging Face token provided")
            sys.exit(1)
    else:
        hf_token = sys.argv[1]

    space_name = "MSK9218/HackPhase-4"

    try:
        deploy_to_hf_space(space_name, hf_token)
    except Exception as e:
        print(f"\n[-] Deployment failed: {e}")
        sys.exit(1)
