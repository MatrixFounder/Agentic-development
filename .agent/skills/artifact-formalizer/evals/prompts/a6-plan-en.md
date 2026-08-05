Write a development plan in Markdown — the document that turns an approved specification into
ordered, checkable steps.

**Subject.** A single build produces one deployable artifact containing both the web front end and
the batch workers. A change to either one forces a full redeploy of both, and the workers cannot be
scaled independently. The team is splitting the build into two artifacts that share one library.
The shared library must be extracted before either artifact can be built from it.

Include the ordering rule, the steps grouped into stages, the verification after each stage, and
how to revert if a stage fails.

Output the document as Markdown and nothing else. Do not add a preamble, a summary, or a closing
remark.
