Harbor Docs pipeline: the stages and the order they wait for each other (ci/PIPELINE.md:6-14).

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
      +-----------+-----------+
      |                       |
      v                       v
 link check          accessibility check
      |                       |
      +-----------+-----------+
                  |
                  v
            deploy preview
                  |
                  v
               publish  <--  maintainer approval
                             (comment in the merge request)

How to read it: an arrow leads to a stage that starts after the stage above it has passed. The figure does not show the failure path.

- A stage starts only after every stage it waits for has passed (PL-1). Deploy preview needs both the link check and the accessibility check to pass.
- The link check and the accessibility check run in parallel after build site (PL-2).
- A failed stage stops the run. The next push starts a new run from lint (PL-3).
- Publish also needs a maintainer approval, recorded as a comment in the merge request. Until then, the run waits at publish (PL-4).
- The link check fails if it runs longer than 20 min (PL-5).