# Go (Golang) Security Quick-Reference

> Condensed from `References/security-best-practices/references/golang-general-backend-security.md`.
> Load this when generating or reviewing Go code.

## LLM Anti-Patterns (DO NOT recommend these)

- ❌ Using `http.ListenAndServe(":8080", handler)` without explicit server timeouts — zero timeouts = infinite, DoS risk.
  - ✅ Always create `&http.Server{ReadHeaderTimeout: ..., ReadTimeout: ..., WriteTimeout: ..., IdleTimeout: ..., MaxHeaderBytes: ...}`.
- ❌ Using `text/template` for HTML output — no auto-escaping, XSS.
  - ✅ Always use `html/template` for HTML.
- ❌ Using `template.HTML(userInput)` to bypass escaping — direct XSS.
  - ✅ Pass user data as data values, never as `template.HTML`/`template.JS`/`template.URL`.
- ❌ Using `exec.Command("sh", "-c", userInput)` — shell injection.
  - ✅ Use `exec.CommandContext("tool", "--flag", validatedArg)` with explicit arg list, no shell.
- ❌ Using `math/rand` for tokens/secrets — predictable output.
  - ✅ Always `crypto/rand` for security-sensitive random values.
- ❌ Setting `InsecureSkipVerify: true` in TLS config.
  - ✅ Fix certificate issues properly. Never skip verification in production.
- ❌ Recommending `cookie.Secure = true` unconditionally — breaks local HTTP dev.
  - ✅ Conditional: `Secure: os.Getenv("ENV") == "production"` or config-driven.

## Critical Grep Patterns

```
# HTTP server hardening
http.ListenAndServe(    # Must use http.Server with timeouts instead
&http.Server{           # Verify ReadHeaderTimeout, MaxHeaderBytes set

# Body / upload limits
io.ReadAll(r.Body)      # Must use http.MaxBytesReader first
json.NewDecoder(r.Body) # Verify body size limit
http.MaxBytesReader     # Should be present per-handler

# Debug endpoints
net/http/pprof          # Must not be public in production
/debug/pprof            # Must be behind auth or internal listener
http.DefaultServeMux    # May have pprof registered globally

# Templates / XSS
text/template           # Must use html/template for HTML
template.HTML(          # Typed wrapper — verify not user-controlled
template.JS(            # Same risk — typed string bypasses escaping

# File handling
http.ServeFile(         # Verify path not user-controlled
http.FileServer(        # Verify directory is constrained
filepath.Join(          # Verify no user input causes traversal

# SQL injection
fmt.Sprintf("SELECT     # String-formatted SQL — use parameterized
db.Query( / db.Exec(    # Verify using placeholders ($1 / ?)

# Command injection
exec.Command("sh"       # Shell execution — very dangerous
exec.Command("bash"     # Same — never with user input in args

# SSRF
http.Get(               # Verify URL not user-controlled
http.DefaultClient      # Has no timeout — use configured client

# Crypto
math/rand               # NEVER for security — use crypto/rand
InsecureSkipVerify      # TLS bypass — NEVER in production

# Auth
bcrypt                  # Correct for passwords
subtle.ConstantTimeCompare  # Correct for tokens/MACs

# Concurrency & Supply chain
go test -race           # Must be in CI
GOSUMDB=off             # Disables integrity checking — dangerous
govulncheck             # Should be in CI
```

## Framework-Specific Edge Cases

1. **`http.Server` zero timeouts** — Go's default is 0 = forever. A slowloris attack can exhaust all connections. Always set `ReadHeaderTimeout` at minimum.
2. **`template.HTML()`** — Marks a string as "safe HTML". If user input flows in, it's XSS. Same for `template.JS()`, `template.URL()`.
3. **`text/template` vs `html/template`** — Same API, different safety. `text/template` does NO escaping. A common LLM mistake is importing the wrong one.
4. **`http.DefaultServeMux`** — `import _ "net/http/pprof"` registers on the default mux. If you serve with `http.DefaultServeMux`, pprof is publicly accessible.
5. **`filepath.Join` is NOT path-safe** — `filepath.Join("/base", "../../../etc/passwd")` returns `/etc/passwd`. Must verify result stays under base directory.
6. **`io.ReadAll(r.Body)`** — No size limit. Attacker sends 10GB body → OOM. Always wrap with `http.MaxBytesReader` first.
7. **`GOSUMDB=off`** — Disables module integrity verification. Supply chain attacks become trivial. Only use `GONOSUMDB` for genuinely private modules.
8. **Data races** — Go's race detector only finds races in executed code paths. Must run `go test -race` in CI with good coverage.

## Recommended Audit Order

1. HTTP server timeouts and `MaxHeaderBytes` — verify explicit values
2. Body size limits — `http.MaxBytesReader` on all handlers accepting bodies
3. Template safety — `html/template` (not `text/template`), no `template.HTML()` with user data
4. SQL injection — parameterized queries, no `fmt.Sprintf` SQL
5. Command injection — no `exec.Command("sh", "-c", ...)` with user input
6. SSRF — outbound HTTP with user-controlled URLs
7. Secret management — no hardcoded secrets, no logging of credentials
8. Cookie flags — `Secure` (conditional), `HttpOnly`, `SameSite`
9. CSRF — all cookie-auth state-changing endpoints protected
10. Debug endpoints — pprof/expvar not publicly accessible
11. Crypto — `crypto/rand` for tokens, bcrypt/argon2 for passwords
12. Dependencies — `govulncheck` in CI, `go.sum` committed
