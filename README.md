# ETcash — Kenya-first Financial System

Desktop finance suite (React + Django + Electron) for invoicing, accounting, banking, inventory, payroll, multi-entity consolidation, and Kenya tax (VAT 16%, WHT).

## Project layout

```
cursor et cash/
├── backend/     Django API (SQLite, port 8765)
├── frontend/    React + Vite UI
└── electron/    Desktop shell
```

## Quick start

### All-in-one launcher (recommended)

Runs backend, frontend, and admin setup with a single command:

**Windows (PowerShell):**
```powershell
.\scripts\run_all.ps1
```

**macOS / Linux / Git Bash:**
```bash
./scripts/run_all.sh
```

Then open: **http://localhost:5173**

**Login credentials:**
- Username: `admin`
- Password: `Admin1234!`

### Manual setup

If you prefer to run each component separately:

**Backend:**
```powershell
cd backend
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 127.0.0.1:8765
```

**Frontend (in another terminal):**
```powershell
cd frontend
npm install
npm run dev
```

Then open: **http://localhost:5173**

### Demo data

```powershell
cd backend
python scripts/seed_demo_flow.py
```

## Modules

| Area | Features |
|------|----------|
| **Sales** | Customers, invoices with VAT lines, mark sent/paid |
| **Purchases** | Expenses (VAT/WHT), vendors, bills |
| **Accounting** | Chart of accounts, journal entries (post) |
| **Banking** | Accounts, reconciliation, CSV import |
| **Inventory** | Items, stock movements (SME+) |
| **Projects** | Budgets, job costing (SME+) |
| **Payroll** | Employees, PAYE/NSSF/NHIF runs (SME+) |
| **Entities** | Legal entities, consolidation (Multi-Entity) |
| **Reports** | P&L, balance sheet, cash flow, VAT & WHT |
| **Insights** | Live alerts from your books |
| **Settings** | Company profile |

## Installation modes

- **Freelancer** — core sales, purchases, reports
- **SME** — + inventory, projects, payroll
- **Multi-Entity** — + entities & consolidation

## Desktop app

```powershell
cd frontend && npm install && npm run build
cd ..\electron && npm install && npm start
```

## Package installer

Build a packaged desktop installer after building the frontend:

```powershell
cd electron
npm run build:desktop
```

For platform-specific installers use `npm run build:win`, `npm run build:mac`, or `npm run build:linux` from the `electron` folder.

## API

- Base: `http://127.0.0.1:8765/api`
- Auth: `Authorization: Token <key>`
