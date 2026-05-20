# Technical Specification: Framework Installer Script

### 0. Meta Information
- **Task ID:** 063
- **Slug:** `framework-installer`
- **Mode:** VDD (Verification-Driven Development)
- **Type:** New tooling — installer for the agentic-development framework
- **Source Plan:** `/Users/sergey/.claude/plans/snug-foraging-wind.md` (approved)
- **Already created:** [install.sh](../install.sh) + [System/scripts/install.py](../System/scripts/install.py) (argparse skeletons only — no logic yet)

## 1. General Description

В репозитории `agentic-development` нет вспомогательного скрипта для развёртывания фреймворка в чистом пользовательском проекте. Сейчас разработчики копируют структуру вручную (см. [Universal-skills](/Users/sergey/dev-projects/Universal-skills) — per-item симлинки на соседний клон). Нужен идемпотентный CLI-установщик, который раскладывает в target-проекте только нужные артефакты для выбранной системы агентов и защищает пользовательские файлы от перезаписи.

**Ключевая архитектурная идея**: все файлы фреймворка живут в **`.agentic-development/`** внутри корня target-проекта (либо симлинк на соседний клон, либо полная копия). Все vendor-симлинки указывают **внутрь** этой папки через стабильные относительные пути (`../../.agentic-development/...`). Это даёт универсальность (проект не привязан к расположению framework в FS), воспроизводимость, простоту `.gitignore` и чистый `switch`/`uninstall`.

**Supported vendors:** `claude`, `antigravity`, `codex`, `cursor`, `gemini-cli` — декларативно в `vendors.yaml`, новый вендор добавляется без правки Python.

## Requirements Traceability Matrix (RTM)

