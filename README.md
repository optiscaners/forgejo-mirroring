# Forgejo Mirroring

[![python][python-version-src]][python-version-href]

Quickly backup your GitHub and GitLab repositories via [Forgejo](https://forgejo.org/) mirroring, Docker ready.

Repository mirror name will use this template: `{forge_shortcut}_{group}_{name}` (lowercase), like `gh_ewilan-riviere_forgejo-mirroring`. Mirror authentication will use `oauth2` with GitHub/GitLab token (`mirror` and `private`).

## Environnement

Create `.env`:

```sh
git clone https://github.com/ewilan-riviere/forgejo-mirroring.git
cp .env.example .env
```

> [!TIP]
> For security reasons, choose a token with an expiration date. The goal of this project is to make mirroring very easy on all your repositories, so if your tokens have a one-year expiration date, you only need to run a command once a year.

### For GitHub

- `GITLAB_ORGS`: set GitHub username and organizations you want to mirror
- `GITHUB_TOKEN`: set GitHub token, go to <https://github.com/settings/tokens> to generate it

[**Personal access tokens (classic)**](https://github.com/settings/tokens)

- `repo`: `repo:status`, `repo_deployment`, `public_repo`, `repo:invite`, `security_events`
- `read:org`

### For GitLab

Here domain is `gitlab.com`, of course you can replace with your own instance.

- `GITLAB_DOMAIN`: set GitLab domain, default is `gitlab.com`
- `GITLAB_ORGS`: set GitLab username and organizations you want to mirror
- `GITLAB_TOKEN`: set GitLab token, go to <https://gitlab.com/-/user_settings/personal_access_tokens> to generate it

[**Personal access tokens**](https://gitlab.com/-/user_settings/personal_access_tokens)

- `read_api`

### For Forgejo

Here domain is `codeberg.org`, of course you can replace with your own instance.

- `FORGEJO_URL`: optional full Forgejo base URL, for example `http://192.168.19.45:3000`
- `FORGEJO_PROTOCOL`: protocol for `FORGEJO_DOMAIN`, default is `https`
- `FORGEJO_DOMAIN`: set Forgejo domain, default is `codeberg.org`
- `FORGEJO_TOKEN`: set Forgejo token, go to <https://codeberg.org/user/settings/applications> to generate it

[**Access tokens**](https://codeberg.org/user/settings/applications)

- `organization`: _Read_
- `repository`: _Read and write_
- `user`: _Read_

## Usage

Use `docker compose` to execute container:

```sh
docker compose up -d
```

### `sync`

Sync GitHub and GitLab repositories with Forgejo.

```sh
docker exec -it forgejo-mirroring forgejo-mirroring sync
```

| Option       | Alias | Description                                  | Default |
| ------------ | ----- | -------------------------------------------- | ------- |
| `--archived` | `-a`  | Create mirrors for archived repositories too | `False` |
| `--pull`     | `-p`  | Pull changements from mirrored repository    | `False` |

### `override`

Erase Forgejo mirrored repositories to create new mirrors of GitHub and GitLab repositories with Forgejo.

```sh
docker exec -it forgejo-mirroring forgejo-mirroring override
```

| Option       | Alias | Description                                  | Default |
| ------------ | ----- | -------------------------------------------- | ------- |
| `--archived` | `-a`  | Create mirrors for archived repositories too | `False` |

### Sync every week

If you want to sync your repositories with Forgejo every week, you can set a cron:

```sh
sudo crontab -e
```

```bash
# Every sunday
0 0 * * SUN docker exec -it forgejo-mirroring forgejo-mirroring sync -a
```

### Refresh token

If you need to refresh GitHub and GitLab tokens, change tokens into `.env` and use `override` command:

```sh
docker exec -it forgejo-mirroring forgejo-mirroring override -a
```

<!-- ### Test

Execute tests:

```sh
pytest -v
``` -->

## Endpoints used

### GitHub API

[GitHub API](https://docs.github.com/en/rest/about-the-rest-api/about-the-rest-api) with **API Version** _2022-11-28_

- [**List repositories for the authenticated user**](https://docs.github.com/en/rest/repos/repos#list-repositories-for-the-authenticated-user): _GET_ `/user/repos` (`visibility`, `affiliation`, `sort`, `direction`, `per_page`, `page`)

### GitLab API

[GitLab API](https://docs.gitlab.com/api/rest) and [Endpoints available for GitHub App user access tokens](https://docs.github.com/en/rest/authentication/endpoints-available-for-github-app-user-access-tokens) with **API Version** _18.8.0_ (`/api/v4`)

- [**List projects**](https://docs.gitlab.com/api/projects/#list-all-projects): _GET_ `/projects` (`membership`, `order_by`, `sort`, `per_page`, `page`)

### Forgejo API

[Forgejo API](https://codeberg.org/api/swagger) (or with `FORGEJO_INSTANCE/api/swagger`) with **API Version** _13.0.3_ (`/api/v1`)

- [**List the repos that the authenticated user owns**](https://codeberg.org/api/swagger#/user/userCurrentListRepos): _GET_ `/user/repos` (`order_by`, `limit`, `page`)
- [**Get a repository**](https://codeberg.org/api/swagger#/repository/repoGet): _GET_ `/repos/{owner}/{repo}`
- [**Delete a repository**](https://codeberg.org/api/swagger#/repository/repoDelete): _DELETE_ `/repos/{owner}/{repo}`
- [**Migrate a remote git repository**](https://codeberg.org/api/swagger#/repository/repoMigrate): _POST_ `/repos/migrate` (`clone_addr`, `repo_name`, `auth_username`, `auth_password`, `mirror`, `private`)
- [**Sync a mirrored repository**](https://codeberg.org/api/swagger#/repository/repoMirrorSync): _POST_ `/repos/{owner}/{repo}/mirror-sync`

[python-version-src]: https://img.shields.io/static/v1?style=flat&label=Python&message=v3.12&color=3776AB&logo=python&logoColor=ffffff&labelColor=18181b
[python-version-href]: https://www.python.org/
