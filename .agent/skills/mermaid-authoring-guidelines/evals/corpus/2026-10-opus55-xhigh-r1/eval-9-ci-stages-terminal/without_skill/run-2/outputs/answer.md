The stages form a single chain that splits into two parallel checks after the build and joins again before deploy:

  push
   -> lint
   -> unit tests
   -> build site
       -> link check            \  run in parallel,
       -> accessibility check   /  both must pass
   -> deploy preview
   -> publish  (also needs a maintainer approval comment in the MR)

How a run moves through it:

1. Every push to a merge request starts a new run at lint. Lint, unit tests and build site run one after another. Each stage starts only when the stage before it has passed (PL-1).

2. When build site passes, link check and accessibility check start at the same time (PL-2).

3. Deploy preview starts only after both checks have passed. If either check fails, no preview is deployed.

4. Publish needs two things: deploy preview has passed, and a maintainer has approved in a comment on the merge request. Until that comment exists, the run waits at publish (PL-4).

5. If any stage fails, the run stops. A failed run is not resumed. The next push starts a new run from lint (PL-3).

Things to watch:

- If link check runs longer than 20 min, it fails (PL-5). That stops the run before deploy preview and publish.
- Preview sites are deleted 7 days after the merge request closes (PL-6).