| ID    | Requirement                                                  | MVP? | Sub-features |
|-------|--------------------------------------------------------------|------|--------------|
| FR-1  | CLI с подкомандами install/switch/update/uninstall/doctor    | ✅ | argparse skeleton, bash wrapper, exit codes, --dry-run, --verbose/--quiet, --json (doctor) |
| FR-2  | Vendor profile system через `vendors.yaml`                   | ✅ | 5 vendor entries (claude/antigravity/codex/cursor/gemini-cli), per-action schema validator, defaults block, optional/if_missing flags |
| FR-3  | `.agentic-development/` root management                      | ✅ | symlink mode (default, relative paths), copy mode (`shutil.copytree(symlinks=False)`), foreign-content detection, ignore-list для копирования (.git, .venv, __pycache__) |
| FR-4  | Per-item symlinks с relative paths                           | ✅ | `link_per_item` action, `link_folder` action, relpath computation, reachability check (`os.stat(follow_symlinks=True)`) после создания, cross-FS downgrade в copy |
| FR-5  | Managed-block engine (общий для gitignore и bootstrap)       | ✅ | SHA-256 hash блока в state, abort-on-mismatch с unified-diff, `--force` сохраняет старое в `.agent/backups/`, atomic write через temp+os.replace |
| FR-6  | Vendor-aware bootstrap (at_import + marker_block)            | ✅ | `at_import` стратегия (Claude): CLAUDE.md скелет, CLAUDE.local.md мост, CLAUDE.agentic.md симлинк; `marker_block` стратегия (Antigravity/Codex/Gemini-CLI): managed-блок в AGENTS.md/GEMINI.md; `none` (Cursor) |
| FR-7  | `.gitignore` block с hash защитой                            | ✅ | marker `# >>> agentic-development framework >>>` / `# <<<`, секции framework/state/vendor/bridge, `!`-сканер для project-local скиллов, filter dotfiles, без рекурсии |
| FR-8  | Pre-flight conflict prevention                                | ✅ | per-component classification (safe/our/hard-conflict/soft-conflict), `--force` для overwritable hard-конфликтов (кроме CLAUDE.md/AGENTS.md/GEMINI.md), `--force-system-link` для System/, `--skip` flag, финальный отчёт |
| FR-9  | State management (.agentic-installer-state.json в корне)     | ✅ | в корне target (не внутри `.agent/`), JSON структура с vendor/mode/framework_path/installed_at/hashes/managed_paths/skipped_components, heuristic-mode при потере state |
| FR-10 | `switch --vendor X` с backup                                 | ✅ | snapshot OLD в `.agent/backups/<UTC-timestamp>/`, retention `--max-backups N` default 5, удаление bridge-файлов OLD (не project files), вырезание managed-блока для marker_block-стратегии, `.agentic-development/` не пересоздаётся |
| FR-11 | `uninstall` с опцией `--purge`                               | ✅ | удаление managed_paths через state; `--purge` дополнительно удаляет `.agentic-development/`; heuristic mode при отсутствии state; `--all-vendors` sweep; CLAUDE.md/AGENTS.md/GEMINI.md сохраняются |
| FR-12 | `doctor` read-only verifier                                  | ✅ | проверка симлинков (resolve внутри `.agentic-development/`), hash блоков, состояние state, codex git-root check, AGENTS.md not-overwrite check, `--json` output |
| FR-13 | Platform fallback                                            | ✅ | Windows symlink probe через `tempfile.TemporaryDirectory()`, auto-fallback в copy mode, long-path detection, BASH_VERSION guard в wrapper |
| FR-14 | Codex git-root requirement                                   | ✅ | `git_root_required: true` в профиле, проверка наличия `target/.git/`, warning при mismatch, `--force` override |
| FR-15 | Per-vendor bootstrap-file mapping                            | ✅ | каждый вендор объявляет свой `bootstrap_file` (Claude→`CLAUDE.md`, Antigravity→`GEMINI.md`, Codex/Cursor→`AGENTS.md`); опциональный `bootstrap_aliases` поддерживает несколько bootstrap-файлов, но ни один из поставляемых вендоров его не использует |
| NFR-1 | Idempotency                                                  | ✅ | повторный `install` → "0 created, N already linked", корректный симлинк → no-op, hash mismatch detection |
| NFR-2 | No silent clobber                                            | ✅ | abort + diff на ручную правку, --force с backup, never-overwrite list (CLAUDE.md/AGENTS.md/GEMINI.md) |
| NFR-3 | Stub-First implementation                                    | ✅ | argparse skeleton первым (готово), затем модули по слоям (vendors → state → framework_root → symlinks → managed_block → bootstrap → gitignore → install) |
| NFR-4 | Тестируемость                                                | ✅ | pytest на `tmp_path`, integration suite по verification-рецепту из плана, unit tests на каждый модуль installer/ |
| NFR-5 | Минимальные зависимости                                      | ✅ | stdlib + PyYAML; bash wrapper проверяет наличие, печатает hint |

**MVP boundary**: всё FR-1..FR-15 + NFR-1..NFR-5 — это core installer. Post-MVP: миграция на plural `.agents/`, `.cursor/rules/*.mdc` трансформер, git-clone/submodule population.

## 2. Epics & Issues (Chainlink Decomposition)

### Epic E1 — CLI Foundation & Vendor Profile System

> **Goal**: Установщик читает аргументы, грузит и валидирует профили вендоров, отказывается работать на невалидных конфигах ДО любых операций с файловой системой.

#### Issue I1.1 — `install.sh` bash wrapper
**Status:** ✅ Stub created (uncommitted).
**Acceptance:**
- ✅ Файл [install.sh](../install.sh) исполняемый (`chmod +x`).
- ✅ Shebang `#!/usr/bin/env bash` + `set -euo pipefail`.
- ✅ Guard `[ -z "${BASH_VERSION:-}" ]` отказывает с понятной ошибкой если запущен под `sh`/`dash`.
- ✅ Проверка наличия `python3` (≥3.9) и PyYAML, hint при отсутствии.
- ✅ `exec python3 "$SCRIPT_DIR/System/scripts/install.py" --installer-script-dir "$SCRIPT_DIR" "$@"`.

#### Issue I1.2 — `install.py` argparse skeleton
**Status:** ✅ Stub created (uncommitted).
**Acceptance:**
- ✅ Подкоманды: `install`, `switch`, `update`, `uninstall`, `doctor`.
- ✅ Каждая подкоманда имеет соответствующие флаги из плана (см. CLI section).
- ✅ `--installer-script-dir` опция (SUPPRESS в help) — для bash wrapper.
- ✅ Dispatch в `installer.cli.main(args)` который возвращает exit code.
- ✅ Exit code ≥ 2 на ошибку валидации, 1 на runtime error, 0 на успех.

