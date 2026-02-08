# Quickstart Guide: Todo Web Application

## Overview
This guide provides step-by-step instructions to set up and run the Todo Web Application for development.

## Prerequisites
- Node.js 18+ (for frontend development)
- Python 3.11+ (for backend development)
- PostgreSQL-compatible database (Neon Serverless recommended)
- Docker and Docker Compose (optional, for containerized development)
- Git

## Environment Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd todo-app
```

### 2. Set up Backend
```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Set up Frontend
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install
```

## Configuration

### 1. Environment Variables

Create `.env` files in both backend and frontend directories:

**Backend (.env)**:
```env
DATABASE_URL=postgresql://username:password@localhost:5432/todo_app
SECRET_KEY=your-super-secret-jwt-signing-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

**Frontend (.env.local)**:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_BASE_URL=http://localhost:3000
```

### 2. Database Setup
The application uses Neon Serverless PostgreSQL. You can either:
- Use a local PostgreSQL instance
- Set up a free Neon account and connect to the serverless database
- Use Docker Compose to run PostgreSQL locally

## Running the Application

### Option 1: Separate Terminals (Recommended for Development)

**Terminal 1 - Backend**:
```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
uvicorn main:app --reload --port 8000
```

**Terminal 2 - Frontend**:
```bash
cd frontend
npm run dev
```

### Option 2: Using Docker Compose
```bash
# From the project root
docker-compose up --build
```

## API Endpoints

### Authentication Endpoints
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout

### Task Management Endpoints
- `GET /api/tasks` - List user's tasks
- `POST /api/tasks` - Create a new task
- `GET /api/tasks/{id}` - Get specific task
- `PUT /api/tasks/{id}` - Update task details
- `DELETE /api/tasks/{id}` - Delete a task
- `PATCH /api/tasks/{id}/complete` - Toggle task completion

## Development Commands

### Backend Development
```bash
# Run tests
pytest

# Format code
black .

# Lint code
flake8 .
```

### Frontend Development
```bash
# Run development server
npm run dev

# Run tests
npm run test

# Build for production
npm run build

# Lint code
npm run lint
```

## Database Migrations
If using Alembic for database migrations:
```bash
# Generate migration
alembic revision --autogenerate -m "Migration description"

# Apply migration
alembic upgrade head
```

## Testing

### Running Tests
```bash
# Backend tests
cd backend
python -m pytest

# Frontend tests
cd frontend
npm run test
```

## Troubleshooting

### Common Issues
1. **Port already in use**: Check if ports 3000 (frontend) and 8000 (backend) are available
2. **Database connection errors**: Verify DATABASE_URL in backend .env file
3. **Authentication issues**: Ensure JWT secret keys match between frontend and backend

### Reset Development Data
```bash
# Clear database (be careful!)
# For local PostgreSQL:
dropdb todo_app
createdb todo_app
```

## Next Steps
1. Implement user authentication flow
2. Create task management components
3. Add responsive design for mobile support
4. Implement proper error handling
5. Add loading states and user feedback