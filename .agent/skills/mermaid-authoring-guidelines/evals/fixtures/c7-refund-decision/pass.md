**Figure 1.** Refund decision — how R6.1 to R6.6 approve or decline a refund request.

```mermaid
%%{init: {"layout": "dagre", "look": "classic", "flowchart": {"nodeSpacing": 45, "rankSpacing": 55, "wrappingWidth": 400}, "themeCSS": "foreignObject { overflow: visible; }"}}%%
flowchart TB
    accTitle: Refund decision
    accDescr: How R6.1 to R6.6 approve or decline a refund request.
    R61{"R6.1<br/>defect reported? over 30 days?"}
    R62{"R6.2<br/>digital good, downloaded?"}
    R63{"R6.3<br/>$50 or less?"}
    AG{"Support agent approves?<br/>R6.4"}
    TL{"Team lead approves?<br/>R6.5"}
    APP("Approved<br/>R6.6 · to the original payment method")
    DEC("Declined")
    %% edge order chosen for the layout
    R63 -->|"no"| AG
    TL -->|"yes"| APP
    R61 -->|"no defect, over 30 days"| DEC
    R61 -->|"no defect, up to 30 days"| R62
    R62 -->|"no"| R63
    AG -->|"no"| DEC
    R61 -->|"defect reported"| AG
    R62 -->|"yes"| DEC
    AG -->|"yes, up to $500"| APP
    R63 -->|"yes"| APP
    AG -->|"yes, above $500"| TL
    TL -->|"no"| DEC
    class R61,R62,R63,AG,TL,APP,DEC wf
    classDef wf fill:#E8F0FB,stroke:#2E5A8A,color:#0F2A47
```

- Diamond: a check, top to bottom in the order R6.1, R6.2, R6.3; the last two are decisions of a person.
- Rounded box: an outcome.
- Arrow label: the answer that leads to the next box.
