**Figure 1.** Container view — who calls whom in Larkspur WMS, which events pass through the Event
bus, and which service owns which database.

```mermaid
%%{init: {"layout": "dagre", "look": "classic", "flowchart": {"nodeSpacing": 45, "rankSpacing": 55, "wrappingWidth": 400}}}%%
flowchart TB
  accTitle: Container view of Larkspur WMS
  accDescr: The two client apps call the API gateway, which calls the Picking service and the Inventory service. The Picking service reserves stock, prints labels and publishes pick.completed. The Slotting service consumes stock.changed and stores slot assignments through the Inventory service.
  HH(["Handheld app"])
  SC(["Supervisor console"])
  GW["API gateway"]
  PICK("Picking service")
  INV("Inventory service")
  SLOT("Slotting service")
  LBL("Label printer bridge")
  BUS["Event bus"]
  PDB[("Picking DB")]
  IDB[("Inventory DB")]
  HH -->|"HTTPS"| GW
  SC -->|"HTTPS"| GW
  GW -->|"pick tasks"| PICK
  GW -->|"stock queries"| INV
  PICK -->|"reserve stock"| INV
  PICK -->|"print label"| LBL
  PICK -.->|"pick.completed"| BUS
  BUS <-.->|"consumes · publishes"| INV
  BUS -.->|"stock.changed"| SLOT
  SLOT -->|"slot assignments"| INV
  PICK -->|"owns"| PDB
  INV -->|"owns"| IDB
  classDef ext fill:#FFFFFF,stroke:#607D8B,color:#263238,stroke-dasharray:4 3
  classDef wf fill:#E8F0FB,stroke:#2E5A8A,color:#0F2A47
  classDef wfNew fill:#FFF4E0,stroke:#B36B00,color:#4A2C00,stroke-width:2px
  classDef db fill:#F3EEF9,stroke:#5E35B1,color:#2A1653
  classDef svc fill:#F5F5F5,stroke:#546E7A,color:#1F2A30
  class HH,SC ext
  class PICK,INV,LBL wf
  class SLOT wfNew
  class GW,BUS svc
  class PDB,IDB db
```

Legend:
- dashed stadium = client app
- grey rectangle = off-the-shelf product
- blue rounded box = service written by the Larkspur team
- orange rounded box with a thick border = service added by this task
- cylinder = database
- solid arrow = a call, from caller to callee; into a cylinder, the database the service owns
- dashed arrow = an event through the Event bus; two heads = the service consumes and publishes
- not drawn: the Inventory DB also streams to the Reporting replica of the data zone
