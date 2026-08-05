# Feature flag store — read path

## 1. Scope

In scope: the read path of the flag store and its cache. Out of scope: the admin write path, which
the configuration service owns.

## 2. Requirements

| ID | Requirement | MVP? |
| :--- | :--- | :--- |
| R1 | A flag lookup resolves from the in-process cache when the entry is under 30 seconds old | Y |
| R2 | A cache miss reads the store and populates the entry | Y |
| R3 | A store timeout resolves the flag to its declared default | Y |

### 2.1 Detail

**R1.** The cache holds one entry per flag key with its fetch timestamp.

**Why.** The store serves 40,000 lookups per second at peak, against a quota of 5,000.

**R2.** A miss issues one store read per key, and concurrent misses for one key share it.

**Why.** An unshared miss produced 300 identical reads during the 2026-04-11 restart.

**R3.** A read exceeding 50 milliseconds resolves to the default declared in the flag definition.

**Why.** The call site has no path for an absent value.

## 3. Failure modes

| Condition | Outcome | Detected by |
| :--- | :--- | :--- |
| The store is unreachable | every flag resolves to its default | T4 |
| A flag has no declared default | the definition is rejected at load | T5 |

## 4. Test obligations

- T1 — two lookups 10 seconds apart → one store read; fails when the timestamp is not stored.
- T2 — 50 concurrent misses on one key → one store read.
- T3 — a store delay of 80 milliseconds → the default is returned.
