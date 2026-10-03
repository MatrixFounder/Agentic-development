**Рисунок 4.1.** Развёртывание МедЗаписи: узлы ЦОД-1 и ЦОД-2, путь запросов от пациентов и регистратуры до СУБД основной, репликация и резервные копии.

```mermaid
%%{init: {"layout": "dagre", "look": "classic", "flowchart": {"nodeSpacing": 45, "rankSpacing": 55, "wrappingWidth": 400}}}%%
flowchart TB
  accTitle: Развёртывание МедЗаписи
  accDescr: Узлы ЦОД-1 и ЦОД-2, путь запросов от пациентов и регистратуры до СУБД основной, репликация и резервные копии.
  PAT(["Пациенты"])
  REG(["Рабочие места регистратуры"])
  subgraph DC1["ЦОД-1 · основной"]
    WAF["WAF<br/><small>единственный вход из Интернета</small>"]
    VPN["VPN-шлюз<br/><small>вход для рабочих мест регистратуры</small>"]
    LB["Балансировщик<br/><small>HAProxy · пара active/passive</small>"]
    APP("Узлы приложения<br/><small>app-01 · app-02 · app-03</small>")
    DB1[("СУБД основная<br/><small>PostgreSQL 15</small>")]
    MON{{"Сервер мониторинга<br/><small>Zabbix · опрашивает все узлы обоих ЦОД</small>"}}
  end
  subgraph DC2["ЦОД-2 · резервный"]
    BAK{{"Сервер резервных копий<br/><small>хранит копии 14 дней</small>"}}
    DB2[("СУБД резервная<br/><small>отставание до 5 с</small>")]
  end
  PAT -->|"сайт записи · HTTPS"| WAF
  REG -->|"подключение"| VPN
  WAF -->|"запросы"| LB
  VPN -->|"запросы"| LB
  LB -->|"распределяет запросы"| APP
  APP -->|"чтение · запись"| DB1
  BAK -->|"снимает копии каждые 6 ч"| DB1
  DB1 -->|"асинхронная репликация"| DB2
  %% layout only
  DB1 ~~~ MON
  class PAT,REG ext
  class APP wf
  class DB1,DB2 db
  class WAF,VPN,LB svc
  class MON,BAK infra
  style DC1 fill:#7F7F7F0D,stroke:#90A4AE
  style DC2 fill:#7F7F7F0D,stroke:#90A4AE
  classDef ext fill:#FFFFFF,stroke:#607D8B,color:#263238,stroke-dasharray:4 3
  classDef wf fill:#E8F0FB,stroke:#2E5A8A,color:#0F2A47
  classDef db fill:#F3EEF9,stroke:#5E35B1,color:#2A1653
  classDef svc fill:#F5F5F5,stroke:#546E7A,color:#1F2A30
  classDef infra fill:#FAFAFA,stroke:#8D6E63,color:#3E2723
```

Легенда:
- овал с пунктирной рамкой = вне системы: пациенты и рабочие места регистратуры
- прямоугольник = сетевой узел; скруглённый блок = узлы приложения
- цилиндр = СУБД; шестиугольник = сервер мониторинга или резервных копий
- серая рамка = центр обработки данных
- стрелка = действие из подписи, от узла, который его выполняет; репликация идёт от СУБД основной к резервной
- не нарисованы: опрос всех узлов сервером мониторинга (он указан на самом узле) и ручное переключение при отказе ЦОД-1 (§4.3)