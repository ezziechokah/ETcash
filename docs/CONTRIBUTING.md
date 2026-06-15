# Contributing to ETcash

Thank you for contributing to ETcash. This file describes the recommended workflow for branching, commits, reviews, and documentation updates.

## Branching

- Create feature branches for new work, e.g. `feature/invoice-pdf-export`.
- Use `bugfix/` for bug fixes.
- Use `hotfix/` for urgent production patches.
- Use `release/` for staging or release candidate branches.
- Keep branches focused on a single change or related set of changes.

## Commit messages

Use clear, imperative commit messages.

Examples:

- `Add invoice PDF export button`
- `Fix CSV export formatting for KRA WHT report`
- `Update backend API auth flow`

Commit message tips:

- Keep the summary line concise.
- Add a longer description when necessary.
- Reference issue or ticket IDs if your team uses them.

## Pull requests / code review

- Open one pull request per logical change.
- Include a short summary of the work.
- Describe testing steps and verification instructions.
- Keep PRs small and easy to review.

## Code style and quality

### Backend

- Follow Python and Django best practices.
- Keep models, serializers, views, and URLs organized in their app directories.
- Add new endpoints consistently in `backend/etcash/urls.py` and app-specific `urls.py` files.

### Frontend

- Keep React components reusable and composable.
- Use `src/` conventions for pages, components, utilities, and API client code.
- Avoid large monolithic components.

### Desktop

- Keep Electron shell code focused on window, IPC, and packaging concerns.
- Store frontend build artifacts in `electron/resources` only via packaging.

## Documentation updates

- Update `docs/README.md` when setup, workflow, or architecture changes.
- Add new API routes to the `API Documentation` section.
- Add new frontend run/build instructions to the `Installation` or `Development Workflows` sections.
- If workflow changes are significant, consider adding examples to `docs/CHANGELOG.md`.

## Reporting issues

- Provide a clear description of the issue.
- Include reproduction steps.
- Add relevant environment details, such as OS, Python version, and Node/npm versions.
- If possible, include screenshots or console logs.

## Local development checklist

Before opening a PR:

- [ ] Run backend migrations and ensure the server starts cleanly.
- [ ] Run the frontend dev server and confirm the UI loads.
- [ ] Verify any new API routes are reachable.
- [ ] Update documentation if installation, setup, or usage changed.

## License and code of conduct

- This repo currently does not include an explicit license file.
- Add `LICENSE` for commercial or open-source distribution.
- If you adopt a code of conduct, add it at the root of the repository.
