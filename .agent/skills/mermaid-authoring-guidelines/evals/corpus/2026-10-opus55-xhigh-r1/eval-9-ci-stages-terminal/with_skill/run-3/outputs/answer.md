The pipeline is one chain with a single fork and join (ci/PIPELINE.md:6-20):

    push
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
      +-----------------+
      |                 |
      v                 v
    link check        accessibility check
      |                 |
      +--------+--------+
               |
               v
         deploy preview
               |
               v
            publish <-- maintainer approval (MR comment)

An arrow means "starts only after the stage above has passed" (PL-1). Where two arrows join, both stages must pass first.

- Link check and accessibility check both wait for build site and run in parallel (PL-2). Deploy preview waits for both of them.
- Publish also needs a maintainer approval, recorded as a comment in the merge request. Until that comment exists, the run waits at publish (PL-4).
- A failed stage stops the run, and the next push starts a new run from lint (PL-3). The link check fails on its own after 20 min (PL-5).