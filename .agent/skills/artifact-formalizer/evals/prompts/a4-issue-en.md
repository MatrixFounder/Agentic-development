Write a defect record in Markdown — the document a maintainer files so that someone else can
reproduce and fix the problem.

**Subject.** A nightly reporting job runs on a cron schedule expressed in local time. On the night a
daylight-saving transition moves the clock backwards, the job fires twice, and the second run
duplicates every row it had already written. The duplicate rows have distinct primary keys, so no
constraint catches them. The problem was noticed a week later, from a support ticket about a
doubled invoice total.

Include what a reader needs: the symptom, the reproduction, the impact, the severity, the suspected
cause, and what remains unknown.

Output the document as Markdown and nothing else. Do not add a preamble, a summary, or a closing
remark.
