# jQuery Security Quick-Reference

> Condensed from `References/security-best-practices/references/javascript-jquery-web-frontend-security.md`.
> Load this when generating or reviewing jQuery code.

## LLM Anti-Patterns (DO NOT recommend these)

- ❌ Using `.html(userInput)` — jQuery's `.html()` is equivalent to `innerHTML`, direct XSS.
  - ✅ Use `.text(userInput)` for text content. Build elements with `$("<span>").text(userInput)`.
- ❌ Using `$(userInput)` where input could be HTML — jQuery interprets HTML strings as element creation.
  - ✅ Use explicit selectors: `$("#" + $.escapeSelector(id))`, or build nodes with `$("<tag>").text(...)`.
- ❌ Using `$.parseHTML(html, context, true)` with `keepScripts=true` on untrusted HTML.
  - ✅ Always `keepScripts=false` for untrusted input.
- ❌ Using JSONP (`dataType: "jsonp"`) with untrusted endpoints — executes arbitrary JavaScript.
  - ✅ Use `dataType: "json"` with CORS. Set `jsonp: false` as defense-in-depth.
- ❌ Deep-merging untrusted objects with `$.extend(true, target, untrustedObj)` — prototype pollution.
  - ✅ Shallow merge with allowlisted keys, or filter `__proto__`/`constructor`/`prototype`.

## Critical Grep Patterns

```
# HTML injection sinks (DOM XSS)
.html(                # XSS if argument is untrusted
.append(              # XSS if argument contains HTML
.prepend(             # Same risk
.before(              # Same risk
.after(               # Same risk
.replaceWith(         # Same risk
.wrap(                # Same risk
$(                    # If argument might be HTML (not a selector)
$.parseHTML(          # Check keepScripts parameter

# Script execution
$.getScript(          # Fetches and executes JS — never with user URL
dataType: "script"    # Same as getScript
dataType: "jsonp"     # Executes response as JS — avoid
jsonp:                # Must set jsonp: false for untrusted URLs
callback=?            # JSONP trigger pattern
.load(                # Loads HTML and can execute scripts
eval(                 # Never with user input
$.globalEval          # Never with user input

# Attribute injection
.attr("href"          # URL validation needed — block javascript:
.attr("src"           # Same risk
.attr("style"         # CSS injection risk
.attr("onclick"       # Event handler injection — never from strings
.prop("href"          # Same as .attr("href")

# Prototype pollution
$.extend(true         # Deep merge — filter untrusted objects
__proto__             # Dangerous key in user objects
constructor           # Dangerous key in user objects

# Selector injection
"#" +                 # Selector construction — use $.escapeSelector()
"." +                 # Same risk
$("[data-id='" +      # Selector attribute injection

# CSRF (cookie auth only)
$.post(               # Verify CSRF token included
$.ajax({ method:      # Same — verify CSRF header
$.ajaxSetup           # Central place for CSRF headers

# jQuery version / sourcing
jquery-*.js           # Check version — must be ≥3.5.0
integrity=            # SRI — must be present for CDN scripts
```

## Framework-Specific Edge Cases

1. **`.html()` vs `.text()`** — `.html(x)` parses and inserts HTML (XSS). `.text(x)` inserts as text content (safe). Always default to `.text()`.
2. **`$(htmlString)`** — If the string starts with `<`, jQuery creates elements. Attackers can inject `<img onerror=...>`. Use `$.parseHTML` with `keepScripts=false` if parsing is needed.
3. **`.load()` script execution** — Without a selector suffix, `.load()` passes content to `.html()` before removing scripts, which means scripts CAN execute. With a selector suffix, scripts are stripped first.
4. **CVE-2020-11022/11023** — jQuery < 3.5.0 had XSS in DOM manipulation methods even with "sanitized" input. Must use ≥3.5.0.
5. **CVE-2019-11358** — jQuery < 3.4.0 had prototype pollution in `$.extend`. Must use ≥3.4.0.
6. **jQuery 4.0 Trusted Types** — jQuery 4.0+ supports `TrustedHTML` in manipulation methods. Leverage this with CSP `require-trusted-types-for`.
7. **`$.escapeSelector()`** — Available since jQuery 3.0. Must use when building selectors from user input to prevent selector injection.
8. **JSONP `jsonp: false`** — jQuery docs explicitly recommend setting this "for security reasons". Always set it when the target endpoint is not fully trusted.

## Recommended Audit Order

1. jQuery version — must be ≥3.5.0 (critical CVEs below this)
2. HTML injection sinks: `.html()`, `.append()`, `$(htmlString)` with user data
3. Script execution: `.load()`, `$.getScript()`, JSONP usage
4. `$.parseHTML()` — verify `keepScripts=false` for untrusted input
5. Prototype pollution: `$.extend(true, ...)` with untrusted objects
6. Attribute injection: `.attr("href"/src"/style"/onclick")` with user data
7. Selector injection: `$("#" + userInput)` — use `$.escapeSelector()`
8. CSRF tokens on all `$.post()`/`$.ajax()` state-changing requests
9. CDN scripts — SRI (`integrity=`) present on all external script tags
