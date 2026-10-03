Each push to a merge request starts a new run. The stages form one chain that splits in two after the build and joins again before deploy:

  push
   |
  lint
   |
  unit tests
   |
  build site
   |
   +----------------+
   |                |
  link check    accessibility check     (run in parallel)
   |                |
   +----------------+
   |
  deploy preview    (needs both checks to pass)
   |
  publish           (also needs a maintainer approval comment on the MR)

How the connections behave:

- A stage starts only when every stage it waits for has passed (PL-1). Deploy preview therefore waits for both the link check and the accessibility check.
- The link check and the accessibility check both start as soon as build site passes, and they run at the same time (PL-2).
- If any stage fails, the run stops there. Nothing resumes. The next push starts a fresh run from lint (PL-3).
- After deploy preview passes, the run waits at publish until a maintainer records approval as a comment in the merge request (PL-4).

Limits to keep in mind:

- The link check fails if it runs longer than 20 minutes (PL-5). That stops the run, so deploy preview and publish never start.
- Preview sites are deleted 7 days after the merge request closes (PL-6).