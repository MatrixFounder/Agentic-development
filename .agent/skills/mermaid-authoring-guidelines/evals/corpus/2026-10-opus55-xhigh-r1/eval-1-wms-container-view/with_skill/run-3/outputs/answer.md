**Figure 3.1.** Larkspur WMS containers: who calls whom, which service owns which database, and the stream to the Reporting replica.

```mermaid
%%{init: {"layout": "dagre", "look": "classic", "flowchart": {"nodeSpacing": 45, "rankSpacing": 55, "wrappingWidth": 400}}}%%
flowchart TB
  accTitle: Larkspur WMS containers
  accDescr: Who calls whom, which service owns which database, and the stream to the Reporting replica.
  CLI(["Client apps<br/><small>Handheld app · Supervisor console</small>"])
  GW["API gateway<br/><small>Kong</small>"]
  PICK("Picking service<br/><small>Java</small>")
  PDB[("Picking DB<br/><small>MariaDB</small>")]
  LPB("Label printer bridge<br/><small>Go</small>")
  INV("Inventory service<br/><small>Java</small>")
  BUS["Event bus<br/><small>RabbitMQ</small>"]
  IDB[("Inventory DB<br/><small>MariaDB</small>")]
  REP[("Reporting replica<br/><small>MariaDB · read-only</small>")]
  SLOT("Slotting service<br/><small>Python · added by this task</small>")
  CLI -->|"tasks · scans · reports"| GW
  GW -->|"pick tasks"| PICK
  PICK -->|"owns"| PDB
  PICK -->|"print label"| LPB
  PICK -->|"reserve stock"| INV
  PICK -->|"publishes pick.completed"| BUS
  GW -->|"stock queries"| INV
  INV -->|"consumes · publishes"| BUS
  INV -->|"owns"| IDB
  IDB -->|"streams"| REP
  SLOT -->|"stores slot assignments"| INV
  SLOT -->|"consumes stock.changed"| BUS
  class CLI ext
  class PICK,LPB,INV wf
  class SLOT wfNew
  class GW,BUS svc
  class PDB,IDB,REP db
  classDef ext fill:#FFFFFF,stroke:#607D8B,color:#263238,stroke-dasharray:4 3
  classDef wf fill:#E8F0FB,stroke:#2E5A8A,color:#0F2A47
  classDef wfNew fill:#FFF4E0,stroke:#B36B00,color:#4A2C00,stroke-width:2px
  classDef svc fill:#F5F5F5,stroke:#546E7A,color:#1F2A30
  classDef db fill:#F3EEF9,stroke:#5E35B1,color:#2A1653
```

Legend:
- dashed stadium = client apps; rounded box = service the Larkspur team writes; orange with a thick border = added by this task
- rectangle = off-the-shelf product; cylinder = database
- arrow = call, from caller to callee; `owns` = the service owns the database; `streams` = the database streams to the replica

Client calls use HTTPS, calls to the Event bus use AMQP, and every other call uses gRPC. The Inventory service consumes `pick.completed` and publishes `stock.changed`. Not drawn: the zone of each container, which the Zone column of the table lists.