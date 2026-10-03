**Figure 5.1.** Sales data flow: how sales data moves from the three sources through the stages of §5.1 to the consumers of §5.2.

```mermaid
%%{init: {"layout": "dagre", "look": "classic", "flowchart": {"nodeSpacing": 45, "rankSpacing": 55, "wrappingWidth": 400}}}%%
flowchart TB
  accTitle: Sales data flow
  accDescr: How sales data moves from the three sources through the pipeline stages to the consumers.
  SRC(["Sales sources<br/><small>POS feeds · Web orders · Loyalty CSV</small>"])
  RAW[("Raw zone<br/><small>bucket</small>")]
  NORM("Normalizer<br/><small>hourly</small>")
  STG[("Staging tables")]
  DEDUP("Deduplicator<br/><small>hourly · after Normalizer</small>")
  CLEAN[("Clean sales")]
  LOAD("Warehouse loader<br/><small>nightly</small>")
  WH[("Sales warehouse")]
  FIN(["Finance dashboards"])
  FC(["Demand forecast job<br/><small>weekly</small>"])
  PLAN["Planning system<br/><small>external supply system</small>"]
  DQ(["Data quality monitor"])
  SRC ==>|"files"| RAW
  RAW ==> NORM
  NORM ==> STG
  STG ==> DEDUP
  DEDUP ==> CLEAN
  CLEAN ==> LOAD
  LOAD ==> WH
  WH --> FIN
  WH --> FC
  FC -->|"forecasts"| PLAN
  WH --> DQ
  STG --> DQ
  class SRC,FIN,FC,DQ ext
  class NORM,DEDUP,LOAD wf
  class RAW,STG,CLEAN,WH db
  class PLAN svc
  classDef ext fill:#FFFFFF,stroke:#607D8B,color:#263238,stroke-dasharray:4 3
  classDef wf fill:#E8F0FB,stroke:#2E5A8A,color:#0F2A47
  classDef db fill:#F3EEF9,stroke:#5E35B1,color:#2A1653
  classDef svc fill:#F5F5F5,stroke:#546E7A,color:#1F2A30
```

Legend:
- every arrow points the way the data moves; thick arrow = the main path of a sales record, from its source to the Sales warehouse; thin arrow = data a consumer reads or writes
- dashed stadium = the three sources, drawn as one node, and the consumers of §5.2
- rounded box = pipeline stage, with when it runs; cylinder = data store; rectangle = external system
- not drawn: the alert of the Data quality monitor to `#sales-data-oncall`