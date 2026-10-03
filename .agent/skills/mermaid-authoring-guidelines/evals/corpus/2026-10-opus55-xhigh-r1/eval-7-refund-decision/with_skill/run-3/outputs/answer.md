**Figure 6.1.** Refund decision: the checks of R6.1, R6.2 and R6.3 in the order they run, and the three results they lead to.

```mermaid
%%{init: {"layout": "dagre", "look": "classic", "flowchart": {"nodeSpacing": 45, "rankSpacing": 55, "wrappingWidth": 400}}}%%
flowchart TB
  accTitle: Refund decision
  accDescr: The checks of R6.1, R6.2 and R6.3 in the order they run, and the three results they lead to.
  CUST(["Customer"])
  DEF{"Reported as defective?"}
  AGE{"Over 30 days after delivery?"}
  DIG{"Downloaded digital good?"}
  AMT{"Refund of $50 or less?"}
  AGENT("Support agent decides<br/><small>approval above $500 needs a team lead</small>")
  APP("Approved automatically")
  DEC("Declined")
  CUST -->|"refund request"| DEF
  DEF -->|"yes · any age"| AGENT
  DEF -->|"no"| AGE
  AGE -->|"no"| DIG
  AGE -->|"yes"| DEC
  DIG -->|"no"| AMT
  DIG -->|"yes"| DEC
  AMT -->|"no · above $50"| AGENT
  AMT -->|"yes"| APP
  class CUST ext
  class DEF,AGE,DIG,AMT,AGENT,APP,DEC wf
  classDef ext fill:#FFFFFF,stroke:#607D8B,color:#263238,stroke-dasharray:4 3
  classDef wf fill:#E8F0FB,stroke:#2E5A8A,color:#0F2A47
```

Legend:
- diamond = a check, run top to bottom: R6.1 as two checks, then R6.2, then R6.3
- rounded box = a result of the checks; dashed stadium = the customer
- arrow label = the answer that leads to the next box
- not drawn: the payout of R6.6 and the limits of §6.2