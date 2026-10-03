The pipeline is mostly a straight chain, with one point where it splits into two parallel checks and then joins again:

    push to merge request
      |
      v
    lint
      |
      v
    unit tests
      |
      v
    build site
      |
      +------------------+
      |                  |
      v                  v
    link check     accessibility check     (run in parallel)
      |                  |
      +------------------+
      |
      v
    deploy preview                         (needs BOTH checks passed)
      |
      v
    publish  <-- also needs a maintainer approval comment in the MR

How the hand-offs work:

- Every push to a merge request starts a new run at lint.
- A stage starts only after every stage it waits for has passed (PL-1).
- After build site, the link check and the accessibility check start at the same time and run side by side (PL-2).
- Deploy preview is the join point. It waits until both checks have passed. One passing is not enough.
- Publish needs two things: deploy preview has passed, and a maintainer has recorded approval as a comment in the merge request. Until that comment exists, the run sits waiting at publish (PL-4). It does not fail.
- Any failed stage stops the whole run. There is no resume or retry from the failed stage. The next push starts over from lint (PL-3).
- The link check is capped at 20 minutes. If it runs longer, it fails, and that stops the run like any other failure (PL-5).

Source: ci/PIPELINE.md, section 3.