#### Issue I1.3 — `vendors.yaml` со всеми 5 профилями
**Acceptance:**
- ✅ Файл `System/scripts/vendors.yaml` создан с ключом `version: 1`.
- ✅ Блок `defaults` с `agent_components` и `root_components` (см. план).
- ✅ Профили: `claude`, `antigravity`, `codex`, `cursor`, `gemini-cli` — точно как в плане (bootstrap_strategy, bootstrap_file, vendor_dir, components).
- ✅ Codex имеет `git_root_required: true`.
- ✅ Antigravity: `bootstrap_strategy: marker_block`, `bootstrap_file: GEMINI.md` (только GEMINI.md — без AGENTS.md).
- ✅ Cursor: `bootstrap_strategy: marker_block`, `bootstrap_file: AGENTS.md` (Cursor читает стандарт AGENTS.md).

#### Issue I1.4 — `installer/vendors.py` с per-action validator
**Acceptance:**
- ✅ `load_vendors(path)` парсит YAML, возвращает typed structure.
- ✅ `validate_profile(name, profile, framework_root)` проверяет:
  - Каждый component-action имеет требуемые поля (`source` обязателен для link_*/copy; запрещён для mkdir; `path` всегда обязателен).
  - `source` резолвится в существующий путь внутри framework_root (с учётом `optional: true`).
  - `bootstrap_strategy` ∈ {`at_import`, `marker_block`, `none`}; для marker_block обязателен `bootstrap_source`.
- ✅ Валидатор вызывается ДО любых fs-операций (фаза 3 алгоритма install).
- ✅ Невалидный профиль → `InstallerError` с указанием конкретного поля и его расположения.

#### Issue I1.5 — `installer/errors.py` + exit codes
**Acceptance:**
- ✅ Класс `InstallerError(Exception)` с полем `exit_code` (default 1).
- ✅ Подклассы: `ConfigurationError` (exit 2), `ConflictError` (exit 3), `IntegrityError` (exit 4).
- ✅ `installer/cli.py main()` ловит и форматирует.

---

### Epic E2 — `.agentic-development/` Root Management

> **Goal**: Корневая папка `.agentic-development/` корректно создаётся симлинком или копией, не перезаписывает foreign content без `--force`, исключает мусор при копировании.

#### Issue I2.1 — `installer/framework_root.py` (symlink mode)
**Acceptance:**
- ✅ `ensure_agentic_dev_symlink(target, framework_path, force)`:
  - Не существует → создать relative symlink через `os.path.relpath`.
  - Существует и корректен (симлинк, который резолвится в framework_path) → no-op + log.
  - Существует и foreign → требовать `force=True`, иначе `ConflictError`.
- ✅ Если framework и target не на одной FS hierarchy (relpath даёт абсолютный путь длиннее) — использовать абсолютный.
- ✅ Reachability check после создания.

#### Issue I2.2 — `installer/framework_root.py` (copy mode)
**Acceptance:**
- ✅ `ensure_agentic_dev_copy(target, framework_path, force)`:
  - `shutil.copytree(framework, target/.agentic-development, symlinks=False, ignore=_ignore_func)`.
  - `_ignore_func` пропускает: `.git`, `.venv`, `__pycache__`, `.pytest_cache`, `.DS_Store`, `*.pyc`, `node_modules`, `.hypothesis`, `.ruff_cache`.
- ✅ Foreign content → backup + force semantics.

#### Issue I2.3 — Pre-flight target guards
**Acceptance:**
- ✅ `Path(target).resolve() == Path(framework).resolve()` → `ConflictError`.
- ✅ `Path(target).resolve().is_relative_to(Path(framework).resolve())` → `ConflictError`.
- ✅ Сообщение об ошибке указывает обе пути.

---

### Epic E3 — Symlink Engine

> **Goal**: Per-item и folder-level симлинки создаются с правильными относительными путями, идемпотентно, с reachability check.

