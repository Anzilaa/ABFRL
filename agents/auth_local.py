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
from dotenv import load_dotenv


def setup_google_api_key(env_var: str = "GOOGLE_API_KEY",
                         dotenv_path: Optional[str] = None,
                         use_vertexai: bool = False,
                         prompt: bool = True) -> None:
    """Configure `GOOGLE_API_KEY` for local use.

    Resolution order:
    1. Existing environment variable
    2. `.env` file (if `python-dotenv` is available and `dotenv_path` is provided or discoverable)
    3. Interactive prompt (if `prompt=True` and input is available)

    Side effects:
    - sets `os.environ['GOOGLE_API_KEY']`
    - sets `os.environ['GOOGLE_GENAI_USE_VERTEXAI']` to "TRUE" or "FALSE"
    """
    api_key = os.environ.get(env_var)

    if not api_key and dotenv_path is not None:
        try:
            from dotenv import load_dotenv, find_dotenv
            path = dotenv_path or find_dotenv()
            if path:
                load_dotenv(path)
                api_key = os.environ.get(env_var)
        except Exception:
            pass

    if not api_key and dotenv_path is None:
        # try to auto-discover a .env in the project
        try:
            from dotenv import load_dotenv, find_dotenv
            path = find_dotenv()
            if path:
                load_dotenv(path)
                api_key = os.environ.get(env_var)
        except Exception:
            pass

    if not api_key and prompt:
        try:
            val = input("Enter your GOOGLE_API_KEY (leave empty to cancel): ").strip()
            if val:
                api_key = val
        except Exception:
            pass

    if not api_key:
        raise RuntimeError(
            "Google API key not found. Set the environment variable 'GOOGLE_API_KEY', "
            "create a .env file with GOOGLE_API_KEY=..., or provide it interactively."
        )

    os.environ[env_var] = api_key
    os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "TRUE" if use_vertexai else "FALSE"


if __name__ == "__main__":
    try:
        setup_google_api_key()
        print("✅ Google API key configured (source: environment/.env/interactive).")
    except Exception as e:
        print(f"🔑 Authentication Error: {e}")
