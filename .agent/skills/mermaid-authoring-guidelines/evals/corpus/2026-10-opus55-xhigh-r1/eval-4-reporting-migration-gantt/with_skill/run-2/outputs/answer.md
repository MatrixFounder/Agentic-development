**Figure 1.** Warehouse move schedule: the tasks of §2.1 by team, in working days from 2 November 2026. Each bar carries the task ID of the table in §2.1.

```mermaid
%%{init: {"look": "classic", "themeVariables": {"doneTaskBkgColor": "#C8E6C9", "doneTaskBorderColor": "#2E7D32", "activeTaskBkgColor": "#FFF3C4", "activeTaskBorderColor": "#F9A825", "taskBkgColor": "#FFFFFF", "taskBorderColor": "#9E9E9E", "critBkgColor": "#FFFFFF", "critBorderColor": "#C62828", "taskTextColor": "#212121", "taskTextDarkColor": "#212121"}, "gantt": {"barHeight": 16, "barGap": 4, "topPadding": 50, "fontSize": 12, "sectionFontSize": 12, "numberSectionStyles": 2, "useWidth": 900}, "themeCSS": ".grid .tick line { stroke-opacity: 0.25; } .activeText0.taskTextOutsideRight, .activeText1.taskTextOutsideRight, .activeText2.taskTextOutsideRight, .activeText3.taskTextOutsideRight, .activeCritText0.taskTextOutsideRight, .activeCritText1.taskTextOutsideRight, .activeCritText2.taskTextOutsideRight, .activeCritText3.taskTextOutsideRight, .doneText0.taskTextOutsideRight, .doneText1.taskTextOutsideRight, .doneText2.taskTextOutsideRight, .doneText3.taskTextOutsideRight, .doneCritText0.taskTextOutsideRight, .doneCritText1.taskTextOutsideRight, .doneCritText2.taskTextOutsideRight, .doneCritText3.taskTextOutsideRight, .activeText0.taskTextOutsideLeft, .activeText1.taskTextOutsideLeft, .activeText2.taskTextOutsideLeft, .activeText3.taskTextOutsideLeft, .activeCritText0.taskTextOutsideLeft, .activeCritText1.taskTextOutsideLeft, .activeCritText2.taskTextOutsideLeft, .activeCritText3.taskTextOutsideLeft, .doneText0.taskTextOutsideLeft, .doneText1.taskTextOutsideLeft, .doneText2.taskTextOutsideLeft, .doneText3.taskTextOutsideLeft, .doneCritText0.taskTextOutsideLeft, .doneCritText1.taskTextOutsideLeft, .doneCritText2.taskTextOutsideLeft, .doneCritText3.taskTextOutsideLeft { fill: #ffffff !important; mix-blend-mode: difference; }"}}%%
gantt
  accTitle: Warehouse move schedule
  accDescr: The tasks of section 2.1 by team, in working days from 2 November 2026. Each bar carries the task ID of the table in section 2.1.
  dateFormat YYYY-MM-DD
  axisFormat %d %b
  tickInterval 1week
  weekday monday
  excludes weekends
  todayMarker off
  section Platform
    P1 :crit, p1, 2026-11-02, 4d
    P2 :crit, p2, after p1, 3d
  section Data
    D1 :d1, after p2, 2d
    D2 :crit, d2, after p2, 6d
  section QA
    Q1 :crit, q1, after d1 d2, 2d
  section Release
    R1 :crit, r1, after q1, 1d
    R2 :crit, milestone, r2, after r1, 0d
```

- **Bar:** a task, from its first working day to the end of its last one.
- **Diamond:** R2, the switch of the dashboards when the write freeze ends.
- **Red border:** the critical path of §2.2. D1 has a grey border because it is off the critical path, with 4 working days of slack.
- **Shaded columns:** Saturdays and Sundays, which fall outside every duration.
- **Not drawn:** the 3-day rollback readiness after R2 and the decommissioning tracked in TASK-512.