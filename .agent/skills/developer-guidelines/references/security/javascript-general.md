# Frontend JavaScript/TypeScript Security Quick-Reference

> Condensed from `References/security-best-practices/references/javascript-general-web-frontend-security.md`.
> Load this when generating or reviewing vanilla JS/TS frontend code (no framework).

## LLM Anti-Patterns (DO NOT recommend these)

- ❌ Using `innerHTML` for inserting user-provided text — XSS vector.
  - ✅ Use `textContent` for text. Use `createElement` + `appendChild` for structured DOM.
- ❌ Using `eval()`, `new Function()`, or string `setTimeout("...")` — code injection.
  - ✅ Use `JSON.parse()` for JSON, structured dispatch for dynamic behavior, function-ref `setTimeout`.
- ❌ Storing session tokens in `localStorage` — single XSS exfiltrates everything.
  - ✅ Server-set `HttpOnly` cookies for session. Short-lived in-memory tokens if cookies impractical.
- ❌ Using `postMessage(data, "*")` — sends to any origin.
  - ✅ Always specify exact target origin. On receive, validate `event.origin` against an allowlist.
- ❌ Relying on CSP via `<meta>` tag for `frame-ancestors` — it's ignored in meta-delivered CSP.
  - ✅ Set `frame-ancestors` via HTTP headers only. Meta CSP cannot protect against clickjacking.

## Critical Grep Patterns

```
# DOM XSS sinks
innerHTML             # Use textContent instead
outerHTML             # Same risk as innerHTML
insertAdjacentHTML    # Same risk
document.write        # Never in production
document.writeln      # Same as document.write

# Code execution
eval(                 # Never with user input
new Function          # Same as eval
setTimeout("          # String form = eval; use function reference
setInterval("         # Same risk

# Event handler injection
setAttribute("on      # onclick/onload etc. from strings — use addEventListener
.onclick =            # If RHS is string — code execution
.onload =             # Same risk

# URL / Navigation
window.location       # Open redirect if user-controlled
location.href         # Same risk
location.assign       # Same risk
location.replace      # Same risk
javascript:           # Must be blocked in all URL contexts
window.open           # Validate URL before opening

# postMessage
postMessage(          # Verify targetOrigin is not "*"
addEventListener("message"  # Verify event.origin validation
.includes("trusted    # Substring origin check — INSECURE
event.data            # Treat as untrusted; never innerHTML/eval

# Storage
localStorage.setItem  # Never store secrets/tokens
localStorage.getItem  # Treat retrieved values as untrusted
sessionStorage        # Same risks as localStorage

# Third-party scripts
<script src="https:   # Verify integrity= (SRI) present
createElement("script")  # Dynamic script injection — verify URL
.src =                # Script source assignment — verify trusted

# CSP / Security headers
Content-Security-Policy  # Verify present (header or meta)
unsafe-inline         # Weakens CSP significantly — avoid
unsafe-eval           # Allows eval/Function — avoid
meta http-equiv       # Limited: no frame-ancestors, no report-uri/only

# DOM clobbering
window.               # Named property access — can be clobbered
document.             # Same risk
|| "/default"         # Fallback pattern — clobberable
```

## Framework-Specific Edge Cases

1. **CSP via `<meta>` limitations** — `frame-ancestors`, `report-uri`, `sandbox` are IGNORED in meta-delivered CSP. Only HTTP headers support them.
2. **Meta CSP placement** — Must appear before any `<script>` tags to govern them. Scripts above the meta are unprotected.
3. **DOM clobbering** — `<a id="redirectTo" href="javascript:alert(1)">` makes `window.redirectTo` resolve to the anchor element. If code does `location.assign(window.redirectTo || "/")`, it navigates to `javascript:`.
4. **`textContent` vs `innerText`** — Both are safe for text insertion. `textContent` is faster and doesn't trigger reflow. Prefer it.
5. **Trusted Types** — CSP `require-trusted-types-for 'script'` makes `innerHTML` reject raw strings. Must create policies via `trustedTypes.createPolicy()`.
6. **SRI hash format** — Use `sha384-` or `sha512-`. Update hashes when pinned script versions change. Wrong hash = script won't load.
7. **`window.name`** — Persists across navigations. Treat as attacker-controlled input since any previous page could have set it.
8. **`document.baseURI`** — Can be manipulated via `<base>` tag injection. Don't trust for security-sensitive URL resolution.

## Recommended Audit Order

1. DOM XSS sinks: `innerHTML`, `document.write`, `insertAdjacentHTML` with user data
2. Code execution: `eval`, `new Function`, string `setTimeout`/`setInterval`
3. URL/navigation: `window.location` assignment with user-controlled values
4. `postMessage`: origin validation on receive, explicit targetOrigin on send
5. Event handler attributes: `setAttribute("onclick", ...)` with user data
6. Storage: `localStorage`/`sessionStorage` for secrets/tokens
7. CSP: presence, no `unsafe-inline`/`unsafe-eval`, correct delivery method
8. Third-party scripts: SRI present, pinned versions, minimal vendors
9. DOM clobbering: `window.*` fallback patterns used in security-sensitive paths
