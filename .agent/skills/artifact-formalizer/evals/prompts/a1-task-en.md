Write a technical specification (a TASK document) in Markdown for the work described below.

**Subject.** A public HTTP API currently has no rate limiting. Clients authenticate with an API key.
Traffic is bursty: a small number of keys produce most of the load, and one misbehaving client has
twice exhausted the database connection pool. The team wants per-key quotas, a shared burst
allowance, and a documented retry contract for clients that are throttled.

Include the sections a specification of this kind needs: the problem, the requirements with
identifiers, the use cases, the acceptance criteria, the open questions, the decisions taken, and
what is out of scope.

Output the document as Markdown and nothing else. Do not add a preamble, a summary, or a closing
remark.
