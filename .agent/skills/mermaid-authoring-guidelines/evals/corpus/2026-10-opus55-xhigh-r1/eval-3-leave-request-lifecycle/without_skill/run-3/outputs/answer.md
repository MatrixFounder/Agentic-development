Диаграмма показывает переходы из 2.3.1. Итоговые состояния «Завершена», «Отклонена» и «Отменена» ведут в конечную точку. Уведомления и эскалации из 2.3.3 состояние не меняют, поэтому на диаграмме их нет.

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

    [*] --> Draft : Сотрудник создаёт
    Draft --> Review : Сотрудник отправляет
    Review --> Approved : Руководитель согласует
    Review --> Returned : Руководитель возвращает
    Review --> Rejected : Руководитель отклоняет
    Returned --> Review : Сотрудник исправляет и отправляет
    Approved --> Scheduled : Служба кадров, hr_schedule()
    Approved --> Cancelled : Сотрудник отменяет
    Scheduled --> OnLeave : Дата начала отпуска
    Scheduled --> Cancelled : Сотрудник отменяет, не позднее чем за 2 дня
    OnLeave --> Completed : Дата окончания отпуска

    Completed --> [*]
    Rejected --> [*]
    Cancelled --> [*]
```