# Full-Stack Application - copilot-instructions.md

## Project Overview
This is a full-stack web application with a React frontend and Node.js/Express backend.

## Technology Stack

### Frontend
- React 18 with TypeScript
- Vite for build tooling
- TanStack Query for data fetching
- Tailwind CSS for styling
- Zustand for global state

### Backend
- Node.js 24 LTS
- Express.js
- PostgreSQL with Prisma ORM
- Redis for caching
- JWT for authentication

### Infrastructure
- Docker for containerization
- GitHub Actions for CI/CD
- AWS (ECS, RDS, ElastiCache)

## Code Conventions

### TypeScript Style
- Strict mode enabled
- Explicit return types on functions
- Prefer `interface` over `type` for objects
- Use `readonly` where applicable

### File Naming
- Components: `PascalCase.tsx`
- Hooks: `useCamelCase.ts`
- Utils: `camelCase.ts`
- Constants: `UPPER_SNAKE_CASE.ts`

### Component Structure
```typescript
// Component file structure
import statements
type definitions
component function
helper functions
export
```

## Architecture Patterns

### Frontend Architecture
```text
src/
├── components/          # Reusable UI components
│   ├── ui/             # Base UI components
│   └── features/       # Feature-specific components
├── hooks/              # Custom React hooks
├── pages/              # Route pages
├── services/           # API service layer
├── stores/             # Zustand stores
├── types/              # TypeScript definitions
└── utils/              # Utility functions
```

### Backend Architecture
```text
src/
├── controllers/        # Request handlers
├── services/          # Business logic
├── repositories/      # Data access layer
├── middleware/        # Express middleware
├── routes/            # Route definitions
├── types/             # TypeScript types
└── utils/             # Utilities
```

## Common Patterns

### React Component
```typescript
import { FC } from 'react';
import { useQuery } from '@tanstack/react-query';

interface UserCardProps {
  userId: string;
  showActions?: boolean;
}

export const UserCard: FC<UserCardProps> = ({ userId, showActions = true }) => {
  const { data: user, isLoading } = useQuery({
    queryKey: ['user', userId],
    queryFn: () => userService.getUser(userId),
  });

  if (isLoading) return <Skeleton />;
  if (!user) return null;

  return (
    <Card>
      <CardHeader>{user.name}</CardHeader>
      {showActions && <UserActions user={user} />}
    </Card>
  );
};
```

### API Service
```typescript
// services/userService.ts
import { api } from '@/lib/api';
import type { User, CreateUserInput } from '@/types';

export const userService = {
  getUser: (id: string): Promise<User> =>
    api.get(`/users/${id}`).then(res => res.data),

  createUser: (input: CreateUserInput): Promise<User> =>
    api.post('/users', input).then(res => res.data),
};
```

### Express Controller
```typescript
// controllers/userController.ts
import { Request, Response, NextFunction } from 'express';
import { userService } from '../services/userService';

export const userController = {
  getUser: async (req: Request, res: Response, next: NextFunction) => {
    try {
      const user = await userService.findById(req.params.id);
      if (!user) {
        return res.status(404).json({ error: 'User not found' });
      }
      res.json(user);
    } catch (error) {
      next(error);
    }
  },
};
```

### Prisma Repository
```typescript
// repositories/userRepository.ts
import { prisma } from '../lib/prisma';
import type { User, Prisma } from '@prisma/client';

export const userRepository = {
  findById: (id: string): Promise<User | null> =>
    prisma.user.findUnique({ where: { id } }),

  create: (data: Prisma.UserCreateInput): Promise<User> =>
    prisma.user.create({ data }),
};
```

## State Management

### Zustand Store
```typescript
import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';

interface AuthState {
  user: User | null;
  token: string | null;
  login: (user: User, token: string) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  devtools(
    persist(
      (set) => ({
        user: null,
        token: null,
        login: (user, token) => set({ user, token }),
        logout: () => set({ user: null, token: null }),
      }),
      { name: 'auth-storage' }
    )
  )
);
```

## Error Handling

### Frontend
```typescript
// Use TanStack Query error handling
const { error } = useQuery({
  queryKey: ['data'],
  queryFn: fetchData,
  onError: (error) => {
    toast.error('Failed to load data');
    console.error(error);
  },
});
```

### Backend
```typescript
// Centralized error handler
export const errorHandler = (
  error: Error,
  req: Request,
  res: Response,
  next: NextFunction
) => {
  console.error(error.stack);

  if (error instanceof AppError) {
    return res.status(error.statusCode).json({
      error: error.message,
      code: error.code,
    });
  }

  res.status(500).json({ error: 'Internal server error' });
};
```

## Testing

### Frontend Testing
- Use Vitest and React Testing Library
- Mock API calls with MSW
- Test user interactions

### Backend Testing
- Use Jest
- Use Supertest for API testing
- Mock database with Prisma

## Important Notes
- Always handle loading and error states in components
- Use environment variables for configuration
- Implement proper validation on both client and server
- Use transactions for multi-step database operations
