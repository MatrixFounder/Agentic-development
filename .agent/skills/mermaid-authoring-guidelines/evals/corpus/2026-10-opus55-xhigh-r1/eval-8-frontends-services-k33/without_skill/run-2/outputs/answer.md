```mermaid
flowchart LR
    subgraph frontends["Front-ends"]
        web["Web shop"]
        bff["Mobile BFF"]
        partner["Partner API"]
    end
    subgraph services["Domain services"]
        catalog["Catalog service"]
        pricing["Pricing service"]
        stock["Stock service"]
    end
    web --> catalog
    web --> pricing
    web --> stock
    bff --> catalog
    bff --> pricing
    bff --> stock
    partner --> catalog
    partner --> pricing
    partner --> stock
```

*Figure 2.4: Calls from the front-ends to the domain services (FS-1). Each arrow is a direct HTTP/JSON call, and no API gateway sits between them (FS-2). The figure leaves out Stock service → Pricing service (FS-3), the Admin console (FS-4) and the Warehouse feed (FS-5).*