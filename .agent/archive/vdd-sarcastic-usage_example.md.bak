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

| # | Issue | Sarcastic Verdict |
| :--- | :--- | :--- |
| 1 | **No TTL / eviction** | Congrats, you've built a memory leak that *also* serves stale data. Best of both worlds! |
| 2 | **No thread safety** | I'm sure two threads writing to a bare `dict` simultaneously will work out *great*. |
| 3 | **No error handling on `fetch_from_api`** | When the API is down, your cache will helpfully store... an exception traceback. |
| 4 | **No max size** | Eventually this dict will consume all available RAM, but hey, RAM is cheap, right? |
| 5 | **Hardcoded global state** | Testing this will be a joy. "Why does test #7 fail only when run after test #3?" — Future You |

### Exit Signal Check
**Status**: NOT Zero-Slop. All 5 issues are real and grounded in the code. The Roast continues.
