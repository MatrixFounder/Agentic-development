# JavaScript / TypeScript Developer Guidelines

## Core Principles
- **Modern Syntax:** STRICTLY use ES6+ features (const/let, arrow functions, destructuring).
- **TypeScript First:** All new code MUST be TypeScript. Use `strict: true` in `tsconfig.json`.
    - **No Any:** Avoid `any` at all costs. Use `unknown` with narrowing if necessary.
    - **Utility Types:** Use `Pick<T>`, `Omit<T>`, `Partial<T>` for precise type modeling.
    - **Config:** Enable `noUncheckedIndexedAccess` to catch undefined array/object access errors.

- **Immutability:** Prefer immutable data structures. Use spread syntax `...` or `toSorted()`/`toSpliced()` (ES2023) instead of mutating array methods.

## Async Patterns
- **No Raw Promises:** Always use `async/await`. Avoid `.then()` chains unless strictly necessary.
- **Concurrent Execution:** Use `Promise.all()` for fail-fast or `Promise.allSettled()` for robust concurrent tasks.
- **Error Handling:** Use `try/catch` block for async operations. Ensure errors are typed or cast properly in TS.

## Ecosystem Standards
- **Validation:** Use **Zod** for runtime schema validation (API inputs, config).
- **Testing:** Prefer **Vitest** over Jest for speed and native ESM support.
- **Linting:** Use **Prettier** for formatting and **ESLint** for code quality.

## React/Frontend Patterns
- **Component Composition:** Prefer composing small components over prop drilling.
- **Custom Hooks:** Extract complex logic into custom hooks (`useFeature()`) to keep components clean.
- **State Management:** Use **TanStack Query** for server state; avoid global store (Redux/Zustand) for simple API data.

## Common Pitfalls
- **Floating Promises:** Always await promises or explicitly handle them (`void func()`).
- **Null Checks:** Use Optional Chaining `?.` and Nullish Coalescing `??` instead of bespoke logic.

## Specific Contexts (n8n / Scripts / Embedded)
- **Runtime Limits:** In `n8n` or simplified environments, TypeScript and Zod may not be available.
    - **Validation:** Use `Array.isArray(x)` and `typeof x === 'string'` for defensive coding.
    - **Imports:** Use platform-specific imports (e.g., `require` or `$input.all()`).
    - **JSDoc:** Use JSDoc comments `/** @type {string} */` for type safety without a build step.

