**Рисунок 4.1.** Развёртывание МедЗаписи: узлы обоих ЦОД, путь запроса от пациентов и регистратуры до СУБД основной, репликация и снятие резервных копий.

```mermaid
%%{init: {"layout": "dagre", "look": "classic", "flowchart": {"nodeSpacing": 45, "rankSpacing": 55, "wrappingWidth": 400}}}%%
flowchart TB
  accTitle: Развёртывание МедЗаписи
  accDescr: Узлы обоих ЦОД, путь запроса от пациентов и регистратуры до СУБД основной, репликация и снятие резервных копий.
  PAT(["Пациенты"])
  REG(["Рабочие места регистратуры"])
  subgraph ZA["ЦОД-1 · основной"]
    WAF["WAF<br/><small>единственный вход из Интернета</small>"]
    VPN["VPN-шлюз<br/><small>вход для рабочих мест регистратуры</small>"]
    LB["Балансировщик<br/><small>HAProxy · пара active/passive</small>"]
    APP("Узлы приложения<br/><small>app-01 · app-02 · app-03</small>")
    PGA[("СУБД основная<br/><small>PostgreSQL 15 · данные приложения</small>")]
    MON["Сервер мониторинга<br/><small>Zabbix · опрашивает все узлы обоих ЦОД</small>"]
  end
  subgraph ZB["ЦОД-2 · резервный"]
    BK["Сервер резервных копий<br/><small>хранит копии 14 дней</small>"]
    PGB[("СУБД резервная<br/><small>отставание до 5 с · только чтение</small>")]
  end
  PAT -->|"HTTPS"| WAF
  REG -->|"подключение"| VPN
  WAF -->|"запросы"| LB
  VPN -->|"запросы"| LB
  LB -->|"распределяет запросы"| APP
  APP -->|"чтение · запись"| PGA
  PGA -->|"асинхронная репликация"| PGB
  BK -->|"копии каждые 6 ч"| PGA
  %% layout only
  PGA ~~~ MON
  class PAT,REG ext
  class APP wf
  class PGA,PGB db
  class WAF,VPN,LB,MON,BK svc
  style ZA fill:#7F7F7F0D,stroke:#90A4AE
  style ZB fill:#7F7F7F0D,stroke:#90A4AE
  classDef ext fill:#FFFFFF,stroke:#607D8B,color:#263238,stroke-dasharray:4 3
  classDef wf fill:#E8F0FB,stroke:#2E5A8A,color:#0F2A47
  classDef db fill:#F3EEF9,stroke:#5E35B1,color:#2A1653
  classDef svc fill:#F5F5F5,stroke:#546E7A,color:#1F2A30
```

Легенда:
- овал со штриховой рамкой: пользователи вне системы; прямоугольник: инфраструктурный узел;
- скруглённый блок: узлы приложения; цилиндр: СУБД;
- серая рамка: ЦОД;
- стрелка: обращение от того, кто его начинает; у репликации стрелка идёт от основной СУБД к резервной;
- не нарисованы: опрос всех узлов сервером мониторинга (он указан во второй строке узла) и ручное переключение при отказе ЦОД-1 (§4.3).