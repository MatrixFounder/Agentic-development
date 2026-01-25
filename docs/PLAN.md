# Plan: Update TOC in READMEs

## Goal
Regenerate TOC for `README.md` and `README.ru.md` to include new sections.

## Proposed Changes

### README.md TOC
```markdown
- [Installation & Setup](#-installation--setup)
  - [1. Copy Framework Folders](#1-copy-framework-folders)
  - [2. Choose Your AI Assistant](#2-choose-your-ai-assistant)
  - [3. Installation Requirements (Python)](#3-installation-requirements-python)
- [System Overview](#-system-overview)
  - [Directory Structure](#directory-structure)
  - [Meta-System Prompt](#-meta-system-prompt-00_agent_developmentmd)
  - [The Agent Team (Roles)](#-the-agent-team-roles)
  - [The Product Team (Roles)](#-the-product-team-roles)
  - [Skills System](#-skills-system)
- [Workspace Workflows](#-workspace-workflows)
  - [Quick Start](#quick-start)
  - [Variants](#variants)
- [How to Start Development](#-how-to-start-development-step-by-step-plan)
  - [Phase 0: Product Discovery](#phase-0-product-discovery-optional)
  - [Stages 1-5](#stage-1-pre-flight-check)
- [Artifact Management](#-artifact-management)
- [What to do with .AGENTS.md files?](#-what-to-do-with-agentsmd-files)
- [How to prepare for future iterations?](#-how-to-prepare-for-future-iterations)
- [Reverse Engineering](#-reverse-engineering-if-documentation-is-outdated)
- [Starter Prompts](#-starter-prompt-templates)
- [Migration Guide](#-migration-from-older-versions)
- [Integration with Cursor IDE](#-integration-with-cursor-ide-agentic-mode)
```

### README.ru.md TOC
```markdown
- [Установка и Настройка](#-установка-и-настройка-installation--setup)
  - [1. Скопируйте папки фреймворка](#1-скопируйте-папки-фреймворка)
  - [2. Выберите вашего AI-ассистента](#2-выберите-вашего-ai-ассистента)
  - [3. Требования к установке (Python)](#3-требования-к-установке-python)
- [Обзор Системы](#-обзор-системы-system-overview)
  - [Структура Директорий](#структура-директорий)
  - [Мета-Системный Промпт](#-мета-системный-промпт-00_agent_developmentmd)
  - [Команда Агентов (Роли)](#-команда-агентов-роли)
  - [Продуктовая Команда (Роли)](#-продуктовая-команда-роли)
  - [Система Навыков](#-система-навыков-skills-system)
- [Workspace Workflows](#-workspace-workflows)
  - [Быстрый старт](#быстрый-старт)
  - [Варианты](#варианты-variants)
- [Как начать разработку](#-как-начать-разработку-пошаговый-план)
  - [Фаза 0: Product Discovery](#phase-0-product-discovery-опционально)
  - [Этапы 1-5](#этап-1-подготовка-к-началу-разработки)
- [Управление артефактами](#-управление-артефактами-artifact-management)
- [Что делать с файлами .AGENTS.md?](#-что-делать-с-файлами-agentsmd)
- [Подготовка к итерациям](#-как-подготовиться-к-следующим-доработкам)
- [Reverse Engineering](#-reverse-engineering-если-документация-устарела)
- [Шаблоны промптов](#-шаблоны-стартовых-промптов-starter-prompts)
- [Миграция со старых версий](#-миграция-со-старых-версий)
- [Интеграция с Cursor IDE](#-интеграция-с-cursor-ide-agentic-mode)
```

## Verification
- Manual link checking (headers are messy in GitHub Markdown, I will use simplified best-guess anchors and user can report if they break, or I can use a simpler flat list).
- *Correction*: I will use proper anchor generation rules (lowercase, replace spaces with hyphens, remove punctuation).

