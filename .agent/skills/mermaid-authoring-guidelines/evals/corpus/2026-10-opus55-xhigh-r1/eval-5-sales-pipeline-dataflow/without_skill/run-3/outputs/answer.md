The figure below shows how sales data moves from the three sources, through the pipeline stages, to the consumers listed in §5.2. Cylinders are data stores. Dashed arrows are the Data quality monitor's reads and its alert.

```mermaid
flowchart TB
    accTitle: Sales data pipeline data flow
    accDescr: POS feeds, web orders and the loyalty CSV land in the Raw zone. The Normalizer, Deduplicator and Warehouse loader move the data through Staging tables and Clean sales into the Sales warehouse. Finance dashboards and the Demand forecast job read the Sales warehouse, and the Demand forecast job writes forecasts to the external Planning system. The Data quality monitor reads Staging tables and the Sales warehouse and alerts the on-call channel when a feed is more than 2 hours late.

    subgraph sources["Sources"]
        pos["POS feeds<br>12 regions, CSV over SFTP"]
        web["Web orders<br>JSON export"]
        loyalty["Loyalty CSV<br>loyalty card purchases"]
    end

    subgraph pipeline["Pipeline"]
        raw[("Raw zone")]
        normalizer["Normalizer<br>hourly"]
        staging[("Staging tables")]
        dedup["Deduplicator<br>hourly, after Normalizer"]
        clean[("Clean sales")]
        loader["Warehouse loader<br>nightly"]
        warehouse[("Sales warehouse")]
    end

    subgraph consumers["Consumers"]
        finance["Finance dashboards"]
        forecast["Demand forecast job<br>weekly"]
        dq["Data quality monitor"]
    end

    planning["Planning system<br>external supply system"]
    oncall["#sales-data-oncall"]

    pos -- "hourly" --> raw
    web -- "hourly" --> raw
    loyalty -- "daily" --> raw
    raw --> normalizer --> staging --> dedup --> clean --> loader --> warehouse
    warehouse --> finance
    warehouse --> forecast
    forecast -- "forecasts" --> planning
    staging -.-> dq
    warehouse -.-> dq
    dq -. "feed more than 2 h late" .-> oncall
```