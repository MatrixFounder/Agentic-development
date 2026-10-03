Диаграмма показывает состояния и переходы из разделов 2.3.1 и 2.3.2.

```mermaid
stateDiagram-v2
    state "Черновик" as Draft
    state "На согласовании" as Review
    state "Возвращена" as Returned
    state "Согласована" as Approved
    state "Запланирована" as Scheduled
    state "В отпуске" as OnLeave
    state "Завершена" as Completed
    state "Отклонена" as Rejected
    state "Отменена" as Cancelled

    [*] --> Draft : сотрудник создаёт
    Draft --> Review : сотрудник отправляет
    Review --> Approved : руководитель согласует
    Review --> Returned : руководитель возвращает
    Review --> Rejected : руководитель отклоняет
    Returned --> Review : сотрудник отправляет повторно
    Approved --> Scheduled : служба кадров, hr_schedule()
    Approved --> Cancelled : сотрудник отменяет
    Scheduled --> OnLeave : наступила дата начала
    Scheduled --> Cancelled : сотрудник отменяет не позднее чем за 2 дня до начала
    OnLeave --> Completed : наступила дата окончания
    Completed --> [*]
    Rejected --> [*]
    Cancelled --> [*]

    classDef reserved fill:#fff1c2,stroke:#9a6700,color:#1f2328
    class Approved,Scheduled,OnLeave reserved
```

Цветом выделены состояния с резервом дней. Итоговые состояния ведут в конечную точку. Напоминание и эскалация из раздела 2.3.3 не меняют состояние заявки, поэтому на диаграмме их нет.