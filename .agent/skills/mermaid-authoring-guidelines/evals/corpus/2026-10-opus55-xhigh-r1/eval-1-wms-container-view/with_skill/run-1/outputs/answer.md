**Figure 3.1.** Larkspur WMS containers: who calls whom, which service owns which database, and the replication of the Inventory DB.

```mermaid
%%{init: {"layout": "dagre", "look": "classic", "flowchart": {"nodeSpacing": 45, "rankSpacing": 55, "wrappingWidth": 400}}}%%
flowchart TB
  accTitle: Larkspur WMS containers
  accDescr: Who calls whom, which service owns which database, and the replication of the Inventory DB.
  CLI(["Client apps<br/><small>Handheld app · Supervisor console</small>"])
  GW["API gateway<br/><small>Kong</small>"]
  PICK("Picking service<br/><small>Java</small>")
  SLOT("Slotting service<br/><small>Python · no database of its own</small>")
  INV("Inventory service<br/><small>Java</small>")
  PICKDB[("Picking DB<br/><small>MariaDB</small>")]
  LBL("Label printer bridge<br/><small>Go</small>")
  BUS["Event bus<br/><small>RabbitMQ</small>"]
  INVDB[("Inventory DB<br/><small>MariaDB</small>")]
  REP[("Reporting replica<br/><small>MariaDB · read-only</small>")]
  CLI -->|"tasks · scans · reports"| GW
  GW -->|"pick tasks"| PICK
  GW -->|"stock queries"| INV
  PICK -->|"owns"| PICKDB
  PICK -->|"print label"| LBL
  PICK -->|"publish pick.completed"| BUS
  PICK -->|"reserve stock"| INV
  SLOT -->|"store slot assignments"| INV
  SLOT -->|"consume stock.changed"| BUS
  INV -->|"consume · publish"| BUS
  INV -->|"owns"| INVDB
  INVDB -->|"streams"| REP
  class CLI ext
  class PICK,INV,LBL wf
  class SLOT wfNew
  class GW,BUS svc
  class PICKDB,INVDB,REP db
  classDef ext fill:#FFFFFF,stroke:#607D8B,color:#263238,stroke-dasharray:4 3
  classDef wf fill:#E8F0FB,stroke:#2E5A8A,color:#0F2A47
  classDef wfNew fill:#FFF4E0,stroke:#B36B00,color:#4A2C00,stroke-width:2px
  classDef db fill:#F3EEF9,stroke:#5E35B1,color:#2A1653
  classDef svc fill:#F5F5F5,stroke:#546E7A,color:#1F2A30
```

Legend:
- dashed stadium = the two client apps
- rounded box = a service the Larkspur team writes; orange with a thick border = added by this task
- rectangle = an off-the-shelf product; cylinder = a database
- arrow = a call, from caller to callee; an arrow labelled `owns` points from a service to its database; `streams` = the replication stream
- client calls use HTTPS, calls to the Event bus use AMQP, and every other call uses gRPC
- not drawn: the zones, which the table above gives