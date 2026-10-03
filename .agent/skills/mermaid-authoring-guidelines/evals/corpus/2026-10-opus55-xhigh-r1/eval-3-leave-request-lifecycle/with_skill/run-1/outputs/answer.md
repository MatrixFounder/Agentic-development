**Рисунок 2.3.** Состояния заявки на отпуск. Каждый переход подписан исполнителем. Где §2.3.1 исполнителя не называет, переход подписан условием.

```mermaid
%%{init: {"layout": "dagre", "look": "classic"}}%%
stateDiagram-v2
    accTitle: Состояния заявки на отпуск
    accDescr: Каждый переход подписан исполнителем, а там, где текст его не называет, условием.
    direction TB
    state "Черновик" as draft
    state "На согласовании" as review
    state "Согласована" as approved
    state "Запланирована" as scheduled
    state "В отпуске" as onleave
    state "Завершена" as done
    state "Отменена" as cancelled
    state "Возвращена" as returned
    state "Отклонена" as rejected
    [*] --> draft : сотрудник
    draft --> review : сотрудник
    review --> approved : руководитель
    approved --> scheduled : hr_schedule()
    scheduled --> onleave : дата начала
    onleave --> done : дата окончания
    approved --> cancelled : сотрудник
    scheduled --> cancelled : сотрудник
    review --> returned : руководитель
    returned --> review : сотрудник
    review --> rejected : руководитель
    classDef hold fill:#E8F0FB,stroke:#2E5A8A,color:#0F2A47,stroke-width:2px
    classDef wait fill:#FFFFFF,stroke:#607D8B,color:#263238
    classDef final fill:#ECEFF1,stroke:#37474F,color:#263238,stroke-dasharray:4 3
    class approved,scheduled,onleave hold
    class draft,review,returned wait
    class done,rejected,cancelled final
```

1. Закрашенный кружок обозначает создание заявки.
2. Толстая синяя рамка и бледно-голубая заливка: дни отпуска зарезервированы («Резерв дней» = да).
3. Тонкая серо-синяя рамка и белая заливка: дни не зарезервированы.
4. Пунктирная тёмно-серая рамка обозначает итоговое состояние. Из него заявка не выходит.
5. Подпись перехода называет его исполнителя. Подписи «дата начала» и «дата окончания» обозначают условия: наступает дата начала или дата окончания отпуска.
6. Запланированную заявку сотрудник отменяет не позднее чем за 2 дня до начала отпуска.
7. На рисунке нет напоминания и эскалации от ночного задания (§2.3.3), потому что они не меняют состояние заявки.