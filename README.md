
TicketEase --- AI-Powered Ticketing & Booking Assistant
TicketEase is a web-based ticketing and booking application designed for
students and college communities. It helps users discover events and
venues and supports the ticket-booking workflow.

Project structure
AI-powered-Online-Tickting-and-Booking-Assistant/
├── app/                  # Next.js frontend (if present at repository root)
├── backend/              # FastAPI backend
│   ├── app/
│   ├── requirements.txt
│   └── Dockerfile
└── README.md
The frontend is configured as a Next.js application at the repository
root. If your checked-out branch has a different frontend directory,
run the frontend commands from that directory instead.

Requirements
Node.js (LTS) and npm
Python 3.11
PostgreSQL
Redis
For local development, PostgreSQL and Redis must be running and
reachable using the URLs configured for the backend. Alternatively, use
cloud PostgreSQL and Redis connection URLs.

1. Start the frontend
Open a terminal in the repository root (the folder containing the
frontend package.json).

Install dependencies:

npm install
Start the Next.js development server:

npm run dev
Open http://localhost:3000 in your browser.

For a production build:

npm run build
npm start
Stop the development server with Ctrl + C.

2. Start the backend
Open a second terminal in the repository root.

Windows PowerShell
cd backend
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
If PowerShell blocks virtual-environment activation:

Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
Start FastAPI:

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
Backend URL: http://localhost:8000

API documentation (if enabled): http://localhost:8000/docs

3. Backend environment variables
The backend reads configuration from environment variables / a .env
file. Use backend/.env.example as the reference for supported variable
names.

Configure the database and Redis URLs for the environment where the
backend runs:

DATABASE_URL
REDIS_URL
CELERY_BROKER_URL
CELERY_RESULT_BACKEND
The application also supports settings such as ENVIRONMENT, DEBUG,
and AI provider/API-key settings. Put secrets in a local .env file or
your hosting provider's environment-variable settings. Do not commit
.env files or publish passwords, API keys, or connection strings.

The backend uses asynchronous PostgreSQL access; its connection URL
commonly uses the postgresql+asyncpg:// scheme. Follow the project's
configuration requirements.

4. Run frontend and backend together
Use two terminals.

Terminal 1 --- frontend (repository root):

npm run dev
Terminal 2 --- backend:

cd backend
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
Then visit http://localhost:3000.

If the frontend cannot reach the backend, check the frontend's API base
URL and the backend's CORS configuration. The local backend address is
http://localhost:8000.

5. Deployment notes
The frontend is deployed separately as a Next.js application (for
example, on Vercel).
The backend is a FastAPI service (for example, on Render) using
backend/Dockerfile.
A deployed backend needs reachable cloud PostgreSQL and Redis
services. Local localhost database/Redis URLs will not work from a
cloud host.
Configure production secrets and service URLs in the hosting
provider's environment-variable settings.
Set the frontend's API base URL to the deployed backend URL before
using it in production.
Troubleshooting
npm is not recognized
Install Node.js LTS, reopen the terminal, then check:

node --version
npm --version
uvicorn is not recognized
Activate the backend virtual environment and install requirements:

cd backend
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Database or Redis connection errors
Confirm that the services are running and that DATABASE_URL and
REDIS_URL point to reachable services. Do not use localhost for a
cloud deployment unless the service is actually running in the same
host/network.

Frontend loads but booking/API actions fail
Confirm that the backend is running, the frontend API base URL is
correct, CORS permits the frontend origin, and the backend has valid
database and Redis connections.

For development, start the frontend and backend in separate terminals.
Keep all credentials private and out of source control.

Toggle sidebar
Ctrl+Shift+S
