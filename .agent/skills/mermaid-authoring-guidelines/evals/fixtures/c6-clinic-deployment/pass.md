**Рисунок 1.** Развёртывание МедЗаписи — узлы основного ЦОД-1 и резервного ЦОД-2, запросы и потоки данных между ними.

```mermaid
%%{init: {"layout": "dagre", "look": "classic", "flowchart": {"nodeSpacing": 45, "rankSpacing": 55, "wrappingWidth": 400}}}%%
flowchart TB
    accTitle: Развёртывание МедЗаписи
    accDescr: Узлы основного ЦОД-1 и резервного ЦОД-2, запросы и потоки данных между ними.
    PAT(["Пациенты"])
    REG(["Рабочие места регистратуры"])
    subgraph DC1["ЦОД-1"]
        WAF["WAF"]
        VPN["VPN-шлюз"]
        LB["Балансировщик<br/><small>HAProxy, пара active/passive</small>"]
        APP("Узлы приложения<br/><small>app-01 · app-02 · app-03</small>")
        DB1[("СУБД основная<br/><small>PostgreSQL 15</small>")]
        MON["Сервер мониторинга<br/><small>Zabbix</small>"]
    end
    subgraph DC2["ЦОД-2"]
        DB2[("СУБД резервная")]
        BAK{{"Сервер резервных копий<br/><small>хранит копии 14 дней</small>"}}
    end
    PAT -->|"по HTTPS"| WAF
    REG --> VPN
    WAF --> LB
    VPN --> LB
    LB --> APP
    APP --> DB1
    DB1 -->|"репликация · до 5 с"| DB2
    DB1 -->|"копии каждые 6 ч"| BAK
    class PAT,REG ext
    class WAF,VPN,LB,MON svc
    class APP wf
    class DB1,DB2 db
    class BAK infra
    style DC1 fill:#7F7F7F0D,stroke:#90A4AE
    style DC2 fill:#7F7F7F0D,stroke:#90A4AE
    classDef ext fill:#FFFFFF,stroke:#607D8B,color:#263238,stroke-dasharray:4 3
    classDef wf fill:#E8F0FB,stroke:#2E5A8A,color:#0F2A47
    classDef db fill:#F3EEF9,stroke:#5E35B1,color:#2A1653
    classDef svc fill:#F5F5F5,stroke:#546E7A,color:#1F2A30
    classDef infra fill:#FAFAFA,stroke:#8D6E63,color:#3E2723
```

- Пунктирный стадион: пользователи вне системы.
- Прямоугольник: сетевой узел или служебный сервер.
- Скруглённый прямоугольник: узлы приложения.
- Цилиндр: СУБД.
- Шестиугольник: сервер, который снимает копии по расписанию.
- Серая рамка: ЦОД; ЦОД-1 основной, ЦОД-2 резервный.
- Стрелка: запрос или данные, от отправителя к получателю.
- Не нарисованы: опрос всех узлов сервером мониторинга и переключение при отказе ЦОД-1.
