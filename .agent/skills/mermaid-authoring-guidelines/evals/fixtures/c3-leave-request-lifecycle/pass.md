**Рисунок 1.** Жизненный цикл заявки на отпуск — девять состояний и переходы между ними; на переходе
указан исполнитель, а где текст его не называет, — условие.

```mermaid
%%{init: {"layout": "dagre", "look": "classic"}}%%
stateDiagram-v2
  accTitle: Жизненный цикл заявки на отпуск
  accDescr: Девять состояний заявки на отпуск и переходы между ними. На переходе указан исполнитель, а где текст его не называет, условие.
  direction TB
  state "Черновик" as draft
  state "На согласовании" as pending
  state "Возвращена" as returned
  state "Согласована" as approved
  state "Запланирована" as scheduled
  state "В отпуске" as onLeave
  state "Завершена" as closed
  state "Отклонена" as rejected
  state "Отменена" as cancelled
  [*] --> draft
  draft --> pending : сотрудник
  pending --> approved : руководитель
  pending --> rejected : руководитель
  pending --> returned : руководитель
  returned --> pending : сотрудник
  approved --> scheduled : служба кадров
  approved --> cancelled : сотрудник
  scheduled --> onLeave : наступает дата начала
  scheduled --> cancelled : сотрудник
  onLeave --> closed : наступает дата окончания
  classDef hold fill:#E8F0FB,stroke:#2E5A8A,color:#0F2A47,stroke-width:2px
  classDef wait fill:#FFFFFF,stroke:#607D8B,color:#263238
  classDef final fill:#ECEFF1,stroke:#37474F,color:#263238,stroke-dasharray:4 3
  class approved,scheduled,onLeave hold
  class draft,pending,returned wait
  class closed,rejected,cancelled final
```

Условные обозначения:
1. Закрашенный кружок — начало: заявку создаёт сотрудник.
2. Толстая синяя рамка — дни отпуска в резерве («Резерв дней» = да).
3. Тонкая серо-синяя рамка, белая заливка — дни не в резерве, состояние не итоговое.
4. Пунктирная тёмно-серая рамка — итоговое состояние: из него заявка не выходит.
5. Надпись на переходе — исполнитель; «наступает дата начала» и «наступает дата окончания» —
   условия.