#### Issue I3.1 — `installer/symlinks.py` link_one
**Acceptance:**
- ✅ `link_one(link_path, source_path)`:
  - Source существует → создать relative symlink через `os.path.relpath(source, start=link_path.parent)`.
  - Link уже корректный → no-op, log как "already-linked".
  - Link есть но указывает в другое место → `ConflictError` (если не наш — within .agentic-development/), иначе atomic replace через `os.replace`.
- ✅ После создания — `os.stat(follow_symlinks=True)`; на провал — return `ReachabilityError`.

#### Issue I3.2 — `installer/symlinks.py` link_per_item
**Acceptance:**
- ✅ `link_per_item(target_dir, source_dir)`:
  - Итерация `os.scandir(source_dir)`.
  - Для каждой записи (включая папки и файлы, исключая dotfiles) → `link_one`.
  - Создаёт `target_dir` если отсутствует.
- ✅ Возвращает счётчики (created/already_linked/skipped/conflicts).

#### Issue I3.3 — `link_folder` action
**Acceptance:**
- ✅ `link_folder(target_path, source_dir)`: одна симлинк-запись через `link_one`.
- ✅ Идемпотентность через тот же предикат.

#### Issue I3.4 — `mkdir` action
**Acceptance:**
- ✅ `make_dir(target_path)`: создаёт пустую папку, кладёт `.gitkeep`.
- ✅ Идемпотентно (no-op если уже есть).

---

### Epic E4 — Managed-Block Engine (Shared by Gitignore and Bootstrap)

> **Goal**: Общий движок для блоков, ограниченных маркерами, с защитой от silent clobber через SHA-256 hash.

#### Issue I4.1 — `installer/managed_block.py` базовая логика
**Acceptance:**
- ✅ `inject_block(file_path, content, marker_pair, state_hash=None, force=False)`:
  - Файла нет → создать с блоком.
  - Маркер открытия найден → вычислить SHA-256 текущего блока.
    - hash совпадает с `state_hash` → atomic rewrite через temp + `os.replace`.
    - hash не совпадает → return `HashMismatchError` с unified-diff (state ↔ current); `--force` сохраняет старое в backup и переписывает.
  - Маркера нет → append в конец файла.
- ✅ Возвращает новый hash блока.

#### Issue I4.2 — Маркер-форматы
**Acceptance:**
- ✅ Для `.gitignore` маркер: `# >>> agentic-development framework >>>` ... `# <<< end agentic-development framework <<<`.
- ✅ Для markdown файлов (AGENTS.md/GEMINI.md): `<!-- >>> agentic-development >>> -->` ... `<!-- <<< agentic-development <<< -->`.
- ✅ Marker pair передаётся параметром.

#### Issue I4.3 — Atomic write + backup на --force
**Acceptance:**
- ✅ Запись через `tempfile.NamedTemporaryFile` в том же dir → `os.replace`.
- ✅ На --force старая версия сохраняется в `.agent/backups/<ts>/<filename>.user-edits.txt` ДО перезаписи.

---

### Epic E5 — Vendor-Aware Bootstrap

> **Goal**: Bootstrap-файлы корректно создаются для каждого вендора по двум разным стратегиям (`@`-import для Claude, marker-block для остальных).

