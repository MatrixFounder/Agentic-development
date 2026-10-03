## 5. Sales data pipeline

Every sale of Corvid Retail reaches the Sales warehouse through the pipeline of this section.
Finance, supply planning and the data team read the results.

### 5.1 Sources and stages

Three sources deliver sales records. Each source drops its files into the Raw zone bucket.

| Source | What it delivers | Delivery |
| :--- | :--- | :--- |
| POS feeds | one CSV file per region and hour, over SFTP | hourly |
| Web orders | a JSON export of the web shop's orders | hourly |
| Loyalty CSV | the purchases of loyalty card holders | daily |

The 12 regional POS feeds are North, North-East, East, South-East, South, South-West, West,
North-West, Central, Highlands, Coast and Islands.

| Stage | Runs | Reads | Writes |
| :--- | :--- | :--- | :--- |
| Normalizer | hourly | Raw zone | Staging tables |
| Deduplicator | hourly, after Normalizer | Staging tables | Clean sales |
| Warehouse loader | nightly | Clean sales | Sales warehouse |

### 5.2 Consumers

- Finance dashboards read the Sales warehouse.
- The Demand forecast job runs weekly. It reads the Sales warehouse.
- The Demand forecast job writes forecasts to the Planning system, an external supply system.
- The Data quality monitor reads Staging tables and the Sales warehouse.
- The Data quality monitor alerts `#sales-data-oncall` when a feed is more than 2 h late.

### 5.3 Retention and late files

| Store | Keeps data for |
| :--- | :--- |
| Raw zone | 90 days |
| Sales warehouse | 7 years |

A late file is accepted for 48 h after its hour. A file that arrives later is rejected.
