---
title: "Todo Backend API"
emoji: "📝"
colorFrom: "blue"
colorTo: "green"
sdk: "docker"
app_file: "Dockerfile"
pinned: false
---

# Todo Web Application

A modern full-stack todo web application with user authentication and task management functionality. This application allows users to register, authenticate, and manage their tasks in a responsive, secure interface.

## Features

- User registration and authentication
- Secure JWT-based session management
- Full task management (Create, Read, Update, Delete)
- Task completion toggling
- Responsive UI for mobile, tablet, and desktop
- User data isolation (each user sees only their tasks)

## Project Overview

This is a monorepo using GitHub Spec-Kit for spec-driven development. The application consists of:
- A Next.js 16+ frontend with TypeScript and Tailwind CSS
- A Python FastAPI backend with SQLModel ORM
- Neon Serverless PostgreSQL for data persistence
- JWT-based authentication with Better Auth

## Project Structure

```
todo-app/
├── backend/              # Python FastAPI server
│   ├── main.py           # FastAPI app entry point
│   ├── models.py         # SQLModel database models
│   ├── db.py             # Database connection management
│   ├── routes/           # API route handlers
│   ├── schemas/          # Pydantic request/response schemas
│   ├── services/         # Business logic
│   └── utils/            # Utility functions
├── frontend/             # Next.js 16 application
│   ├── app/              # App Router pages
│   ├── components/       # Reusable UI components
│   ├── lib/              # Shared utilities and API client
│   └── styles/           # Global styles
├── specs/                # Specification documents
│   └── 1-todo-web-app/   # Feature specifications
├── docker-compose.yml    # Container orchestration
└── README.md            # This file
```

## Getting Started

### Prerequisites

- Node.js 18+
- Python 3.11+
- Docker and Docker Compose
- Git

### Environment Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd todo-app
```

2. Set up the backend:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Set up the frontend:
```bash
cd frontend
npm install
```

4. Create environment files:
```bash
# In backend/
cp .env.example .env

# In frontend/
cp .env.local.example .env.local
```

### Running the Application

#### Option 1: Separate Terminals (Development)

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
uvicorn main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

#### Option 2: Docker Compose

```bash
docker-compose up --build
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Backend Documentation: http://localhost:8000/docs

## Development Workflow

1. Read spec: @specs/1-todo-web-app/spec.md
2. Review architecture: @specs/1-todo-web-app/plan.md
3. Check tasks: @specs/1-todo-web-app/tasks.md
4. Implement backend: @backend/CLAUDE.md
5. Implement frontend: @frontend/CLAUDE.md
6. Test and iterate

## API Documentation

The backend API provides endpoints for:
- Authentication: `/api/auth/` (register, login, logout)
- Tasks: `/api/tasks/` (CRUD operations)

Auto-generated documentation is available at http://localhost:8000/docs when the backend is running.

## Commands

- Frontend development: `cd frontend && npm run dev`
- Backend development: `cd backend && uvicorn main:app --reload`
- Run with Docker: `docker-compose up --build`
- Run tests: See individual package.json and requirements.txt files

## Hugging Face Space Deployment

⚠️ **Important**: This application is a full-stack web application with both frontend and backend components. Hugging Face Spaces is primarily designed for machine learning applications and demos, not for traditional web applications with separate frontend and backend services.

When deployed to Hugging Face Spaces:
- Only the backend API will be accessible
- The Next.js frontend will not run properly in the Hugging Face environment
- You can access the API at the root URL
- API documentation is available at `/docs`

For a complete deployment of both frontend and backend, consider using:
- **Frontend**: Vercel, Netlify
- **Backend**: Render, Railway, Heroku, or AWS

To deploy the backend API to Hugging Face Spaces, use the following configuration:

### Hugging Face Space Configuration

The repository includes:
- `app.py` - Entry point for Hugging Face deployment
- `space.yaml` - Space configuration file
- Updated `requirements.txt` with necessary dependencies

### Environment Variables for Hugging Face Deployment

Set these secrets in your Hugging Face Space settings:
- `DATABASE_URL` - PostgreSQL database connection string
- `SECRET_KEY` - JWT secret key
- `ALGORITHM` - JWT algorithm (default: HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES` - Token expiration time