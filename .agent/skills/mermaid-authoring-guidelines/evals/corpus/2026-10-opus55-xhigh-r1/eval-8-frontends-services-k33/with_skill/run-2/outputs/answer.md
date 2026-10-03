**Table 2.4.** Front-end calls: each front-end calls each of the three domain services.

| Front-end | Catalog service | Pricing service | Stock service |
| :--- | :--- | :--- | :--- |
| Web shop | calls | calls | calls |
| Mobile BFF | calls | calls | calls |
| Partner API | calls | calls | calls |

Every call goes directly over HTTP/JSON, with no API gateway in between (FS-1, FS-2). Two callers are not shown because they are not front-ends: the Admin console writes to Catalog service and Pricing service (FS-4), and Stock service calls Pricing service (FS-3).