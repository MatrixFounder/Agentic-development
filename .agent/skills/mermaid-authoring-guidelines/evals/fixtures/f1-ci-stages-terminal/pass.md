Figure 1. Pipeline stages in run order; the two checks run in parallel.

```text figure
lint -> unit tests -> build site -+-> link check ----------+-> deploy preview -> publish
                                  |                        |
                                  +-> accessibility check -+
```

Publish also waits until a maintainer approval is recorded in the merge request.
