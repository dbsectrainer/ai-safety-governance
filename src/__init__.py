"""Application package.

Loading .env here ensures configuration is available before the database and
security modules read environment variables. Existing environment variables are
not overridden (load_dotenv default), so Docker/CI settings take precedence.
"""

from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")
