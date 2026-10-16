"""The modules of `lint_mermaid.py`, one per section of the file before TASK 126.

Callers import `lint_mermaid`, which imports these modules in order and binds every
top-level name of them. Each module registers its rules into `RULES` as it runs, so a
module imported alone sees only the rules of the modules imported so far.
"""
