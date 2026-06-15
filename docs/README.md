# ETcash System Documentation

## Overview

ETcash is a Kenya-first financial application built as a hybrid web/desktop system. It combines:
- Django REST backend API (`backend/`)
- React + Vite frontend application (`frontend/`)
- Electron desktop shell (`electron/`)

The system supports invoicing, expenses, accounting, banking, inventory, payroll, multi-entity consolidation, and Kenya-specific tax workflows such as VAT 16% and WHT.

## Table of Contents

- [Overview](#overview)
- [System Components](#system-components)
- [Core Functionality](#core-functionality)
- [Technical Features](#technical-features)
- [System Requirements](#system-requirements)
- [Repository Structure](#repository-structure)
- [Installation](#installation)
  - [Clone the repository](#clone-the-repository)
  - [Backend setup](#backend-setup)
  - [Frontend setup](#frontend-setup)
  - [Desktop packaging](#desktop-packaging)
  - [Automated setup process](#automated-setup-process)
- [Configuration and Environment Variables](#configuration-and-environment-variables)
- [Database Setup](#database-setup)
- [Development Workflows](#development-workflows)
  - [Backend development](#backend-development)
  - [Frontend development](#frontend-development)
  - [Adding new dependencies](#adding-new-dependencies)
- [Testing](#testing)
- [API Documentation](#api-documentation)
- [Development Conventions](#development-conventions)
- [Deployment](#deployment)
- [Monitoring and Logging](#monitoring-and-logging)
- [License](#license)

## System Components

### Backend (`backend/`)

- Django 4.2.9
- Django REST Framework 3.14.0
- SQLite local database by default
- Token-based authentication using `rest_framework.authtoken`
- Core modules:
  - `accounting`
  - `invoicing`
  - `expenses`
  - `banking`
  - `inventory`
  - `projects`
  - `entities`
  - `payroll`
  - `reports`

### Frontend (`frontend/`)

- React 18.2.0
- Vite 5.0.11
- Tailwind CSS 3.4.1
- React Router DOM 6.21.3
- State and data handling via React Query, Zustand, and React Hook Form
- Export features with `jspdf`, `jspdf-autotable`, `papaparse`, and `file-saver`

### Electron (`electron/`)

- Electron 28.0.0
- `electron-builder` for packaged desktop installers
- Packages backend and frontend into a cross-platform desktop app

## Core Functionality

The system supports:

- Sales / invoicing
  - invoice creation
  - customer management
  - VAT treatment on invoices
  - invoice PDF export
- Purchasing / expenses
  - vendor expenses
  - WHT handling
  - expense reporting
- Accounting
  - chart of accounts
  - journal entries
  - posting and financial records
- Banking
  - account tracking
  - reconciliation
  - CSV import support
- Inventory
  - stock items
  - stock movements
- Projects
  - project budgets
  - job costing
- Payroll
  - employee payroll runs
  - PAYE / NSSF / NHIF handling (Kenya)
- Multi-entity operations
  - legal entities
  - consolidation workflows
- Reporting
  - profit & loss
  - balance sheet
  - cash flow
  - VAT and WHT reports

## Technical Features

- REST API backend with token authentication
- Local SQLite persistence with configurable database path
- CORS enabled for local frontend during development
- Token-based auth header: `Authorization: Token <key>`
- Frontend built and served by Vite in development
- Electron shell for desktop packaging
- No Redis or Celery is currently configured in this repository

## System Requirements

### Recommended

- Git
- Python 3.10+ (3.11 recommended)
- Node.js 18+ / npm 9+
- Windows / macOS / Linux

### Backend requirements

- `Django==4.2.9`
- `djangorestframework==3.14.0`
- `django-cors-headers==4.3.1`

### Frontend requirements

- `react`, `react-dom`
- `react-router-dom`
- `@tanstack/react-query`
- `@tanstack/react-table`
- `vite`, `@vitejs/plugin-react`
- `tailwindcss`, `postcss`, `autoprefixer`

### Desktop requirements

- `electron` 28.x
- `electron-builder` 24.x

## Repository Structure

```
cursor et cash/
├── backend/             # Django REST API
│   ├── accounting/
│   ├── banking/
│   ├── entities/
│   ├── expenses/
│   ├── invoicing/
│   ├── inventory/
│   ├── payroll/
│   ├── projects/
│   ├── reports/
│   ├── etcash/          # Django project settings
│   ├── requirements.txt
│   ├── manage.py
│   └── scripts/
├── frontend/            # React UI app
│   ├── src/
│   ├── package.json
│   ├── vite.config.js
│   └── tailwind.config.js
├── electron/            # Desktop packaging
│   ├── main.js
│   ├── preload.js
│   ├── package.json
│   └── resources/
├── scripts/             # Launcher scripts
│   ├── run_all.sh
│   ├── run_all.ps1
│   └── run_all          # alternate shell script
└── docs/
    └── README.md
```

## Installation

### Clone the repository

```bash
git clone https://github.com/your-org/rsmc-nairobi.git
cd rsmc-nairobi
```

> Replace the URL above with the actual repository URL for your project.

### Backend setup

```bash
cd backend
python -m venv .venv
# Unix/macOS
source .venv/bin/activate
# Windows PowerShell
# .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
```

### Frontend setup

```bash
cd frontend
npm install
```

### Desktop packaging setup

```bash
cd electron
npm install
```

### Run backend and frontend manually

```bash
# backend
cd backend
source .venv/bin/activate   # or .\.venv\Scripts\Activate.ps1
python manage.py runserver 127.0.0.1:8765

# frontend in another terminal
cd frontend
npm run dev -- --host 127.0.0.1
```

Open the app at: `http://localhost:5173`

### Default login

- Username: `admin`
- Password: `Admin1234!`

## Automated setup process

This repository currently uses launcher scripts in `scripts/`.

### Bash / Unix / Git Bash

```bash
chmod +x scripts/run_all.sh
./scripts/run_all.sh
```

### Windows PowerShell

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.
\scripts\run_all.ps1
```

The launcher performs:
- Python virtualenv activation
- backend migrations
- demo data seeding when configured
- frontend dependency install
- frontend development server startup
- backend development server startup

### Notes

- This repo does not currently include `scripts/setup.sh`.
- Use `scripts/run_all.sh` / `scripts/run_all.ps1` for fast local bootstrapping.

## Configuration and Environment Variables

The backend uses environment variables defined in `backend/etcash/settings.py`.

### Available variables

- `ETCASH_SECRET_KEY`
  - Default: `dev-only-change-in-production`
  - Use a strong secret in production.
- `ETCASH_DEBUG`
  - Default: `1`
  - Set to `0` for production.
- `ETCASH_DATA_DIR`
  - Base directory for data storage.
- `ETCASH_DB_PATH`
  - Explicit SQLite file path.

### Recommended production config

- Set `ETCASH_DEBUG=0`
- Set a secure `ETCASH_SECRET_KEY`
- Configure `ALLOWED_HOSTS` in `backend/etcash/settings.py`
- Consider replacing SQLite with PostgreSQL for production

## Database Setup

By default, the app uses SQLite.

### Default location

- `backend/etcash.db` or
- `ETCASH_DB_PATH` if set

### Migrations

```bash
cd backend
source .venv/bin/activate
python manage.py makemigrations
python manage.py migrate
```

### Demo seed data

```bash
cd backend
source .venv/bin/activate
python scripts/seed_demo_flow.py
```

## Development Workflows

### Backend development

1. Activate the backend virtual environment
2. Install new dependencies
3. Run migrations
4. Start the backend server

```bash
cd backend
source .venv/bin/activate
python manage.py runserver 127.0.0.1:8765
```

### Frontend development

```bash
cd frontend
npm install
npm run dev -- --host 127.0.0.1
```

### Adding new backend dependencies

1. Install the package: `pip install <package>`
2. Add it to `backend/requirements.txt`
3. Re-run `pip install -r requirements.txt`
4. Commit the updated `requirements.txt`

### Adding new frontend dependencies

1. Install the package: `npm install <package>`
2. Commit the updated `frontend/package.json` and `frontend/package-lock.json`

## Testing

- This repository does not currently include a configured backend or frontend test suite.
- Django supports tests via `python manage.py test` once test modules are added.
- Frontend testing tools should be added independently, such as Jest, React Testing Library, or Vitest.

## API Documentation

- The backend exposes API endpoints under `/api/`
- Authentication is by token header: `Authorization: Token <key>`
- There is no autogenerated Swagger/OpenAPI documentation included in the current repo
- Inspect `backend/*/views.py` and `backend/*/serializers.py` for endpoint details

### Core API endpoints

- `POST /api/core/auth/login/` — login and receive auth token
- `POST /api/core/auth/logout/` — logout current token
- `POST /api/core/auth/setup/` — initial setup endpoint for company creation
- `GET /api/core/company/` — fetch current company profile

### Feature module endpoints

The backend includes these high-level API namespaces:

- `/api/invoicing/`
- `/api/accounting/`
- `/api/expenses/`
- `/api/banking/`
- `/api/inventory/`
- `/api/projects/`
- `/api/entities/`
- `/api/payroll/`
- `/api/reports/`
- `/api/tax/`

### Tax endpoints

- `GET /api/tax/insights/`
- `GET /api/tax/vat-report/`
- `GET /api/tax/wht-report/`

### Sample cURL usage

```bash
curl -X POST http://127.0.0.1:8765/api/core/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "Admin1234!"}'
```

```bash
curl http://127.0.0.1:8765/api/core/company/ \
  -H "Authorization: Token <your-token>"
```

## Deployment

This project is currently optimized for local development and desktop packaging.

### Production readiness

For production deployment, you should:
- set `ETCASH_DEBUG=0`
- use a secure `ETCASH_SECRET_KEY`
- lock down `ALLOWED_HOSTS`
- move to a production DB such as PostgreSQL
- serve the frontend as static assets behind a web server
- run Django under a real WSGI server (`gunicorn`, `uwsgi`, etc.)

### Electron packaging

From `electron/`:

```bash
cd electron
npm install
npm run build:desktop
```

### Platform-specific packaging

```bash
npm run build:win
npm run build:mac
npm run build:linux
```

## SSL / TLS

- SSL/TLS is not configured in the current repository.
- For production web deployment, add HTTPS termination with a reverse proxy such as Nginx or Traefik.
- For desktop apps, the Electron shell runs locally and does not require TLS for local host-only API calls.

## Monitoring and Logging

- The current codebase uses Django default logging behavior.
- There is no external monitoring or logging pipeline configured.
- For production, add structured logging, error reporting, and metrics.

## Important Notes

- The repository currently does not use Redis or Celery.
- There is no `scripts/setup.sh` file bundled in this version.
- The recommended local startup commands are `scripts/run_all.sh` and `scripts/run_all.ps1`.

## Development Conventions

### Branching

- Use feature branches for new work, e.g. `feature/invoice-pdf-export`.
- Use `bugfix/` for bug fixes, `hotfix/` for urgent production fixes, and `release/` for staging release branches.
- Keep branch names descriptive and scoped to a single area.

### Commit messages

- Use clear, imperative commits like:
  - `Add invoice PDF export button`
  - `Fix CSV export formatting for KRA WHT report`
  - `Update backend API auth flow`
- Keep messages concise but informative.
- Include issue or ticket IDs if your team uses them.

### Pull requests / code review

- Open one PR per logical change.
- Include a short summary, testing steps, and any manual verification instructions.
- Keep PRs small and focused to make review easier.

### Code style and quality

- Follow Python and Django idioms in backend code.
- Keep React components reusable and avoid large combined components.
- Use existing folder conventions in `backend/` and `frontend/src/`.
- Add comments only for non-obvious business logic or edge cases.

### Documentation updates

- Update `docs/README.md` when setup, workflow, or architecture changes.
- Document new backend API routes in the API Documentation section.
- Document new frontend build or run instructions in the Installation and Development sections.

## License

- No license file is included in this repository at this time.
- Add a `LICENSE` file before sharing or deploying commercially.
