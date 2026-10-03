The figure groups the containers by zone. Arrows run from caller to callee, as listed in §3.2. The dashed box is the Slotting service that this task adds, and the dotted arrow is database replication.

```mermaid
flowchart TB
    accTitle: Larkspur WMS containers
    accDescr: The Handheld app and the Supervisor console call the API gateway in the DMZ, which calls the Inventory and Picking services in the application zone. The Picking service calls the Inventory service and the Label printer bridge. The Picking, Inventory and Slotting services use the Event bus, and the Slotting service stores slot assignments through the Inventory service. The Inventory and Picking services each own a MariaDB database in the data zone, and the Inventory DB streams to the Reporting replica.

    handheld["Handheld app<br/>Android, floor operators"]
    console["Supervisor console<br/>web app, shift supervisors"]

    subgraph dmz["DMZ"]
        gateway["API gateway<br/>Kong"]
    end

    subgraph app["Application zone"]
        inventory["Inventory service<br/>Java"]
        picking["Picking service<br/>Java"]
        slotting["Slotting service<br/>Python"]
        printer["Label printer bridge<br/>Go"]
        bus["Event bus<br/>RabbitMQ"]
    end

    subgraph data["Data zone"]
        invdb[("Inventory DB<br/>MariaDB")]
        pickdb[("Picking DB<br/>MariaDB")]
        replica[("Reporting replica<br/>MariaDB, read-only")]
    end

    handheld -->|"HTTPS"| gateway
    console -->|"HTTPS"| gateway
    gateway -->|"gRPC: stock queries"| inventory
    gateway -->|"gRPC: pick tasks"| picking
    picking -->|"gRPC: reserve stock, synchronous"| inventory
    picking -->|"gRPC: print label"| printer
    picking -->|"AMQP: publishes pick.completed"| bus
    inventory -->|"AMQP: consumes pick.completed,<br/>publishes stock.changed"| bus
    slotting -->|"AMQP: consumes stock.changed"| bus
    slotting -->|"gRPC: stores slot assignments"| inventory
    inventory -->|"owns"| invdb
    picking -->|"owns"| pickdb
    invdb -.->|"streams to"| replica

    classDef added stroke-dasharray: 5 5
    class slotting added
```