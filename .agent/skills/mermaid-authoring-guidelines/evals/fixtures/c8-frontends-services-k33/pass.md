**Figure 1.** Front-ends and domain services — who calls which domain service.

```mermaid
%%{init: {"layout": "dagre", "look": "classic", "flowchart": {"nodeSpacing": 45, "rankSpacing": 55, "wrappingWidth": 400}}}%%
flowchart TB
  accTitle: Front-ends and domain services
  accDescr: Each front-end calls each domain service. Stock service calls Pricing service and imports the Warehouse feed. The Admin console writes to Catalog service and Pricing service.
  FE("Front-ends<br/><small>Web shop · Mobile BFF · Partner API</small>")
  CAT("Catalog service")
  PRI("Pricing service")
  STK("Stock service")
  ADM(["Admin console"])
  WF(["Warehouse feed"])
  FE --> CAT
  FE --> PRI
  FE --> STK
  STK -->|"prices reserved items"| PRI
  STK -->|"imports nightly"| WF
  ADM -->|writes| CAT
  ADM -->|writes| PRI
  classDef wf fill:#E8F0FB,stroke:#2E5A8A,color:#0F2A47
  classDef ext fill:#FFFFFF,stroke:#607D8B,color:#263238,stroke-dasharray:4 3
  class FE,CAT,PRI,STK wf
  class ADM,WF ext
```

- Blue rounded box: a front-end or a domain service. The Front-ends box stands for Web shop,
  Mobile BFF and Partner API.
- White stadium with a dashed outline: Admin console and Warehouse feed, which are neither
  front-ends nor domain services.
- Arrow: from caller to callee. An unlabelled arrow is a call over HTTP/JSON; an arrow from
  Front-ends is that call from each of the three front-ends.
