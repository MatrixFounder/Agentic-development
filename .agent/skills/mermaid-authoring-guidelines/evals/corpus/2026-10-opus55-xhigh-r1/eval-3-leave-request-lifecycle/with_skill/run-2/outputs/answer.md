**Рисунок 2.3.** Состояния заявки на отпуск. Каждый переход подписан исполнителем, а где текст исполнителя не называет, условием.

```mermaid
%%{init: {"layout": "dagre", "look": "classic"}}%%
stateDiagram-v2
    accTitle: Состояния заявки на отпуск
    accDescr: Каждый переход подписан исполнителем, а где текст исполнителя не называет, условием.
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
    approved --> scheduled : hr_schedule()
    scheduled --> onleave : дата начала
    onleave --> completed : дата окончания
    approved --> cancelled : сотрудник
    review --> returned : руководитель
    returned --> review : сотрудник
    review --> rejected : руководитель
    classDef hold fill:#E8F0FB,stroke:#2E5A8A,color:#0F2A47,stroke-width:2px
    classDef wait fill:#FFFFFF,stroke:#607D8B,color:#263238
    classDef final fill:#ECEFF1,stroke:#37474F,color:#263238,stroke-dasharray:4 3
    class approved,scheduled,onleave hold
    class draft,review,returned wait
    class completed,rejected,cancelled final
```

1. Закрашенный кружок обозначает начало: сотрудник создаёт заявку.
2. Толстая синяя рамка с голубой заливкой означает резерв дней: дни отпуска списаны с остатка
   сотрудника.
3. Тонкая серо-голубая рамка с белой заливкой означает, что резерва дней нет.
4. Пунктирная тёмно-серая рамка со светло-серой заливкой обозначает итоговое состояние. Из него
   заявка не выходит.
5. Подпись перехода называет исполнителя так, как его называет текст. `hr_schedule()` — функция
   службы кадров. «дата начала» и «дата окончания» — условия: наступает дата начала или дата
   окончания отпуска.
6. На рисунке не показан один переход: сотрудник отменяет и запланированную заявку, не позднее чем
   за 2 дня до начала отпуска.