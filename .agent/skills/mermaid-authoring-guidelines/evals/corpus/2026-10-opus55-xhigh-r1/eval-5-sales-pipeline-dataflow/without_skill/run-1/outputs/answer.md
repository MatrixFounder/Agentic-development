The diagram below shows how sales data moves from the sources to the consumers. Cylinders are data stores. Solid arrows carry sales data. Dashed arrows are the reads and alerts of the Data quality monitor.

```mermaid
flowchart TD
    accTitle: Sales data pipeline data flow
    accDescr: POS feeds, web orders and the loyalty CSV land in the Raw zone. The Normalizer, Deduplicator and Warehouse loader move the data through Staging tables and Clean sales into the Sales warehouse. Finance dashboards and the Demand forecast job read the Sales warehouse, and the forecast job writes to the external Planning system. The Data quality monitor reads Staging tables and the Sales warehouse and alerts the sales-data-oncall channel.

    subgraph sources["Sources"]
        pos["POS feeds<br/>12 regions, SFTP, hourly"]
        web["Web orders<br/>JSON export, hourly"]
        loyalty["Loyalty CSV<br/>daily"]
    end

    subgraph pipeline["Pipeline"]
        raw[("Raw zone")]
        normalizer["Normalizer<br/>hourly"]
        staging[("Staging tables")]
        dedup["Deduplicator<br/>hourly, after Normalizer"]
        clean[("Clean sales")]
        loader["Warehouse loader<br/>nightly"]
        warehouse[("Sales warehouse")]
    end

    subgraph consumers["Consumers"]
        finance["Finance dashboards"]
        forecast["Demand forecast job<br/>weekly"]
        dq["Data quality monitor"]
    end

    planning["Planning system<br/>external supply system"]
    alerts["#sales-data-oncall"]

    pos --> raw
    web --> raw
    loyalty --> raw
    raw --> normalizer --> staging --> dedup --> clean --> loader --> warehouse
    warehouse --> finance
    warehouse --> forecast
    forecast --> planning
    staging -.-> dq
    warehouse -.-> dq
    dq -.->|"feed more than 2 h late"| alerts

    classDef external stroke-dasharray: 5 5
    class planning external
```