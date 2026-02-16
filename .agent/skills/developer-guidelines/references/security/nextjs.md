# Next.js Security Quick-Reference

> Condensed from `References/security-best-practices/references/javascript-typescript-nextjs-web-server-security.md`.
> Load this when generating or reviewing Next.js code.

## LLM Anti-Patterns (DO NOT recommend these)

- ❌ Using `NEXT_PUBLIC_` prefix for secrets — everything with this prefix is embedded in the client bundle.
  - ✅ Server-only secrets: use env vars without `NEXT_PUBLIC_` prefix; access only in server components/API routes/`getServerSideProps`.
- ❌ Importing server-only modules in client components — secret leakage into the client bundle.
  - ✅ Use `import 'server-only'` at top of server-only modules to get a build-time error if accidentally imported client-side.
- ❌ Returning full DB objects from `getServerSideProps` — leaks internal fields to client via `__NEXT_DATA__`.
  - ✅ Always `pick`/`select` only the fields the client needs.
- ❌ Relying on Next.js middleware for authorization of API routes — middleware can be bypassed in certain configurations.
  - ✅ Always validate auth inside each API route handler / Server Action.
- ❌ Using `dangerouslySetInnerHTML` without sanitization in any component.

## Critical Grep Patterns

```
# Secret exposure
NEXT_PUBLIC_          # Client-visible — must NOT contain secrets
process.env.          # In client components = build-time embed
server-only           # Verify presence in server-only modules

# Data leakage
getServerSideProps    # Verify returned props don't include DB internals
getStaticProps        # Data is serialized to HTML — public
__NEXT_DATA__         # All props visible here — verify no secrets

# XSS
dangerouslySetInnerHTML  # Must sanitize with DOMPurify
innerHTML             # DOM XSS sink
serialize(            # State serialization — verify XSS-safe escaping

# Auth
getSession(           # Verify in every protected API route
getServerSession(     # NextAuth — verify in server components
middleware.ts         # Auth checks here are convenience, not security
cookies()             # Server-side cookie access — verify CSRF
headers()             # Server-side header access

# API Routes / Server Actions
export async function POST  # API route — verify auth check
'use server'          # Server Action — verify auth + input validation
redirect(             # Server Action redirect — verify URL validation
revalidatePath(       # Cache invalidation — verify auth before calling
revalidateTag(        # Cache invalidation — verify auth

# SSRF
fetch(                # In server components/API routes — verify URL source
remotePatterns        # next/image — verify not overly broad
images.domains        # Deprecated — use remotePatterns

# File handling
fs.readFile(          # Path traversal risk if path is user-controlled
path.join(            # Verify no user input in path construction
/api/upload           # Verify size/type limits

# Deployment
next.config.js        # Review all security-relevant settings
output: 'export'      # Static export — no server-side security
```

## Framework-Specific Edge Cases

1. **`NEXT_PUBLIC_` prefix** — Is a compile-time text replacement. The value is literally baked into JS bundles. There's no runtime protection.
2. **Server/Client boundary** — Files imported in client components get bundled for the browser. Use `import 'server-only'` guard on sensitive modules.
3. **`__NEXT_DATA__` script tag** — All `getServerSideProps` / `getStaticProps` return values are serialized into a visible `<script>` tag. Never return more than needed.
4. **Middleware auth bypass** — Middleware runs at the edge and can miss API routes based on `matcher` config. Always add auth checks inside handlers.
5. **`next/image` SSRF** — `remotePatterns` with `**` hostname allows fetching from any host via the image optimization API. Restrict to known domains.
6. **Server Actions (`'use server'`)** — Publicly callable endpoints. MUST validate auth and input inside each action. The `'use server'` directive alone provides no security.
7. **`redirect()` in Server Actions** — If redirect target comes from user input, validate it. Same open redirect risk as traditional routes.
8. **ISR/revalidation cache** — `revalidatePath()`/`revalidateTag()` can be called by anyone who reaches the endpoint. Verify auth before cache invalidation.

## Recommended Audit Order

1. `NEXT_PUBLIC_` env vars — verify none contain secrets
2. `getServerSideProps`/`getStaticProps` return values — verify no data over-fetching
3. `import 'server-only'` guards on sensitive server modules
4. Auth checks inside every API route and Server Action (not just middleware)
5. `dangerouslySetInnerHTML` usage — verify sanitization
6. `next/image` `remotePatterns` — verify restricted domains
7. CSRF protection for cookie-authenticated mutations
8. `redirect()` URL validation in Server Actions
9. Cache invalidation endpoints — verify auth protection
10. `next.config.js` security headers configuration
