The stages form a single chain with one fork and one join. After build site, the link check and the accessibility check run in parallel. Deploy preview waits for both of them.

   push to a merge request
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
    +---------+---------+
    |                   |
    v                   v
link check     accessibility check
    |                   |
    +---------+---------+
              |
              v
       deploy preview
              |
              v
           publish  <--  maintainer approval
                         (comment in the MR)

An arrow means "waits for". A stage starts only after every stage with an arrow into it has passed (PL-1).

Rules that apply to this chain:
- The link check and the accessibility check run in parallel (PL-2).
- Any failed stage stops the run. The next push starts a new run from lint (PL-3).
- Publish also needs a maintainer approval, recorded as a comment in the merge request. Until that comment exists, the run waits at publish (PL-4).
- The link check stops and fails after 20 min (PL-5). Under PL-3, that stops the run.

Source: ci/PIPELINE.md:6-24