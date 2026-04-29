"""Forgejo forge"""

import time
from typing import List
from forgejo_mirroring.models import Repository, RequestMethod, Gitforge
from forgejo_mirroring.env import (
    FORGEJO_DOMAIN,
    FORGEJO_PROTOCOL,
    FORGEJO_TOKEN,
    FORGEJO_URL,
    PER_PAGE,
)
import forgejo_mirroring.utils as utils
from forgejo_mirroring.env import logger
from .forge import Forge


class ForgeForgejo(Forge):
    """Forgejo forge"""

    def __init__(self):
        super().__init__(
            self._set_headers(),
            self._set_api_url(),
            FORGEJO_TOKEN or "",
        )

    def listing(self):
        page = 1

        while True:
            response = self.request(
                "/user/repos",
                RequestMethod.GET,
                {
                    "order_by": "oldest",
                    "limit": PER_PAGE,
                    "page": page,
                },
            )
            body = self._parse_body(response)
            if not body:
                break

            for repo in body:
                repository = Repository(
                    full_name=f"{utils.extract(repo, "full_name")}",
                    url=utils.extract(repo, "html_url"),
                    forge=Gitforge.FORGEJO,
                    archived=utils.extract(repo, "archived"),
                )

                if bool(utils.extract(repo, "mirror")):
                    repository.set_mirrored(True)

                self.repositories.append(repository)
            page += 1

        return self

    def syncing(self, forge: List[Repository]) -> List[Repository]:
        """Check missing repositories into Forgejo list comparing to forge list"""

        # 1. We retrieve all existing names in Forgejo (the recipient).
        # We use a set for ultra-fast searching (O(1)).
        names_in_forgejo = {repo.name for repo in self.repositories}

        # 2. Identify the names of mirrors that should be present (the source).
        # Filter: only keep those whose ‘mirror_name’ is not in ‘names_in_forgejo’.
        missing_repos = [
            repo for repo in forge if repo.mirror_name not in names_in_forgejo
        ]

        return missing_repos

    def sync_mirror(self, repository: Repository):
        """Sync a mirrored repository"""
        try:
            resp = self.request(
                f"/repos/{repository.group}/{repository.name}/mirror-sync",
                RequestMethod.POST,
            )
            time.sleep(0.5)

            if resp.status_code in [200]:
                logger.info("Repository %s synced", repository.full_name)
                return True
            else:
                logger.warning("Repository error with syncing %s", repository.full_name)
                return False

        except Exception as e:
            logger.error(
                "Error sync %s",
                e,
            )

    def mirror_repositories(
        self, repositories: List[Repository], forge: Forge, archived: bool = False
    ):
        """Mirror repositories from `repositories`"""
        for repository in repositories:
            if archived is not True and repository.archived:
                logger.warning(
                    "Skip archived %s %s",
                    repository.forge.value,
                    repository.full_name,
                )
                continue

            self.mirror_repository(repository, forge.token)

        return self

    def delete_mirrors(self):
        """Delete all mirrors on Forgejo"""
        for repository in self.repositories:
            if repository.mirrored:
                logger.warning("Delete Forgejo `%s`", repository.full_name)
                success = self.delete_repository(repository)
                if success is not True:
                    logger.error(
                        "  Forgejo `%s` failed to delete", repository.full_name
                    )

    def mirror_repository(self, repository: Repository, token: str) -> bool:
        """Mirror repository from forge to Forgejo"""
        try:
            resp = self.request(
                "/repos/migrate",
                RequestMethod.POST,
                {},
                {
                    "clone_addr": repository.url,
                    "repo_name": repository.mirror_name,
                    "auth_username": "oauth2",
                    "auth_password": token,
                    "mirror": True,
                    "private": True,
                },
            )
            time.sleep(0.5)

            if resp.status_code in [200, 201]:
                msg = f"{repository.forge.get_forge_name()} `{repository.full_name}` ready"
                if repository.archived:
                    logger.info("%s (archived)", msg)
                else:
                    logger.info(msg)
                return True

            if resp.status_code in [409]:
                logger.warning(
                    "Already exists for %s %s",
                    repository.forge.value,
                    repository.full_name,
                )
                return False

        except Exception as e:
            logger.error(
                "Error migrating %s %s: %s",
                repository.forge.value,
                repository.full_name,
                e,
            )

        logger.error(
            "Error migrating %s %s", repository.forge.value, repository.full_name
        )

        return False

    def delete_repository(self, repository: Repository) -> bool:
        """Delete repository from Forgejo"""
        resp = self.request(
            f"/repos/{repository.group}/{repository.name}",
            RequestMethod.DELETE,
        )

        return resp.status_code in [204]

    def is_exists(self, repository: Repository) -> bool:
        """Check if repository exists"""
        resp = self.request(
            f"/repos/{repository.group}/{repository.name}",
            RequestMethod.GET,
        )
        print(resp)
        print(resp.request.path_url)

        return resp.status_code in [204]

    def _set_headers(self):
        return {
            "Authorization": f"Bearer {FORGEJO_TOKEN}",
            "Accept": "application/json",
        }

    def _set_token(self):
        return FORGEJO_TOKEN or ""

    def _set_api_url(self):
        if FORGEJO_URL:
            base_url = FORGEJO_URL
        else:
            domain = FORGEJO_DOMAIN or "codeberg.org"
            if domain.startswith(("http://", "https://")):
                base_url = domain
            else:
                protocol = (FORGEJO_PROTOCOL or "https").rstrip(":/")
                base_url = f"{protocol}://{domain}"

        return f"{base_url.rstrip('/')}/api/v1"
