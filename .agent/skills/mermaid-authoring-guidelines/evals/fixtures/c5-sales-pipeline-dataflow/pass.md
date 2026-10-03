**Figure 1.** Sales data flow — how sales records move from the three sources to the dashboards, the forecast and the quality monitor.

```mermaid
%%{init: {"layout": "dagre", "look": "classic", "flowchart": {"nodeSpacing": 45, "rankSpacing": 55, "wrappingWidth": 400}}}%%
flowchart TB
    accTitle: Sales data flow
    accDescr: How sales records move from the three sources to the dashboards, the forecast and the quality monitor.
    SRC(["Sources<br/><small>12 POS feeds · Web orders · Loyalty CSV</small>"])
    RAW[("Raw zone")]
    NORM("Normalizer<br/><small>hourly</small>")
    STG[("Staging tables")]
    DEDUP("Deduplicator<br/><small>hourly</small>")
    CLEAN[("Clean sales")]
    LOAD("Warehouse loader<br/><small>nightly</small>")
    WH[("Sales warehouse")]
    DASH(["Finance dashboards"])
    FC("Demand forecast job<br/><small>weekly</small>")
    PLAN["Planning system"]
    DQ("Data quality monitor")
    SRC ==> RAW
    RAW ==> NORM
    NORM ==> STG
    STG ==> DEDUP
    DEDUP ==> CLEAN
    CLEAN ==> LOAD
    LOAD ==> WH
    WH --> DASH
    WH --> FC
    FC -->|"forecasts"| PLAN
    STG --> DQ
    WH --> DQ
    class SRC,DASH ext
    class NORM,DEDUP,LOAD,FC,DQ wf
    class RAW,STG,CLEAN,WH db
    class PLAN svc
    classDef ext fill:#FFFFFF,stroke:#607D8B,color:#263238,stroke-dasharray:4 3
    classDef wf fill:#E8F0FB,stroke:#2E5A8A,color:#0F2A47
    classDef db fill:#F3EEF9,stroke:#5E35B1,color:#2A1653
    classDef svc fill:#F5F5F5,stroke:#546E7A,color:#1F2A30
```

- Thick arrow: the path of a sales record from its source into the warehouse.
- Thin arrow: other data that moves, the way it moves.
- Dashed stadium: a source or a reader outside the pipeline.
- Rounded box: a job of the pipeline.
- Cylinder: a store of sales records.
- Rectangle: an external system.
- Not drawn: the alert of the monitor to `#sales-data-oncall`.
