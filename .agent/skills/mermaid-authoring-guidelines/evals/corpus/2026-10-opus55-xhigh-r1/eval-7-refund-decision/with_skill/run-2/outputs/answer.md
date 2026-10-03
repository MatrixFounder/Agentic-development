**Figure 6.1.** Refund checks: R6.1, R6.2 and R6.3 in the order they run, and the three outcomes they lead to.

```mermaid
%%{init: {"layout": "dagre", "look": "classic", "flowchart": {"nodeSpacing": 45, "rankSpacing": 55, "wrappingWidth": 400}}}%%
flowchart TB
  accTitle: Refund checks
  accDescr: R6.1, R6.2 and R6.3 in the order they run, and the three outcomes they lead to.
  CUST(["Customer<br/><small>asks in the support portal</small>"])
  DEF{"Reported as defective?<br/><small>R6.1 · any age</small>"}
  AGE{"Within 30 days of delivery?<br/><small>R6.1</small>"}
  DIG{"Digital good?<br/><small>R6.2</small>"}
  DL{"Downloaded?<br/><small>R6.2</small>"}
  AMT{"Refund of $50 or less?<br/><small>R6.3</small>"}
  AGENT("Goes to a support agent")
  APPR("Approved automatically<br/><small>back to the original payment method</small>")
  DECL("Declined")
  CUST -->|"refund request"| DEF
  DEF -->|"yes"| AGENT
  DEF -->|"no"| AGE
  AGE -->|"yes"| DIG
  AGE -->|"no"| DECL
  DIG -->|"no"| AMT
  DIG -->|"yes"| DL
  DL -->|"no"| AMT
  DL -->|"yes"| DECL
  AMT -->|"no · above $50"| AGENT
  AMT -->|"yes"| APPR
  class CUST ext
  class DEF,AGE,DIG,DL,AMT,AGENT,APPR,DECL wf
  classDef ext fill:#FFFFFF,stroke:#607D8B,color:#263238,stroke-dasharray:4 3
  classDef wf fill:#E8F0FB,stroke:#2E5A8A,color:#0F2A47
```

Legend:
- dashed stadium = the customer
- diamond = a check, top to bottom in the order R6.1, R6.2, R6.3; its second line names the rule
- rounded box = an outcome; "Goes to a support agent" continues in Figure 6.2
- arrow = the next step; its label = the answer that leads to it

The defect report is checked before the age because R6.1 sends a defective item to a support agent at any age. R6.2 applies to digital goods only, so any other good goes straight to R6.3.

**Figure 6.2.** Refund review: the decision of the support agent and, above $500, the decision of a team lead.

```mermaid
%%{init: {"layout": "dagre", "look": "classic", "flowchart": {"nodeSpacing": 45, "rankSpacing": 55, "wrappingWidth": 400}}}%%
flowchart TB
  accTitle: Refund review
  accDescr: The decision of the support agent and, above $500, the decision of a team lead.
  IN("Goes to a support agent<br/><small>R6.1 defective · R6.4 above $50</small>")
  AG{"Support agent approves?<br/><small>R6.4</small>"}
  BIG{"Refund above $500?<br/><small>R6.5</small>"}
  TL{"Team lead approves?<br/><small>R6.5</small>"}
  APPR("Approved<br/><small>back to the original payment method</small>")
  DECL("Declined")
  IN --> AG
  AG -->|"yes"| BIG
  AG -->|"no"| DECL
  BIG -->|"no"| APPR
  BIG -->|"yes"| TL
  TL -->|"yes"| APPR
  TL -->|"no"| DECL
  class IN,AG,BIG,TL,APPR,DECL wf
  classDef wf fill:#E8F0FB,stroke:#2E5A8A,color:#0F2A47
```

Legend:
- rounded box at the top = the outcome of Figure 6.1 that this review starts from; other rounded boxes = outcomes
- diamond = a decision or a check, top to bottom in the order R6.4, R6.5; its second line names the rule
- arrow = the next step; its label = the answer that leads to it
- not drawn: the record of every decision in the history of the request, and the limits of §6.2, which do not change the decision