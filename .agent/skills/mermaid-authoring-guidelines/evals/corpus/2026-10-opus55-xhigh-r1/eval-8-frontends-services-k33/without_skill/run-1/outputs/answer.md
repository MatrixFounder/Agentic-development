```mermaid
flowchart LR
    accTitle: Front-end calls to domain services
    accDescr: Web shop, Mobile BFF and Partner API each call Catalog service, Pricing service and Stock service directly over HTTP/JSON. There is no API gateway between them.

    subgraph fe["Front-ends"]
        web["Web shop"]
        bff["Mobile BFF"]
        partner["Partner API"]
    end

    subgraph ds["Domain services"]
        catalog["Catalog service"]
        pricing["Pricing service"]
        stock["Stock service"]
    end

    web & bff & partner --> catalog & pricing & stock
```

*Figure 2.4 — Front-end calls to domain services.* Each front-end calls each domain service directly over HTTP/JSON, with no API gateway between them (FS-1, FS-2). The figure leaves out Stock service's calls to Pricing service (FS-3), the Admin console (FS-4) and the Warehouse feed (FS-5).