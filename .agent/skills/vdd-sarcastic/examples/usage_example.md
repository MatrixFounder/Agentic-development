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

| # | Issue | Severity | Confidence | Sarcastic Verdict |
| :--- | :--- | :--- | :--- | :--- |
| 1 | **No TTL / eviction** | HIGH | High | Congrats, you've built a memory leak that *also* serves stale data. Best of both worlds! |
| 2 | **No thread safety** | HIGH | Medium | I'm sure two threads writing to a bare `dict` simultaneously will work out *great*. |
| 3 | **No error handling on `fetch_from_api`** | MED | High | When the API is down, your cache will helpfully store... an exception traceback. |
| 4 | **No max size** | HIGH | High | Eventually this dict will consume all available RAM, but hey, RAM is cheap, right? |
| 5 | **Hardcoded global state** | MED | High | Testing this will be a joy. "Why does test #7 fail only when run after test #3?" — Future You |
| 6 | **Falsy values never re-fetched?** | LOW | Low | If `fetch_from_api` can return `None`, you've cached "nothing" forever. Probably. Reported anyway — low-confidence findings get reported, not swallowed. |

### Exit Signal Check
**Status**: NOT Zero-Slop. All 6 findings reported per the exhaustive-reporting rule — including the low-confidence #6 — each with confidence + severity attached; filtering happens downstream. The Roast continues.
