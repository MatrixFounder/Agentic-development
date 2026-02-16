# React Security Quick-Reference

> Condensed from `References/security-best-practices/references/javascript-typescript-react-web-frontend-security.md`.
> Load this when generating or reviewing React code.

## LLM Anti-Patterns (DO NOT recommend these)

- ❌ Using `dangerouslySetInnerHTML` without DOMPurify — direct XSS vector.
  - ✅ Sanitize with DOMPurify first: `<div dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(html) }} />`
- ❌ Storing tokens in `localStorage` — any XSS exfiltrates them.
  - ✅ Prefer HttpOnly cookies (server-set) + CSRF protection; or short-lived in-memory tokens.
- ❌ Treating `REACT_APP_*` / `VITE_*` / `NEXT_PUBLIC_*` env vars as secret — they're embedded in the build.
  - ✅ Secrets belong server-side. These env vars are PUBLIC.
- ❌ Rendering user-provided URLs in `href` without scheme validation — `javascript:` URLs execute code.
  - ✅ Parse with `new URL()`, allowlist `https:` scheme, block `javascript:` and `data:`.
- ❌ Enabling raw HTML passthrough in markdown renderers (`rehype-raw`, `allowDangerousHtml`, `sanitize: false`).
  - ✅ Disable raw HTML or pipe through DOMPurify.

## Critical Grep Patterns

```
# XSS escape hatches
dangerouslySetInnerHTML  # Must have DOMPurify sanitization
__html:               # Same as above — trace input source
innerHTML             # Direct DOM XSS sink
outerHTML             # Direct DOM XSS sink
insertAdjacentHTML    # Direct DOM XSS sink
document.write        # Direct DOM XSS sink

# Markdown renderers (raw HTML passthrough)
rehype-raw            # Enables raw HTML in react-markdown
allowDangerousHtml    # Various markdown libs
sanitize: false       # Disables built-in sanitization

# Env vars / secrets
REACT_APP_            # CRA — client-visible, NOT secret
VITE_                 # Vite — client-visible, NOT secret
NEXT_PUBLIC_          # Next.js — client-visible, NOT secret
process.env.          # Check what reaches client bundle
import.meta.env.      # Vite env access

# Token storage
localStorage.setItem  # XSS-exfiltrable — avoid for tokens
sessionStorage.setItem # Same risk as localStorage
getItem(              # Check if retrieving auth tokens

# URL injection
href={                # Verify not user-controlled without validation
src={                 # Same risk for images/iframes/scripts
window.location       # Open redirect risk
window.open           # Same redirect risk
navigate(             # React Router — validate destination

# CSRF
credentials: 'include'   # Cookie-sent request — needs CSRF token
withCredentials: true     # Axios equivalent — needs CSRF

# postMessage
postMessage(          # Verify targetOrigin is not "*"
addEventListener('message'  # Verify event.origin validation

# Code execution
eval(                 # Never with user input
new Function          # Same as eval
setTimeout("          # String form = eval equivalent
```

## Framework-Specific Edge Cases

1. **React's auto-escaping** — JSX `{value}` is escaped by default. The danger is when developers bypass it via `dangerouslySetInnerHTML`, DOM APIs, or URL attributes.
2. **`javascript:` in `href`** — React does NOT block `<a href="javascript:alert(1)">`. Must validate scheme explicitly.
3. **Markdown + `rehype-raw`** — `react-markdown` with `rehype-raw` plugin passes raw HTML through. Sanitize with DOMPurify or disable.
4. **`postMessage` with `"*"`** — Sends to any origin. Always specify exact target origin. On receive, check `event.origin` against allowlist.
5. **Service workers** — Cache user-specific data carefully. Stale caches with auth data can leak across sessions.
6. **CSP + Trusted Types** — Best defense-in-depth. Start CSP in report-only mode, then enforce. Use Trusted Types to lock down `innerHTML` sinks.
7. **Source maps in production** — Reveal code structure, internal URLs. Either don't publish or restrict access.
8. **Third-party scripts** — Tag managers (GTM, Segment) run with your origin's privileges. Minimize, pin versions, use SRI.

## Recommended Audit Order

1. `dangerouslySetInnerHTML` — verify DOMPurify sanitization on all instances
2. Env vars — verify no secrets in `REACT_APP_`/`VITE_`/`NEXT_PUBLIC_` prefixed vars
3. Token storage — verify no auth tokens in `localStorage`/`sessionStorage`
4. URL injection — `href={`, `src={` with user-controlled values
5. Markdown renderers — verify raw HTML passthrough is disabled or sanitized
6. CSRF — `credentials: 'include'` paired with CSRF tokens
7. `postMessage` — origin validation on both send and receive
8. Third-party scripts — SRI, pinned versions, minimal vendors
9. CSP — verify presence and no `unsafe-inline`/`unsafe-eval`
