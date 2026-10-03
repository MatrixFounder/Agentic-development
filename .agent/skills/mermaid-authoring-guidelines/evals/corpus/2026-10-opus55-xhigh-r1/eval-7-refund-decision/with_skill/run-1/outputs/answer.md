**Figure 6a.** Refund checks: the checks R6.1, R6.2 and R6.3 in the order they run, and where each answer leads.

```mermaid
%%{init: {"layout": "dagre", "look": "classic", "flowchart": {"nodeSpacing": 45, "rankSpacing": 55, "wrappingWidth": 400}}}%%
flowchart TB
  accTitle: Refund checks
  accDescr: The checks R6.1, R6.2 and R6.3 in the order they run, and where each answer leads.
  CUST(["Customer<br/><small>asks in the support portal</small>"])
  DEF{"Reported as defective?"}
  AGE{"Over 30 days after delivery?"}
  DLG{"Downloaded digital good?"}
  AMT{"Refund of $50 or less?"}
  DECL("Declined")
  APPR("Approved<br/><small>refund to original payment method</small>")
  AGENT("Support agent<br/><small>decides as in Figure 6b</small>")
  CUST -->|"refund request"| DEF
  DEF -->|"no"| AGE
  AGE -->|"yes"| DECL
  AGE -->|"no"| DLG
  DLG -->|"yes"| DECL
  DLG -->|"no"| AMT
  AMT -->|"yes"| APPR
  AMT -->|"no"| AGENT
  DEF -->|"yes"| AGENT
  class CUST ext
  class DEF,AGE,DLG,AMT,DECL,APPR,AGENT wf
  classDef ext fill:#FFFFFF,stroke:#607D8B,color:#263238,stroke-dasharray:4 3
  classDef wf fill:#E8F0FB,stroke:#2E5A8A,color:#0F2A47
```

Legend:
- dashed stadium = the customer who asks for the refund
- diamond = a check, top to bottom in the order they run: the first two are R6.1, then R6.2, then R6.3
- rounded box = an outcome; arrow label = the answer that leads to the next box
- not drawn: the record of each decision in the history of the request, and the limits of §6.2

**Figure 6b.** Review by people: a request that goes to a support agent, the agent's decision, and the team lead's decision above $500 (R6.4, R6.5, R6.6).

```mermaid
%%{init: {"layout": "dagre", "look": "classic", "flowchart": {"nodeSpacing": 45, "rankSpacing": 55, "wrappingWidth": 400}}}%%
flowchart TB
  accTitle: Review by people
  accDescr: A request that goes to a support agent, the agent's decision, and the team lead's decision above 500 dollars.
  AGENT("Support agent<br/><small>defective item · refund above $50</small>")
  AGOK{"Agent approves?"}
  HIGH{"Refund above $500?"}
  LEAD{"Team lead approves?"}
  DECL("Declined")
  APPR("Approved<br/><small>refund to original payment method</small>")
  AGENT --> AGOK
  AGOK -->|"no"| DECL
  AGOK -->|"yes"| HIGH
  HIGH -->|"yes"| LEAD
  HIGH -->|"no"| APPR
  LEAD -->|"no"| DECL
  LEAD -->|"yes"| APPR
  class AGENT,AGOK,HIGH,LEAD,DECL,APPR wf
  classDef wf fill:#E8F0FB,stroke:#2E5A8A,color:#0F2A47
```

Legend:
- rounded box at the top = the request at a support agent, from Figure 6a; rounded boxes below = outcomes
- diamond = a decision, top to bottom in the order it happens; arrow label = the answer that leads to the next box