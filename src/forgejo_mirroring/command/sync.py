"""sync command of forgejo-mirroring"""

from typing import List
from forgejo_mirroring.args import ForgejoMirroringArgs
from forgejo_mirroring.models import Repository
from forgejo_mirroring.forge import ForgeForgejo, ForgeGithub, ForgeGitlab, Forge
from forgejo_mirroring.env import (
    GITHUB_ORGS,
    GITHUB_TOKEN,
    GITLAB_DOMAIN,
    GITLAB_ORGS,
    GITLAB_TOKEN,
    logger,
)
import forgejo_mirroring.utils as utils


def _is_configured(*values: str | None) -> bool:
    """Return True when all config values are present and not placeholder nulls."""
    return all(value and value.strip().lower() not in {"none", "null"} for value in values)


class CommandSync:
    """sync command of forgejo-mirroring"""

    def __init__(self, args: ForgejoMirroringArgs, override: bool = False):
        self._args = args
        self._forgejo = ForgeForgejo()
        self._sources: list[Forge] = []

        if _is_configured(GITHUB_TOKEN, GITHUB_ORGS):
            self._sources.append(ForgeGithub())
        else:
            logger.info("Skip GitHub: GITHUB_TOKEN or GITHUB_ORGS missing")

        if _is_configured(GITLAB_DOMAIN, GITLAB_TOKEN, GITLAB_ORGS):
            self._sources.append(ForgeGitlab())
        else:
            logger.info("Skip GitLab: GITLAB_DOMAIN, GITLAB_TOKEN or GITLAB_ORGS missing")

        self._listing_forgejo()

        if override:
            self._delete_forgejo_mirrors()
            self._listing()

            for forge in self._sources:
                self._mirror(forge.repositories, forge)
        else:
            self._listing()

            for forge in self._sources:
                missing = self._forgejo.syncing(forge.repositories)
                logger.info("Mirroring %s repositories...", forge.__class__.__name__)
                self._mirror(missing, forge)

            if args.pull:
                self._sync_mirrors()

        utils.alert_sound()

    def _sync_mirrors(self):
        """Sync Forgejo repositories mirrors"""
        for repo in self._forgejo.repositories:
            self._forgejo.sync_mirror(repo)

    def _listing_forgejo(self):
        """Fetch Forgejo repositories"""
        logger.info("🚀 Fetch Forgejo repositories...")
        self._forgejo.listing()

    def _listing(self):
        """Fetch repositories of configured source forges"""
        for forge in self._sources:
            logger.info("Fetch %s repositories...", forge.__class__.__name__)
            forge.listing()

    def _mirror(self, repositories: List[Repository], forge: Forge):
        """Mirror `repositories` to Forgejo"""
        self._forgejo.mirror_repositories(
            repositories,
            forge,
            self._args.archived,
        )

    def _delete_forgejo_mirrors(self):
        """Delete mirrored repositories on Forgejo"""
        mirrors = sum(1 for repo in self._forgejo.repositories if repo.mirrored)
        logger.info("Forgejo delete %s mirrors...", mirrors)
        self._forgejo.delete_mirrors()
