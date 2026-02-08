# ADR 004: Authentication Approach - JWT Tokens with Better Auth

## Status
Accepted

## Date
2026-01-05

## Context
We need to implement a secure authentication system for the Todo Web Application that provides user registration, login, session management, and protected API access. The system must ensure secure user identification, protect sensitive data, support stateless API operations, and provide a good user experience across different device sizes. The authentication solution should be scalable, secure against common attacks, and integrate well with our Next.js frontend and FastAPI backend.

## Decision
We will use JWT (JSON Web Tokens) with Better Auth as our authentication approach.

Specifically:
- Authentication Method: JWT tokens stored in HTTP-only cookies
- Library: Better Auth for comprehensive authentication handling
- Token Algorithm: HS256 with secure secret key
- Token Expiration: 24 hours (1440 minutes) with refresh capability
- Security: HTTPS enforcement, secure cookie attributes, CSRF protection
- Integration: Frontend token management with automatic API attachment

## Rationale
JWT tokens provide stateless authentication that works well with our RESTful API architecture. They contain user information within the token itself, reducing database lookups for authentication verification while maintaining security through cryptographic signatures.

Better Auth provides a comprehensive authentication solution that handles user registration, password hashing, session management, and security best practices out of the box. It integrates seamlessly with both Next.js and FastAPI, providing consistent authentication across our full-stack application.

HTTP-only cookies provide security against XSS attacks by preventing client-side JavaScript access to the token, while still allowing automatic token inclusion in API requests.

The approach supports our multi-user requirements with proper data isolation at the API level, ensuring users can only access their own data.

## Alternatives Considered
- Session-based authentication: Requires server-side session storage, doesn't scale well with stateless APIs
- OAuth providers only: Doesn't support direct email/password registration as required
- Custom JWT implementation: More complex, potential security vulnerabilities without proper expertise
- Third-party auth services (Auth0, Firebase): Additional costs, potential vendor lock-in
- Simple API keys: Less secure, doesn't support user registration/login flows

## Consequences
Positive:
- Stateless authentication supporting horizontal scaling
- Secure token handling with HTTP-only cookies
- Comprehensive auth solution with registration/login flows
- Good integration with Next.js and FastAPI
- Proper user data isolation in API layer
- Protection against CSRF and XSS attacks
- Support for token refresh and expiration

Negative:
- JWT tokens cannot be invalidated before expiration without additional complexity
- Larger token size compared to session IDs
- Potential complexity in token refresh management
- Dependency on Better Auth library
- Need for secure secret key management

## References
- specs/1-todo-web-app/spec.md
- specs/1-todo-web-app/data-model.md
- backend/routes/auth.py
- backend/services/auth_service.py
- frontend/lib/auth.ts
- frontend/lib/api.ts