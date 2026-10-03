**Figure 5.1.** Sales data flow: how a sales record moves from the sources to the Sales warehouse, and what the consumers read.

```mermaid
%%{init: {"layout": "dagre", "look": "classic", "flowchart": {"nodeSpacing": 45, "rankSpacing": 55, "wrappingWidth": 400}}}%%
flowchart TB
  accTitle: Sales data flow
  accDescr: How a sales record moves from the sources to the Sales warehouse, and what the consumers read.
  SRC(["Sales sources<br/><small>POS feeds · Web orders · Loyalty CSV</small>"])
  RAW[("Raw zone")]
  NORM("Normalizer<br/><small>hourly</small>")
  STG[("Staging tables")]
  DEDUP("Deduplicator<br/><small>hourly · after Normalizer</small>")
  CLEAN[("Clean sales")]
  LOAD("Warehouse loader<br/><small>nightly</small>")
  WH[("Sales warehouse")]
  FIN(["Finance dashboards"])
  FC(["Demand forecast job<br/><small>weekly</small>"])
  PLAN["Planning system<br/><small>external supply system</small>"]
  DQ(["Data quality monitor<br/><small>alerts #35;sales-data-oncall</small>"])
  SRC ==>|"sales files"| RAW
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
- every arrow points the way the data moves
- thick arrow = the main path of a sales record; thin arrow = other data
- dashed stadium = the sources at the top, or a consumer below the warehouse
- rounded box = pipeline stage, with when it runs
- cylinder = bucket or table; rectangle = external system
- Sales sources stands for the three sources of the table above; each drops its own files into Raw zone