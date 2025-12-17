"""
Local helper to configure GOOGLE_API_KEY for development.

Usage:
- Set the environment variable `GOOGLE_API_KEY` before running, or
- Create a `.env` file in the project root with `GOOGLE_API_KEY=...` and install `python-dotenv`, or
- Fall back to an interactive prompt.

Call `setup_google_api_key()` early in your program.
"""

import os
from typing import Optional


def setup_google_api_key(env_var: str = "GOOGLE_API_KEY",
                         dotenv_path: Optional[str] = None,
                         use_vertexai: bool = False) -> None:
    """Configure `GOOGLE_API_KEY` for local use.

    Resolution order (non-interactive):
    1. Existing environment variable
    2. `.env` file (loaded via python-dotenv if available and discoverable)

    This function will NOT prompt interactively. If the key is not found
    it raises a RuntimeError so calling scripts fail-fast and CI remains
    non-interactive.

    Side effects:
    - sets `os.environ['GOOGLE_API_KEY']`
    - sets `os.environ['GOOGLE_GENAI_USE_VERTEXAI']` to "TRUE" or "FALSE"
    """
    api_key = os.environ.get(env_var)

    # Attempt to load from dotenv if not present in environment
    if not api_key:
        try:
            from dotenv import load_dotenv, find_dotenv  # type: ignore
            path = dotenv_path or find_dotenv()
            if path:
                load_dotenv(path)
                api_key = os.environ.get(env_var)
        except Exception:
            # dotenv not available or load failed — fall through
            api_key = os.environ.get(env_var)

    # If python-dotenv isn't available or didn't find the file, try a manual
    # fallback: look for a .env file at the repository root (one level up
    # from this `agents` package) and parse it for the key. This avoids
    # depending on an external package and works when `.env` sits outside
    # the `agents/` folder.
    if not api_key:
        try:
            repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
            env_file = os.path.join(repo_root, ".env")
            if os.path.exists(env_file):
                with open(env_file, "r", encoding="utf-8") as fh:
                    for line in fh:
                        line = line.strip()
                        if not line or line.startswith("#") or "=" not in line:
                            continue
                        k, v = line.split("=", 1)
                        k = k.strip()
                        v = v.strip().strip('"\'')
                        if k == env_var:
                            api_key = v
                            os.environ[k] = v
                            break
        except Exception:
            # best-effort only — fall through to other checks
            pass

    # Also accept common alternate env names for convenience (e.g. API, API_KEY)
    if not api_key:
        for alt in ("API", "API_KEY"):
            alt_val = os.environ.get(alt)
            if alt_val:
                api_key = alt_val
                break

    if not api_key:
        raise RuntimeError(
            "Google API key not found. Set one of the environment variables '" + env_var + "', "
            "'API' or 'API_KEY', or create a .env file with one of those keys in the project root."
        )

    os.environ[env_var] = api_key
    os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "TRUE" if use_vertexai else "FALSE"


if __name__ == "__main__":
    try:
        setup_google_api_key()
        print("✅ Google API key configured (source: environment/.env/interactive).")
    except Exception as e:
        print(f"🔑 Authentication Error: {e}")
