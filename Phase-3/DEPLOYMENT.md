# Deployment Guide for AI-Powered Todo App

This guide provides instructions for deploying the AI-powered Todo application with chatbot functionality.

## Prerequisites

- Docker and Docker Compose
- API keys for AI services (Google Gemini and/or Groq)
- Access to a PostgreSQL database (NeonDB recommended)

## Environment Configuration

Create a `.env` file in the root directory with the following variables:

```bash
# Database Configuration
DATABASE_URL=your_postgresql_connection_string

# JWT Configuration
JWT_SECRET=your_jwt_secret_key
BETTER_AUTH_SECRET=your_auth_secret

# AI Service API Keys
GOOGLE_GEMINI_API_KEY=your_google_gemini_api_key
GROQ_API_KEY=your_groq_api_key

# MCP Server Configuration
MCP_SERVER_SECRET=your_mcp_server_secret

# Security Configuration
SESSION_SECRET=your_session_secret
CONVERSATION_ENCRYPTION_KEY=your_conversation_encryption_key

# Application URLs
FRONTEND_URL=http://localhost:3000  # Use HTTP for local development
BACKEND_URL=http://localhost:8000    # Use HTTP for local development
# For production deployments, use HTTPS:
# NEXT_PUBLIC_API_URL=https://your-domain.com
```

## Local Deployment with Docker

1. Ensure you have Docker and Docker Compose installed
2. Place your `.env` file in the root directory
3. Run the following command from the project root:

```bash
docker-compose up --build
```

4. The application will be available at:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - Health check: http://localhost:8000/health

## Production Deployment

### Option 1: Deploy to Railway

1. Install the Railway CLI or connect your GitHub repository
2. Set the environment variables in Railway dashboard
3. Deploy using the Railway interface

### Option 2: Deploy to Heroku

1. Install Heroku CLI
2. Create a new Heroku app
3. Set config vars with `heroku config:set`
4. Deploy with `git push heroku main`

### Option 3: Deploy to AWS/GCP

1. Set up ECS/Fargate or GKE cluster
2. Build and push Docker images to container registry
3. Deploy using the provided docker-compose.yml as reference

## Database Migration

When deploying to a new environment, run database migrations:

```bash
# Using Docker
docker-compose exec backend alembic upgrade head
```

## AI Service Configuration

The application supports multiple AI providers:

1. **Google Gemini**: Set `GOOGLE_GEMINI_API_KEY` in environment
2. **Groq**: Set `GROQ_API_KEY` in environment

The system will use the first available service. If neither is configured, it falls back to rule-based processing.

## Health Checks

- Backend health: `GET /health`
- Chat service health: `GET /api/chat/health`
- Database connectivity: Built into startup routine

## Security Best Practices

1. Use strong, unique secrets for all secret keys
2. Enable HTTPS in production
3. Ensure API URLs use HTTPS to prevent mixed content errors
4. Implement proper rate limiting
5. Sanitize all user inputs
6. Regularly rotate API keys

## Scaling Recommendations

- Use a load balancer for multiple backend instances
- Implement Redis for session storage and rate limiting
- Scale database separately from application
- Consider CDN for frontend assets

## Troubleshooting

### Common Issues

1. **Database Connection**: Verify `DATABASE_URL` is correct
2. **AI Services Not Working**: Check API keys and billing
3. **Frontend Cannot Reach Backend**: Verify CORS settings
4. **Authentication Issues**: Check JWT configuration

### Logs

- Backend logs: `docker-compose logs backend`
- Frontend logs: `docker-compose logs frontend`
- Database logs: `docker-compose logs db`

## Updating the Application

1. Pull the latest code
2. Update environment variables if needed
3. Run: `docker-compose down && docker-compose up --build`

## Backup and Recovery

- Database backups should be configured in your PostgreSQL provider
- Store environment variables securely in a password manager
- Version control application code regularly