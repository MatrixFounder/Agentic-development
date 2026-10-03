**Figure 3.1.** Larkspur WMS containers: the calls between them, the databases the services own and the replication stream.

```mermaid
%%{init: {"layout": "dagre", "look": "classic", "flowchart": {"nodeSpacing": 45, "rankSpacing": 55, "wrappingWidth": 400}}}%%
flowchart TB
  accTitle: Larkspur WMS containers
  accDescr: The calls between the containers, the databases the services own and the replication stream.
  CLI(["Client apps<br/><small>Handheld app · Supervisor console</small>"])
  GW["API gateway<br/><small>Kong · DMZ</small>"]
  PICK("Picking service<br/><small>Java · application zone</small>")
  PDB[("Picking DB<br/><small>MariaDB · data zone</small>")]
  LBL("Label printer bridge<br/><small>Go · application zone</small>")
  INV("Inventory service<br/><small>Java · application zone</small>")
  BUS["Event bus<br/><small>RabbitMQ · application zone</small>"]
  IDB[("Inventory DB<br/><small>MariaDB · data zone</small>")]
  REP[("Reporting replica<br/><small>MariaDB · read-only · data zone</small>")]
  SLOT("Slotting service<br/><small>Python · application zone</small>")
  CLI -->|"https"| GW
  GW -->|"pick tasks"| PICK
  PICK -->|"owns"| PDB
  PICK -->|"print label"| LBL
  PICK -->|"reserve stock"| INV
  PICK -->|"publish pick.completed"| BUS
  GW -->|"stock queries"| INV
  INV -->|"consume · publish"| BUS
  INV -->|"owns"| IDB
  IDB -->|"streams"| REP
  SLOT -->|"store slot assignments"| INV
  SLOT -->|"consume stock.changed"| BUS
  class CLI ext
  class PICK,LBL,INV wf
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
- dashed stadium = the two client apps
- rounded box = service the Larkspur team writes; orange with a thick border = added by this task
- rectangle = off-the-shelf product; cylinder = database
- second line = technology and zone
- arrow labelled `owns` = the service owns the database; arrow labelled `streams` = replication;
  every other arrow = a call, from caller to callee