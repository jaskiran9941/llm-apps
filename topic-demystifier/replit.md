# ExplainIt - Educational Explanation App

## Overview

ExplainIt is an AI-powered educational platform that transforms complex topics into engaging, easy-to-understand explanations. Users can submit topics via text or image uploads, and the application generates three distinct learning formats: comic strips with illustrated panels and speech bubbles, visual illustration galleries with detailed descriptions, and interactive slideshow presentations with text-to-speech narration. The platform emphasizes a playful yet clear design approach, inspired by educational platforms like Khan Academy and content platforms like Medium.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture

**Framework & Build System**
- React 18 with TypeScript for type-safe component development
- Vite as the build tool and development server for fast HMR (Hot Module Replacement)
- Client-side routing using Wouter (lightweight alternative to React Router)
- Single-page application (SPA) architecture with client-side state management

**UI Component Strategy**
- Shadcn/ui component library based on Radix UI primitives
- Tailwind CSS for utility-first styling with custom design tokens
- Component organization follows atomic design principles (atoms, molecules, organisms)
- Custom theme system supporting light/dark modes with CSS variables
- Typography system using Google Fonts (Nunito for headers, Inter for body text)

**State Management**
- TanStack Query (React Query) for server state management and API caching
- React hooks for local component state
- Context API for theme and global UI state (ThemeProvider)
- Separation of concerns: server state vs. client state

**Key Frontend Patterns**
- Controlled components for all form inputs
- Progressive disclosure in UI (simple input → rich output)
- Responsive design with mobile-first approach
- Accessibility considerations with ARIA labels and semantic HTML
- Loading states with staged progress indicators for multi-step AI generation

### Backend Architecture

**Server Framework**
- Express.js running on Node.js with TypeScript
- HTTP server created using Node's native `http` module
- Middleware-based request processing pipeline
- RESTful API design for client-server communication

**API Design**
- Single primary endpoint: `POST /api/explain` for topic explanation generation
- Request validation using Zod schemas
- Structured error handling with consistent error response format
- Rate limiting considerations for AI API calls

**AI Integration Strategy**
- OpenAI API integration using official SDK
- Replit AI Integrations service for OpenAI-compatible API access
- Multi-stage generation process:
  1. Image topic analysis (if image provided)
  2. Content generation (summaries, panels, slides)
  3. Parallel image generation with concurrency limiting
- Retry logic with exponential backoff for rate limit handling
- p-limit library for controlling concurrent AI requests

**Image Processing**
- Base64 encoding for image uploads
- Client-side image preview before submission
- Drag-and-drop file upload interface

### Data Storage Solutions

**Current Implementation**
- In-memory storage using Map data structures
- User data stored temporarily in MemStorage class
- No persistent database currently configured (schema prepared for PostgreSQL via Drizzle)

**Database Schema (Prepared but Unused)**
- Drizzle ORM configured for PostgreSQL
- Schema definitions in `shared/schema.ts`
- Migration system ready via drizzle-kit
- User table structure defined with authentication fields

**Session Management**
- Express-session middleware (currently unused)
- Prepared for connect-pg-simple for PostgreSQL session storage
- In-memory session store as fallback

### External Dependencies

**AI Services**
- **OpenAI API**: Primary AI service for content and image generation
  - GPT models for text generation (explanation content, comic scripts, slide content)
  - DALL-E or similar for image generation
  - Accessed via Replit AI Integrations proxy
  - Environment variables: `AI_INTEGRATIONS_OPENAI_BASE_URL`, `AI_INTEGRATIONS_OPENAI_API_KEY`

**Third-Party Libraries**
- **Radix UI**: Accessible component primitives (dialogs, tabs, tooltips, etc.)
- **TanStack Query**: Server state management with automatic caching and refetching
- **Zod**: Runtime type validation for API requests and responses
- **Embla Carousel**: Touch-friendly carousel for comic panels
- **p-limit**: Concurrency control for parallel API requests
- **p-retry**: Retry logic with configurable strategies

**Development Tools**
- **Replit Plugins**: Vite plugins for runtime error overlay, cartographer, and dev banner
- **ESBuild**: Server bundling for production builds
- **TSX**: TypeScript execution for development server

**Font Services**
- Google Fonts API for Nunito and Inter font families

**Potential Future Integrations**
- PostgreSQL database (schema prepared, DATABASE_URL environment variable expected)
- Authentication providers (Passport.js configured but unused)
- Email services (Nodemailer dependency present)
- Payment processing (Stripe dependency present)

### Build & Deployment

**Build Process**
- Two-stage build: client (Vite) and server (ESBuild)
- Client builds to `dist/public` for static serving
- Server bundles to `dist/index.cjs` with dependency allowlist
- Production mode serves pre-built static assets via Express

**Development Environment**
- Vite dev server with middleware mode integrated into Express
- Hot module replacement for client-side changes
- TypeScript compilation checking without emitting files
- Source maps for debugging

**Environment Configuration**
- Node environment detection (development vs. production)
- Replit-specific environment variables for AI integrations
- Database URL configuration (prepared but optional)