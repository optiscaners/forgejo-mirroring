"""Get variables from .env"""

import os
import sys
import logging
from dotenv import load_dotenv

load_dotenv()

GITLAB_DOMAIN = os.environ.get("GITLAB_DOMAIN")
GITLAB_TOKEN = os.environ.get("GITLAB_TOKEN")
GITLAB_ORGS = os.environ.get("GITLAB_ORGS")

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GITHUB_ORGS = os.environ.get("GITHUB_ORGS")

FORGEJO_DOMAIN = os.environ.get("FORGEJO_DOMAIN")
FORGEJO_URL = os.environ.get("FORGEJO_URL")
FORGEJO_PROTOCOL = os.environ.get("FORGEJO_PROTOCOL", "https")
FORGEJO_TOKEN = os.environ.get("FORGEJO_TOKEN")

PER_PAGE = int(os.environ.get("PER_PAGE", 50))

logger = logging.getLogger()


def python_check() -> None:
    """Check Python version"""
    version_min = (3, 12)
    if sys.version_info < version_min:
        sys.stderr.write(
            f"Error: Python {version_min[0]}.{version_min[1]} or later required.\n"
        )
        sys.exit(1)
