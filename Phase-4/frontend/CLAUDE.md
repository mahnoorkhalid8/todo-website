# Frontend Guidelines

## Stack
- Next.js 16+ (App Router)
- TypeScript
- Tailwind CSS
- Better Auth (Authentication)

## Project Structure
- `app/` - Next.js App Router pages
  - `layout.tsx` - Root layout
  - `page.tsx` - Home page
  - `login/` - Login page
  - `register/` - Registration page
  - `dashboard/` - Dashboard with tasks
- `components/` - Reusable UI components
  - `auth/` - Authentication components
  - `tasks/` - Task management components
  - `ui/` - General UI components
- `lib/` - Shared utilities and API client
  - `api.ts` - API client with authentication
  - `auth.ts` - Authentication utilities
- `styles/` - Global styles
- `public/` - Static assets

## API Client
- Use centralized API client in `lib/api.ts`
- All API calls go through the client
- Automatic JWT token attachment
- Error handling and user feedback

## Authentication
- User authentication state in `lib/auth.ts`
- Protected routes with authentication checks
- Token management (storage, refresh, removal)

## Styling
- Use Tailwind CSS utility classes
- Follow mobile-first responsive design
- Use consistent color palette and spacing

## Running
- Development: `npm run dev`
- Build: `npm run build`
- Start production: `npm start`

## Testing
- Component tests in `tests/components/`
- Integration tests in `tests/integration/`
- End-to-end tests in `tests/e2e/`