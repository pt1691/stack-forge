# Releasing Stack Forge

Releases are driven entirely by **git tags**. Pushing a `vMAJOR.MINOR.PATCH`
tag to `origin` triggers the release workflow which:

1. Runs the full test suite (Python 3.12 & 3.13)
2. Builds the wheel and source distribution
3. Publishes to [PyPI](https://pypi.org/p/stack-forge-infra)
4. Creates a GitHub Release with auto-generated notes and the dist artifacts attached

---

## Versioning scheme

Follow [Semantic Versioning](https://semver.org/):

| Change type | Example |
|---|---|
| Breaking / incompatible API change | `v1.0.0` → `v2.0.0` |
| New backwards-compatible feature | `v1.0.0` → `v1.1.0` |
| Backwards-compatible bug fix | `v1.0.0` → `v1.0.1` |
| Pre-release (alpha / beta / rc) | `v1.1.0-alpha.1` |

---

## Step-by-step release process

### 1. Finish your work on `main`

Make sure all intended commits are merged into `main` and CI is green.

```bash
git checkout main
git pull origin main
```

### 2. Create an annotated tag

```bash
# Patch release
git tag -a v0.1.1 -m "chore: release v0.1.1"

# Minor release
git tag -a v0.2.0 -m "chore: release v0.2.0"

# Major release
git tag -a v1.0.0 -m "chore: release v1.0.0"

# Pre-release
git tag -a v1.0.0-alpha.1 -m "chore: release v1.0.0-alpha.1"
```

### 3. Push the tag

```bash
git push origin <tag-name>
# e.g.
git push origin v0.1.1
```

This push triggers the `release.yml` workflow immediately.

### 4. Monitor the release

Open <https://github.com/pt1691/stack-forge/actions> and watch the
**Release** workflow. If it fails, delete the tag, fix the issue, and re-tag:

```bash
# Delete locally and remotely, then re-tag
git tag -d v0.1.1
git push origin :refs/tags/v0.1.1
```

---

## One-time PyPI trusted publishing setup

The release workflow uses OIDC (no long-lived API tokens). Configure the
trusted publisher on PyPI **once**:

1. Go to <https://pypi.org/manage/project/stack-forge-infra/settings/publishing/>
2. Add a **GitHub Actions** publisher with:
   - **Owner:** `pt1691`
   - **Repository:** `stack-forge`
   - **Workflow filename:** `release.yml`
   - **Environment:** `pypi`
3. On GitHub, create an environment named `pypi` at  
   <https://github.com/pt1691/stack-forge/settings/environments>  
   (optionally add required reviewers as an approval gate).

After that, every tag push will publish automatically with no secrets to manage.

---

## Local version check

After installing the package in development mode (`pip install -e ".[dev]"`),
the version reflects the nearest tag plus a dev suffix if there are commits on
top:

```bash
python -c "import stack_forge; print(stack_forge.__version__)"
# On an exact tag:  0.1.1
# Between tags:     0.1.1.dev3+gabcdef0
```
