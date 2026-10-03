**Figure 5.1.** Sales data flow: the path of a sale from the sources to the Sales warehouse, and what each consumer reads and writes.

```mermaid
%%{init: {"layout": "dagre", "look": "classic", "flowchart": {"nodeSpacing": 45, "rankSpacing": 55, "wrappingWidth": 400}}}%%
flowchart TB
  accTitle: Sales data flow
  accDescr: The path of a sale from the sources to the Sales warehouse, and what each consumer reads and writes.
  SRC(["Sources<br/><small>POS feeds · Web orders · Loyalty CSV</small>"])
  RAW[("Raw zone bucket")]
  NORM("Normalizer<br/><small>hourly</small>")
  STG[("Staging tables")]
  DEDUP("Deduplicator<br/><small>hourly · after Normalizer</small>")
  CLEAN[("Clean sales")]
  LOAD("Warehouse loader<br/><small>nightly</small>")
  WH[("Sales warehouse")]
  FIN(["Finance dashboards"])
  FC("Demand forecast job<br/><small>weekly</small>")
  PLAN["Planning system<br/><small>external supply system</small>"]
  DQ("Data quality monitor")
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
  STG --> DQ
  WH --> DQ
  class SRC,FIN ext
  class NORM,DEDUP,LOAD,FC,DQ wf
  class RAW,STG,CLEAN,WH db
  class PLAN svc
  classDef ext fill:#FFFFFF,stroke:#607D8B,color:#263238,stroke-dasharray:4 3
  classDef wf fill:#E8F0FB,stroke:#2E5A8A,color:#0F2A47
  classDef db fill:#F3EEF9,stroke:#5E35B1,color:#2A1653
  classDef svc fill:#F5F5F5,stroke:#546E7A,color:#1F2A30
```

Legend:
- every arrow points the way the data moves
- thick arrow = the path of a sale to the Sales warehouse; thin arrow = a consumer's read or write
- dashed stadium = the sources and the Finance dashboards; rectangle = external system
- rounded box = a stage or a consumer job; its second line = when it runs
- cylinder = a store
- not drawn: the alert the Data quality monitor sends to `#sales-data-oncall`