## 3. Containers

Larkspur WMS runs the warehouse floor of one site. This section lists its containers, the calls
between them and the limits that apply. Slotting service is added by this task; every other
container exists today. The two client apps are the Handheld app and the Supervisor console. The
Larkspur team writes the four services; the API gateway and the Event bus are off-the-shelf
products.

### 3.1 Containers

| Container | Technology | Zone | Owns |
| :--- | :--- | :--- | :--- |
| Handheld app | Android app, used by floor operators | — | — |
| Supervisor console | web app, used by shift supervisors | — | — |
| API gateway | Kong | DMZ | — |
| Inventory service | Java service | application zone | Inventory DB |
| Picking service | Java service | application zone | Picking DB |
| Slotting service | Python service | application zone | — |
| Label printer bridge | Go service | application zone | — |
| Event bus | RabbitMQ | application zone | — |
| Inventory DB | MariaDB | data zone | — |
| Picking DB | MariaDB | data zone | — |
| Reporting replica | MariaDB, read-only | data zone | — |

### 3.2 Calls

Every client call enters through the API gateway.

| Caller | Callee | Protocol | Purpose |
| :--- | :--- | :--- | :--- |
| Handheld app | API gateway | HTTPS | pick tasks and scans |
| Supervisor console | API gateway | HTTPS | stock and pick reports |
| API gateway | Inventory service | gRPC | stock queries |
| API gateway | Picking service | gRPC | pick tasks |
| Picking service | Inventory service | gRPC | reserve stock, synchronous |
| Picking service | Label printer bridge | gRPC | print label |
| Picking service | Event bus | AMQP | publishes `pick.completed` |
| Inventory service | Event bus | AMQP | consumes `pick.completed`, publishes `stock.changed` |
| Slotting service | Event bus | AMQP | consumes `stock.changed` |
| Slotting service | Inventory service | gRPC | stores slot assignments |

Slotting service stores its slot assignments through the Inventory service API; it has no database
of its own. The Inventory DB streams to the Reporting replica. No other database is replicated.

### 3.3 Pick flow

1. A floor operator scans a tote with the Handheld app.
2. The Picking service returns the next pick task.
3. The Picking service reserves the stock in the Inventory service.
4. The operator confirms the pick on the Handheld app.
5. The Label printer bridge prints the shipping label.
6. The Picking service publishes `pick.completed`, and the Inventory service lowers the stock.

### 3.4 Limits

| Subject | Limit |
| :--- | :--- |
| API gateway | a client call times out after 15 s |
| Stock reservation | released after 120 s without a confirmed pick |
| Label printing | retried 3 times |
| Reporting replica | an alert fires when the lag exceeds 30 s |
