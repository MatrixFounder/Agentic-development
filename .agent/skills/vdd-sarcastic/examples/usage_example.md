# Usage Example: Sarcastic Critique (The Roast)

## Input

The Builder submits a caching function:

```python
cache = {}

def get_data(key):
    if key in cache:
        return cache[key]
    data = fetch_from_api(key)
    cache[key] = data
    return data
```

## Sarcasmotron Output

Oh, a *global mutable dictionary* as a cache. How delightfully 2003 of you. Let me count the ways this will betray you:

### The Roast

Lines are counted in the submitted snippet (l.1 = `cache = {}`).

| # | Issue | Severity | Confidence | Check | Sarcastic Verdict |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | **No TTL / eviction**, l.7 | HIGH | High | Test: an entry older than the TTL is fetched again | Congrats, you've built a memory leak that *also* serves stale data. Best of both worlds! |
| 2 | **No thread safety**, l.4-7 | HIGH | Medium | Test: concurrent callers fetch a key once | I'm sure two threads writing to a bare `dict` simultaneously will work out *great*. |
| 3 | **No error handling on `fetch_from_api`**, l.6 | MEDIUM | High | Test: a failing fetch caches nothing | When the API is down, your cache will helpfully store... an exception traceback. |
| 4 | **No max size**, l.7 | HIGH | High | Test: the cache never holds more than N entries | Eventually this dict will consume all available RAM, but hey, RAM is cheap, right? |
| 5 | **Hardcoded global state**, l.1 | MEDIUM | High | Test: two tests in either order see an empty cache | Testing this will be a joy. "Why does test #7 fail only when run after test #3?" — Future You |
| 6 | **Falsy values never re-fetched?**, l.4 | LOW | Low | Test: a `None` result is fetched again | If `fetch_from_api` can return `None`, you've cached "nothing" forever. Probably. Reported anyway — low-confidence findings get reported, not swallowed. |
| 7 | **exit-bar condition unverifiable — test run NOT RUN (snippet submitted without tests)** | HIGH | High | The test run's output comes with the next review | Shipping without a single test is bold; I'll assume it works, just like you did. |

### Exit Signal Check
**Status**: NOT Zero-Slop. All 7 findings reported per the exhaustive-reporting rule — including the low-confidence #6 and the unverifiable test run #7 — each with confidence + severity attached; filtering happens downstream. The Roast continues.
