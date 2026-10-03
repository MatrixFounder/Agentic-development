**Рисунок 4.1.** Развёртывание МедЗаписи: все узлы основного ЦОД-1 и резервного ЦОД-2, путь запросов пациентов и регистратуры до СУБД основной, её репликация и резервные копии.

```mermaid
%%{init: {"layout": "dagre", "look": "classic", "flowchart": {"nodeSpacing": 45, "rankSpacing": 55, "wrappingWidth": 400}}}%%
flowchart TB
  accTitle: Развёртывание МедЗаписи
  accDescr: Все узлы основного ЦОД-1 и резервного ЦОД-2, путь запросов пациентов и регистратуры до СУБД основной, её репликация и резервные копии.
  PAT(["Пациенты"])
  REG(["Рабочие места регистратуры"])
  subgraph DC1["ЦОД-1"]
    WAF["WAF<br/><small>единственный вход из Интернета</small>"]
    VPN["VPN-шлюз"]
    LB["Балансировщик<br/><small>HAProxy · пара active/passive</small>"]
    APP("Узлы приложения<br/><small>app-01 · app-02 · app-03</small>")
    DBM[("СУБД основная<br/><small>PostgreSQL 15 · данные приложения</small>")]
    MON["Сервер мониторинга<br/><small>Zabbix · опрашивает все узлы</small>"]
  end
  subgraph DC2["ЦОД-2"]
    DBR[("СУБД резервная<br/><small>отставание до 5 с · только чтение</small>")]
    BAK["Сервер резервных копий<br/><small>хранит копии 14 дней</small>"]
  end
  PAT -->|"сайт записи · HTTPS"| WAF
  WAF -->|"запросы"| LB
  LB -->|"распределяет запросы"| APP
  APP -->|"чтение · запись"| DBM
  DBM -->|"асинхронная репликация"| DBR
  DBM -->|"копии каждые 6 ч"| BAK
  REG -->|"подключение"| VPN
  VPN -->|"запросы"| LB
  %% layout only
  APP ~~~ MON
  class PAT,REG ext
  class WAF,VPN,LB,MON,BAK svc
  class APP wf
  class DBM,DBR db
  style DC1 fill:#7F7F7F0D,stroke:#90A4AE
  style DC2 fill:#7F7F7F0D,stroke:#90A4AE
  classDef ext fill:#FFFFFF,stroke:#607D8B,color:#263238,stroke-dasharray:4 3
  classDef wf fill:#E8F0FB,stroke:#2E5A8A,color:#0F2A47
  classDef db fill:#F3EEF9,stroke:#5E35B1,color:#2A1653
  classDef svc fill:#F5F5F5,stroke:#546E7A,color:#1F2A30
```

Условные обозначения:
- овал с пунктирной рамкой — вне системы: пациенты и рабочие места регистратуры
- прямоугольник — шлюз, балансировщик или служебный сервер; скруглённый прямоугольник — узлы приложения; цилиндр — СУБД
- серая рамка — ЦОД
- стрелка — запросы или поток данных, от отправителя к получателю
- не показано: опрос всех узлов обоих ЦОД сервером мониторинга; ручное продвижение СУБД резервной и переключение DNS при отказе ЦОД-1 (§4.3)