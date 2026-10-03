## 3. Pipeline

Harbor Docs builds its documentation site from the main repository. Every push to a merge request
starts a run of the pipeline. The table lists the stages in the order they run.

| Stage | Waits for | Does |
| :--- | :--- | :--- |
| lint | the push | checks Markdown style and front matter |
| unit tests | lint | tests the plugins of the site generator |
| build site | unit tests | turns the Markdown pages into static HTML |
| link check | build site | follows every link in the built HTML |
| accessibility check | build site | checks contrast, heading order and alt text |
| deploy preview | link check, accessibility check | uploads the built site to a preview address |
| publish | deploy preview | copies the previewed site to the public host |

- **PL-1.** A stage starts only after every stage it waits for has passed.
- **PL-2.** The link check and the accessibility check run in parallel.
- **PL-3.** A failed stage stops the run. The next push starts a new run from lint.
- **PL-4.** Publish also needs a maintainer approval, recorded as a comment in the merge request.
  Until the approval is recorded, the run waits at publish.

### 3.1 Limits

- **PL-5.** The link check stops after 20 min and fails.
- **PL-6.** Preview sites are deleted 7 days after the merge request closes.