#### Issue I5.1 — `installer/bootstrap.py` стратегия `at_import` (Claude)
**Acceptance:**
- ✅ `CLAUDE.md` — создать скелет только если отсутствует. **Никогда не перезаписываем** (don't-overwrite list).
- ✅ `CLAUDE.local.md` — создать с одной строкой `@CLAUDE.agentic.md` если нет. Если файл есть и не содержит import — append секции под маркером `<!-- agentic-development -->`.
- ✅ `CLAUDE.agentic.md` — relative symlink на `.agentic-development/CLAUDE.md` (`.agentic-development/CLAUDE.md` — один уровень вниз).

#### Issue I5.2 — `installer/bootstrap.py` стратегия `marker_block` (Antigravity/Codex/Gemini-CLI)
**Acceptance:**
- ✅ Для `bootstrap_file` и каждого `bootstrap_aliases`:
  - Файла нет → создать скелет (`# Project\n\n<managed-block>\n`).
  - Файл есть → инжектировать managed-блок через `managed_block.inject_block`.
- ✅ Источник контента блока — `<framework>/<bootstrap_source>` (читается при каждом install для свежести).
- ✅ Hash блока сохраняется в state под ключом `bootstrap_blocks_hash[filename]`.
- ✅ `*.local.md` / `*.agentic.md` НЕ создаются для marker_block стратегии.

#### Issue I5.3 — Стратегия `none` (Cursor)
**Acceptance:**
- ✅ Пропускает все bootstrap-действия.

#### Issue I5.4 — Don't-overwrite list enforcement
**Acceptance:**
- ✅ Функция `is_protected(filename)` возвращает True для `CLAUDE.md`, `AGENTS.md`, `GEMINI.md`.
- ✅ Никакая операция (даже `--force`) не перезаписывает эти файлы; только managed-блок внутри них.

---

### Epic E6 — Conflict Prevention

> **Goal**: Pre-flight scan классифицирует все целевые пути по политике из плана и не трогает foreign content.

#### Issue I6.1 — Conflict classifier
**Acceptance:**
- ✅ Функция `classify_path(target_path, framework_root, expected_action)`:
  - Не существует → `safe`.
  - Симлинк, резолвится внутрь `.agentic-development/` → `our`.
  - Файл с managed-блоком (hash сохранён в state) → `our`.
  - В hard-conflict списке (CLAUDE.md, AGENTS.md, GEMINI.md, */settings.json, System/, /.codex/config.toml) → `hard_conflict`.
  - Per-item путь под `.claude/skills/`, `.agent/skills/` и т.п. → `soft_conflict`.
- ✅ Hard-conflict компоненты по умолчанию **skip + warning**, добавляются в `state.skipped_components`.
- ✅ Soft-conflict items skip → попадают в `!`-exceptions.

#### Issue I6.2 — `System/` special case
**Acceptance:**
- ✅ Default: если `System/` foreign — skip с понятным warning сообщением (см. план).
- ✅ С `--force-system-link`: старая папка → backup, ставится симлинк.
- ✅ `state.skipped_components` содержит `"System"` если пропущен.

#### Issue I6.3 — `--dry-run` остановка на pre-flight
**Acceptance:**
- ✅ `--dry-run` останавливается после classification, печатает финальный отчёт (N to install, M skipped, K need --force).
- ✅ Никаких fs-операций.

#### Issue I6.4 — `--skip COMPONENT,...` flag
**Acceptance:**
- ✅ Пользователь может явно исключить любой component-path из vendors.yaml.
- ✅ Skipped компоненты попадают в `state.skipped_components` с reason `"--skip flag"`.

---

### Epic E7 — State Management & Backup

> **Goal**: State-файл живёт в корне target (не внутри `.agent/`), хранит hashes для anti-clobber защиты, переживает switch/uninstall.

#### Issue I7.1 — `installer/state.py`
**Acceptance:**
- ✅ Файл `<target>/.agentic-installer-state.json`.
- ✅ Структура: `{version, vendor, mode, framework_path, agentic_development_is_symlink, installed_at, gitignore_block_hash, bootstrap_blocks_hash, managed_paths, skipped_components}`.
- ✅ Atomic write через temp + `os.replace`.
- ✅ `load_state()` возвращает `None` при отсутствии, не raise.

#### Issue I7.2 — Heuristic mode при отсутствии state
**Acceptance:**
- ✅ `install` без state → warning, создаёт state из текущего FS.
- ✅ `switch` без state → требует `--force` + heuristic (восстановление из vendors.yaml × всех известных вендоров).
- ✅ `uninstall` без state → heuristic + опция `--all-vendors`.

#### Issue I7.3 — `installer/backup.py` с retention
**Acceptance:**
- ✅ `create_snapshot(paths, target, label)` → `target/.agent/backups/<UTC-ts>-<label>/`.
- ✅ `apply_retention(target, max_backups=5)` удаляет старшие за пределами лимита (lexicographic sort по timestamp).
- ✅ Если `.agentic-development/` симлинк (read-only) — backup всегда в `target/.agent/backups/`.

---

### Epic E8 — Subcommands `switch`, `uninstall`, `doctor`

> **Goal**: Switch чистит OLD vendor без удаления project-owned файлов; uninstall поддерживает heuristic mode; doctor показывает состояние.

#### Issue I8.1 — `switch` implementation
**Acceptance:**
- ✅ Читает state, резолвит OLD vendor.
- ✅ Snapshot OLD-артефактов перед удалением.
- ✅ Удаление OLD: `vendor_dir`, bridge-файлы (`*.local.md`, `*.agentic.md` для at_import), managed-блок в bootstrap-файлах (для marker_block).
- ✅ `CLAUDE.md`/`AGENTS.md`/`GEMINI.md` сохраняются (don't-overwrite).
- ✅ `.agentic-development/` **не пересоздаётся** — inode/symlink-target остаётся прежним.
- ✅ `.agent/sessions/` сохраняется.
- ✅ Без state → требует `--force` + heuristic.

#### Issue I8.2 — `uninstall` implementation
**Acceptance:**
- ✅ Удаляет точно `state.managed_paths` если state есть.
- ✅ Heuristic mode при отсутствии state.
- ✅ `--purge` дополнительно удаляет `.agentic-development/`.
- ✅ `--all-vendors` heuristic-чистка по всем известным профилям.
- ✅ Don't-overwrite list файлов остаётся; managed-блок вырезается.
- ✅ State-файл удаляется в конце.
- ✅ `.gitignore` блок вырезается.

#### Issue I8.3 — `update` implementation
**Acceptance:**
- ✅ Пересобирает per-item симлинки (новые items framework добавляются).
- ✅ `--prune` удаляет симлинки чьи источники исчезли в framework.
- ✅ Не трогает settings.json, bootstrap-файлы, state vendor.

#### Issue I8.4 — `doctor` implementation
**Acceptance:**
- ✅ Read-only. Проверяет:
  - Каждый симлинк из `state.managed_paths` существует и резолвится в `.agentic-development/`.
  - Hashes в файлах совпадают с state (gitignore + bootstrap blocks).
  - State-файл валидный JSON, схема соответствует.
  - Для codex: `target/.git/` существует если `git_root_required: true`.
  - Don't-overwrite файлы (CLAUDE.md/AGENTS.md/GEMINI.md) существуют если требуются профилем.
- ✅ `--json` flag → структурированный отчёт `{ok: bool, errors: [], warnings: []}`.
- ✅ Exit 0 если ok, 1 если errors.

---

### Epic E9 — `.gitignore` Patch

> **Goal**: `.gitignore` всегда содержит правильный блок с hash-защитой и project-local exceptions.

#### Issue I9.1 — `installer/gitignore.py`
**Acceptance:**
- ✅ `update_gitignore(target, vendor_profile, state)`:
  - Использует `managed_block.inject_block` для вставки блока.
  - Маркеры `# >>> agentic-development framework >>>` / `# <<< end ... <<<`.
  - Содержание блока: framework dirs, state file, bridge files, vendor-specific paths.
- ✅ Hash сохраняется в `state.gitignore_block_hash`.
- ✅ `--no-gitignore` пропускает целиком.

#### Issue I9.2 — `!`-exception scanner
**Acceptance:**
- ✅ Сканер обходит `.agent/skills/`, `.agent/workflows/`, `.agent/agents/`, `.claude/skills/`, `.claude/commands/`, `.claude/agents/` (только верхний уровень).
- ✅ Предикат «project-local»: `is_symlink() is False` OR `Path(os.readlink(p)).parts[0] != '.agentic-development'`.
- ✅ Filter: dotfiles (`.DS_Store`, `.git*`).
- ✅ Broken framework symlinks → warning, НЕ добавляем в exceptions.
- ✅ Exceptions добавляются как `!/path/to/item` в конец блока.

---

### Epic E10 — Tests & Verification

> **Goal**: Pytest suite + integration tests покрывают все verification scenarios из плана; CI-friendly.

#### Issue I10.1 — Unit tests на каждый модуль `installer/`
**Acceptance:**
- ✅ `tests/installer/test_vendors.py` — schema validator (valid/invalid profiles).
- ✅ `tests/installer/test_symlinks.py` — link_one/per_item/folder, relpath calculation, reachability.
- ✅ `tests/installer/test_managed_block.py` — inject/update/hash mismatch.
- ✅ `tests/installer/test_bootstrap.py` — обе стратегии.
- ✅ `tests/installer/test_gitignore.py` — exceptions scanner, marker block.
- ✅ `tests/installer/test_state.py` — load/save/heuristic.
- ✅ `tests/installer/test_framework_root.py` — symlink/copy modes.
- ✅ Все используют `tmp_path` fixture, без mutation реальной FS вне tmp.

#### Issue I10.2 — Integration tests (verification recipe)
**Acceptance:**
- ✅ `tests/installer/test_e2e.py` запускает scenarios:
  - fresh install (symlink + copy modes) + проверки путей и hashes
  - install поверх непустого проекта (conflict prevention) — все don't-overwrite файлы сохраняются
  - --force-system-link
  - idempotency (re-install не создаёт новых)
  - switch claude→antigravity (.agentic-development inode unchanged, AGENTS.md created, CLAUDE.md preserved)
  - switch antigravity→codex (AGENTS.md preserved, .agents/skills symlink created)
  - copy mode (no symlinks outside target, but per-item links inside remain)
  - anti-clobber (.gitignore manual edit → abort with diff → --force restores)
  - uninstall без --purge (.agentic-development/ остаётся)
  - uninstall --purge
- ✅ Все тесты используют tmp_path и временный clone framework.

#### Issue I10.3 — Smoke test для bash wrapper
**Acceptance:**
- ✅ `tests/installer/test_wrapper.sh`: запускается под bash, sh, zsh.
- ✅ Под bash проходит; под sh — корректная ошибка `bash required`.
- ✅ Hint при отсутствии PyYAML.

## 3. Non-functional Requirements

- **Performance:** install в режиме symlink на typical project с 50+ skills должен занимать <2 секунд. Copy mode — <10 секунд (LIMITED by `shutil.copytree`).
- **Security:** Никакие пользовательские файлы не перезаписываются; symlinks проверяются на reachability перед фиксацией; backup перед любой destructive операцией.
- **Compatibility:** Python ≥3.9 (для `Path.is_relative_to`); PyYAML. macOS/Linux first-class; Windows через `--mode copy` fallback.
- **Idempotency:** Любая повторная команда без изменений в FS — no-op (0 changes, 0 errors).
- **No silent clobber:** Любое расхождение с state требует явный `--force` + сохранение в backup.

## 4. Constraints and Assumptions

- **Constraint:** Установщик не клонирует framework через git и не работает с submodule — только symlink или copy. Пользователь, желающий git-based управление, сам делает `git clone ... .agentic-development` и затем `install --from .agentic-development` (installer определит корректность).
- **Constraint:** `.agentic-development/` всегда gitignored — никаких опций commit.
- **Constraint:** Только pyyaml как внешняя зависимость; всё остальное stdlib.
- **Assumption:** Target проект имеет git-инициализацию (требуется для codex; warning для остальных).
- **Assumption:** На Windows пользователь либо имеет developer mode (symlinks), либо использует `--mode copy`.
- **Constraint:** `System/` имя — high-risk коллизия; решение через `--force-system-link` opt-in (не default).

## 5. Open Questions

- **Antigravity subagents formats**: `.claude/agents/*.md` используется как источник для `.agent/agents/`. Возможно subagent frontmatter отличается между Claude Code и Antigravity — уточнить при имплементации I5.2.
- **Codex `AGENTS.override.md`**: installer не создаёт этот файл — это пользовательский override. Документируем в выводе `install` (hint), но не trigger conflict.
- **`.codex/config.toml`**: installer создаёт только пустую папку; полный template config.toml — отдельная задача после MVP, если будет request.
- **Cursor `.cursor/rules/*.mdc`**: отдельный концепт от skills, не поддерживается installer'ом сейчас. Возможен MD→MDC трансформер из `.agent/rules/` — отдельная задача после MVP.
- **`System/` rename во framework**: чтобы навсегда устранить high-risk коллизию, можно переименовать в `Agentic/` или вложить в `.agentic-development/` без top-level симлинка. Требует синхронной правки workflows + CLAUDE.md. Отдельная задача после MVP installer'а.
