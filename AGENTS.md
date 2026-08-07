# ATLAS agent guide

This file is the shared operating contract for AI coding agents and human contributors working in ATLAS. Read the root `README.md` and relevant files in `docs/` before making changes.

## Product boundary

ATLAS is an AI-driven **allocation decision-support platform** for the PM Internship Scheme. This repository is a production-oriented foundation, not a finished product.

Do not implement or infer any of the following without an approved specification from the system architect:

- eligibility or deterministic policy rules;
- allocation algorithms, including Hungarian matching;
- AI ranking, scoring, embeddings, or pgvector search;
- fairness criteria or automated fairness decisions;
- chatbot behavior;
- identity-provider or password-lifecycle behavior.

When a product, legal, or policy decision is required, stop at the boundary and add a `TODO(ATLAS):` comment that clearly states the decision needed.

## Architecture rules

### Backend

Maintain the dependency direction:

```text
api/routes -> api dependencies -> application/services -> domain ports
                                               |
                                               v
                              infrastructure/repositories/database
```

- Route handlers only translate HTTP requests and responses.
- Pydantic request/response types belong in `apps/api/app/api/schemas`.
- Application services coordinate use cases; they must not contain unapproved policy.
- `domain` must not import FastAPI, SQLAlchemy, or provider code.
- Repositories own persistence queries; do not embed SQLAlchemy queries in routes.
- Add an Alembic migration for every persisted schema change. Never use `create_all` for deployment.
- Authentication and RBAC are scaffolds. Do not turn placeholder login/token behavior into a real authentication flow without approval.

### Frontend

- `components/ui` contains small, reusable, domain-neutral primitives.
- `components/layout` contains global shell/navigation only.
- `features/<domain>` owns screens, feature hooks, feature-specific state, and API adapters.
- TanStack Query is for server state; Zustand is only for small cross-screen UI/session state.
- Do not put business or allocation logic in React components.
- Preserve accessible semantics, keyboard operation, focus visibility, and responsive behavior.
- All routes must render a deliberate screen, loading state, error state, or empty state.

## Working process

1. Inspect the relevant code and documentation before editing.
2. State the exact files you intend to change and why. For small, obvious fixes, a concise plan is enough.
3. Keep changes focused. Do not combine feature work with broad formatting, dependency upgrades, or unrelated refactors.
4. Reuse existing patterns and components before creating new abstractions.
5. Add or update focused tests for changed observable behavior.
6. Run the relevant validation commands before reporting completion.
7. Report: changed files, validation results, known limitations, and any `TODO(ATLAS)` decisions.

## Required validation

Run only the checks relevant to changed areas, plus any affected cross-cutting checks:

```powershell
# Backend
cd apps/api
python -m pytest
python -m ruff check .

# Frontend
cd apps/web
npm test
npm run lint
npm run build
```

If Docker is available and Compose changes are made, also run:

```powershell
docker compose config
docker compose up --build
```

If a required tool is not installed or a check cannot run, state that fact plainly and provide the exact command a developer should run.

## Security and safety

- Never commit `.env`, credentials, API keys, generated secrets, personal data, or production data.
- Use environment variables through the centralized configuration layers; do not hardcode secrets or URLs for deployed environments.
- Do not weaken authorization, CORS, validation, logging, or error handling just to make tests pass.
- Do not run destructive database, Git, or file-system commands without explicit user approval.
- Treat MCP servers, plugins, browser sessions, and external integrations as privileged. Use the least access necessary.

## Git and pull requests

- Work on a focused branch; use a descriptive, scoped commit message.
- Do not stage or overwrite unrelated user changes.
- Do not push, open a pull request, merge, or alter repository settings unless explicitly asked.
- A PR description must include scope, rationale, validation, limitations, and follow-up work.

## Definition of done

A task is complete only when its requested scope is implemented, validation has been run in proportion to risk, documentation is updated where behavior or setup changed, and no unapproved policy or product decisions were introduced.
