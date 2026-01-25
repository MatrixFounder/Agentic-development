# Task 017: Подход к сохранениею протоколов тестирования

## Проблема
Сейчас протоколы тестирования сохраняются в `docs/test_reports*` и нумеруются по порядку также как текущий task (со Slug), но они не разложены по папкам

## Задача
Необходимо сохранять протоколы тестирования в `tests/tests-{{Task ID}}/test-{{task-id}}-{{subtask/slug}}.md`.

## Пример
tests/
  tests-017/
    test-017-001-task-017.md
    test-017-002-task-017.md
    test-017-003-task-017.md

## План
1. Создать папку `tests/tests-{{Task ID}}`
2. Создать файл `tests/tests-{{Task ID}}/test-{{task-id}}-{{subtask/slug}}.md`
3. Скопировать содержимое `docs/test_reports/task-{{task-id}}-{{slug}}.md` в `tests/tests-{{Task ID}}/test-{{task-id}}-{{subtask/slug}}.md`
4. Удалить `docs/test_reports/task-{{task-id}}-{{slug}}.md`
5. Обновить `docs/WORKFLOWS.md`

Обновить абсолютно все инструкции, которые ссылаются на файлы с тестированием и прописать туда правила сохранения протоколов тестирования.

## Критерии приемки
1. Все инструкции обновлены
2. Все протоколы тестирования сохранены в `tests/tests-{{Task ID}}/test-{{task-id}}-{{subtask/slug}}.md`
3. Все `docs/test_reports/task-{{task-id}}-{{slug}}.md` удалены
