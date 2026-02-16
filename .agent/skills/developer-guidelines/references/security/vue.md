# Vue.js Security Quick-Reference

> Condensed from `References/security-best-practices/references/javascript-typescript-vue-web-frontend-security.md`.
> Load this when generating or reviewing Vue code.

## LLM Anti-Patterns (DO NOT recommend these)

- ❌ Using `v-html` with user-provided content — direct XSS vector, Vue's #1 security warning.
  - ✅ Use text interpolation `{{ }}` (auto-escaped). If HTML needed, sanitize with DOMPurify first.
- ❌ Using user-provided strings as Vue templates — equivalent to arbitrary JS execution.
  - ✅ Templates are code. Keep them developer-controlled. Use runtime-only build (no compiler in browser).
- ❌ Mounting Vue on server-rendered DOM containing user HTML — "safe" HTML becomes unsafe as a Vue template.
  - ✅ Mount Vue into a sterile root element. Render UGC from Vue components with sanitization.
- ❌ Using `VITE_` env vars for secrets — they end up in the client bundle.
  - ✅ Secrets stay server-side. `VITE_*` vars are PUBLIC.
- ❌ Running `vite preview` or `npm run dev` as production server.
  - ✅ Build with `vite build`, serve `dist/` with production-grade server/CDN.

## Critical Grep Patterns

```
# XSS sinks
v-html                # Must sanitize input with DOMPurify
innerHTML             # Direct DOM XSS — even in render functions
insertAdjacentHTML    # DOM XSS sink
document.write        # DOM XSS sink
h('div', { innerHTML  # Render function HTML injection

# Template injection (CRITICAL)
template:             # If value is not static string — SSTI risk
compile(              # Runtime template compilation — very dangerous
@vue/compiler-dom     # Runtime compiler import — review necessity

# URL injection
:href="               # Bound href — verify not user-controlled
:src="                # Bound src — verify validated
window.location       # Open redirect risk
router.push(          # Validate destination if from user input
route.query.next      # Classic redirect parameter — validate
route.query.redirect  # Same risk

# Env vars / secrets
VITE_                 # Client-visible — NOT secret
import.meta.env       # Check what reaches client bundle
.env.production       # Verify no secrets committed
envPrefix             # Vite config — must not be empty/broad

# Auth & tokens
localStorage          # XSS-exfiltrable — avoid for session tokens
sessionStorage        # Same risk
pinia-plugin-persist  # May persist auth state in localStorage

# CSRF
credentials: 'include'  # Cookie auth — needs CSRF protection
withCredentials       # Axios — same as above
X-CSRF-Token          # Verify present on state-changing requests

# Style injection
:style="              # If bound to user-controlled value — UI redress
:onclick="            # Dynamic event handler — very dangerous
:onmouseenter="       # Same as above

# Deployment
vite preview          # NOT a production server
npm run dev           # NOT for production
__VUE_PROD_DEVTOOLS__ # Must be false/absent in production
vue.global.js         # Non-prod build — use .prod.js variant
```

## Framework-Specific Edge Cases

1. **`v-html` ≠ React's `dangerouslySetInnerHTML`** — Both are dangerous, but Vue's name doesn't warn you. Vue docs explicitly call this out as the #1 pitfall.
2. **Untrusted templates = RCE** — `createApp({ template: userString })` is equivalent to `eval(userString)`. Never compile user-provided templates.
3. **Mounting on non-sterile DOM** — If server renders `<div id="app">{{ user_comment }}</div>` and Vue mounts on `#app`, the comment becomes a Vue template expression.
4. **`vite preview`** — Explicitly documented as NOT production-ready. It lacks security hardening, rate limiting, etc.
5. **`__VUE_PROD_DEVTOOLS__`** — Feature flag that enables devtools in production. Must be `false` in production builds.
6. **`:style` binding** — User-controlled CSS strings can perform UI redress attacks. Use object syntax with allowlisted properties only.
7. **SSR state serialization** — `__INITIAL_STATE__` injected into `<script>` tags must be robustly escaped. XSS if attacker controls serialized values.
8. **Vue Router guards** — `beforeEach` is UX only. Backend must enforce authorization independently.

## Recommended Audit Order

1. `v-html` — verify all instances have DOMPurify sanitization
2. Template injection — verify no dynamic template compilation with user input
3. Env vars — verify no secrets in `VITE_*` variables
4. URL injection — `:href`/`:src` with user-controlled values, `javascript:` scheme
5. Auth token storage — verify not in `localStorage`/`sessionStorage`
6. CSRF — `credentials: 'include'` paired with CSRF tokens
7. Style/event handler injection — `:style`/`:onclick` with user input
8. Deployment — no `vite preview` or dev server in production
9. SSR — state serialization XSS, template boundaries
