**Figure 2.4.** Front-end calls: which front-end calls which domain service.

| Front-end | Catalog service | Pricing service | Stock service |
| :--- | :--- | :--- | :--- |
| Web shop | calls | calls | calls |
| Mobile BFF | calls | calls | calls |
| Partner API | calls | calls | calls |

- calls = a direct call over HTTP/JSON (FS-1); no API gateway sits between a front-end and a domain service (FS-2, D-7).
- Not shown: Stock service's calls to Pricing service (FS-3), the Admin console's writes (FS-4) and the Warehouse feed (FS-5).