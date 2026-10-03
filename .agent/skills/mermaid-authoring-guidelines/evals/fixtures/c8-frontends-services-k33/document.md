### 2.4 Front-ends and domain services

Tallowbrook sells through three front-ends. Each front-end belongs to one team and ships on its own
schedule.

| Front-end | What it is |
| :--- | :--- |
| Web shop | the storefront; its pages are rendered on the server |
| Mobile BFF | the backend-for-frontend of the iOS and Android apps |
| Partner API | the public REST interface for marketplace partners |

Product data, prices and stock levels belong to the three domain services: Catalog service,
Pricing service and Stock service. A front-end holds no business rule of its own; it asks the
domain services.

#### 2.4.1 Calls

- **FS-1.** Each front-end calls each domain service directly over HTTP/JSON.
- **FS-2.** There is no API gateway between them (decision D-7). A gateway was rejected because it
  adds a network hop to every page view.
- **FS-3.** Stock service calls Pricing service to price reserved items.
- **FS-4.** The Admin console writes to Catalog service and Pricing service.
- **FS-5.** Stock service imports the Warehouse feed, a nightly SFTP drop of stock levels.

#### 2.4.2 Limits

| Subject | Limit |
| :--- | :--- |
| Partner API | 100 requests/s per partner |
| Web shop | caches catalog responses for 60 s |
| Pricing service | answers within 80 ms at p99 |

A partner that exceeds its rate receives an error and retries later. Web shop and Mobile BFF have
no rate limit of their own.
