**Рисунок 1.** Состояния заявки на отпуск. Каждый переход подписан исполнителем, а где текст исполнителя не называет, подписан условием.

```mermaid
%%{init: {"layout": "dagre", "look": "classic"}}%%
stateDiagram-v2
    accTitle: Состояния заявки на отпуск
    accDescr: Каждый переход подписан исполнителем, а где текст исполнителя не называет, подписан условием.
    direction TB
    state "Черновик" as draft
    state "На согласовании" as review
    state "Согласована" as approved
    state "Возвращена" as returned
    state "Отклонена" as rejected
    state "Запланирована" as scheduled
    state "В отпуске" as onleave
    state "Завершена" as completed
    state "Отменена" as cancelled
    [*] --> draft : сотрудник
    draft --> review : сотрудник
    review --> approved : руководитель
    review --> returned : руководитель
    returned --> review : сотрудник
    review --> rejected : руководитель
    approved --> scheduled : hr_schedule()
    scheduled --> onleave : наступила дата начала
    onleave --> completed : наступила дата окончания
    approved --> cancelled : сотрудник
    scheduled --> cancelled : сотрудник
    classDef hold fill:#E8F0FB,stroke:#2E5A8A,color:#0F2A47,stroke-width:2px
    classDef wait fill:#FFFFFF,stroke:#607D8B,color:#263238
    classDef final fill:#ECEFF1,stroke:#37474F,color:#263238,stroke-dasharray:4 3
    class approved,scheduled,onleave hold
    class draft,review,returned wait
    class completed,rejected,cancelled final
```

1. Закрашенный кружок обозначает начало: сотрудник создаёт заявку.
2. Толстая синяя рамка и бледно-голубая заливка обозначают резерв дней: дни отпуска списаны с остатка сотрудника.
3. Тонкая серо-синяя рамка и белая заливка обозначают состояние без резерва дней.
4. Пунктирная тёмно-серая рамка и светло-серая заливка обозначают итоговое состояние. Из него заявка не выходит.
5. Метка перехода называет исполнителя. `hr_schedule()` — функция, которой служба кадров вносит заявку в график. «Наступила дата начала» и «наступила дата окончания» — условия, потому что исполнителя текст не называет.
6. Сотрудник может отменить заявку из «Запланирована» не позднее чем за 2 дня до начала отпуска.