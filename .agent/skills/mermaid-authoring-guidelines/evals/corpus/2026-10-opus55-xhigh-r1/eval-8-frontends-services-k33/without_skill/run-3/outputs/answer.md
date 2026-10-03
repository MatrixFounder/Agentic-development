```mermaid
flowchart LR
    accTitle: Front-end calls to domain services
    accDescr: Web shop, Mobile BFF and Partner API each call Catalog service, Pricing service and Stock service directly over HTTP/JSON, with no API gateway between them.

    subgraph FE["Front-ends"]
        WEB["Web shop"]
        BFF["Mobile BFF"]
        PAPI["Partner API"]
    end

    subgraph DS["Domain services"]
        CAT["Catalog service"]
        PRC["Pricing service"]
        STK["Stock service"]
    end

    WEB --> CAT & PRC & STK
    BFF --> CAT & PRC & STK
    PAPI --> CAT & PRC & STK
```

*Figure 2.4: Each front-end calls each domain service directly over HTTP/JSON (FS-1), with no API gateway between them (FS-2). Calls between domain services and calls from the Admin console are not shown.*