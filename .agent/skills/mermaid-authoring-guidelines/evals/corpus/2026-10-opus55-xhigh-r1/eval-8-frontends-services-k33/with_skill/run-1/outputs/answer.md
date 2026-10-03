**Figure 2.4.** Front-end calls: each front-end calls each of the three domain services.

```mermaid
%%{init: {"layout": "dagre", "look": "classic", "flowchart": {"nodeSpacing": 45, "rankSpacing": 55, "wrappingWidth": 400}}}%%
flowchart TB
  accTitle: Front-end calls
  accDescr: Each of the three front-ends calls one node that stands for the three domain services.
  WEB("Web shop<br/><small>storefront · server-rendered pages</small>")
  BFF("Mobile BFF<br/><small>backend of the iOS and Android apps</small>")
  PAPI("Partner API<br/><small>public REST · marketplace partners</small>")
  DOM("Domain services<br/><small>Catalog · Pricing · Stock</small>")
  WEB --> DOM
  BFF --> DOM
  PAPI --> DOM
  class WEB,BFF,PAPI,DOM wf
  classDef wf fill:#E8F0FB,stroke:#2E5A8A,color:#0F2A47
```

Legend:
- rounded box in the top row = a front-end. The box below stands for Catalog service, Pricing service and Stock service, drawn as one node.
- arrow = the front-end calls each of the three services directly over HTTP/JSON. No API gateway sits between them (FS-1, FS-2, decision D-7).
- not drawn: the calls from Stock service to Pricing service (FS-3), the Admin console (FS-4) and the Warehouse feed (FS-5).