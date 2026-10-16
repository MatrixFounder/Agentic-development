"""Checks that the tests of the skill's packages share (TASK 126 R3).

A package of `scripts/` holds one module per section of a former file. Its tests pin the imports of
each module, the names that each binds, and that each imports exactly the names its code reads.
These helpers read source with `ast` and `symtable`, so they run no code of a package.

A top-level name is one that a top-level `def`, `class` or assignment binds, each name of a tuple
target included and imported names excluded (TASK 124 §0).
"""
import ast
import builtins
import dis
import symtable
import types


def imports(path):
    """(line, level, module, names) of each import statement of *path*, at any depth."""
    found = []
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if isinstance(node, ast.ImportFrom):
            found.append((node.lineno, node.level, node.module, tuple(a.name for a in node.names)))
        elif isinstance(node, ast.Import):
            found.extend((node.lineno, 0, a.name, ()) for a in node.names)
    return found


def bound_at_top(path):
    """The names that a top-level `def`, `class` or assignment of *path* binds, each name of a
    tuple target included; an imported name is not among them."""
    names = set()
    for node in ast.parse(path.read_text(encoding="utf-8")).body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.add(node.name)
        elif isinstance(node, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
            stack = list(node.targets) if isinstance(node, ast.Assign) else [node.target]
            while stack:
                target = stack.pop()
                if isinstance(target, ast.Name):
                    names.add(target.id)
                elif isinstance(target, (ast.Tuple, ast.List)):
                    stack.extend(target.elts)
                elif isinstance(target, ast.Starred):
                    stack.append(target.value)
    return names


#: Names that a module reads with no import or definition of its own. Python 3.14's `symtable`
#: also reports `__conditional_annotations__`.
MODULE_ATTRS = {"__name__", "__file__", "__doc__", "__spec__", "__package__", "__loader__",
                "__builtins__", "__annotations__", "__conditional_annotations__"}
#: The opcodes that load a global name, by their names on Python 3.11 to 3.14.
_GLOBAL_LOADS = {"LOAD_GLOBAL", "LOAD_NAME", "LOAD_FROM_DICT_OR_GLOBALS"}


def _loaded(code):
    """The global names that *code* and the code objects in it load."""
    names = {ins.argval for ins in dis.get_instructions(code) if ins.opname in _GLOBAL_LOADS}
    for const in code.co_consts:
        if isinstance(const, types.CodeType):
            names |= _loaded(const)
    return names


def reads(source):
    """The global names that *source* reads, annotations included, builtins and `MODULE_ATTRS`
    aside. `symtable` gives the reads of each scope. At the top level a name that the module
    assigns is no read, an imported one aside: since Python 3.12 a comprehension there binds its
    variable in the module's own table (PEP 709). The same inlining hides a read of an imported
    name inside such a comprehension from `symtable`, so the names that the compiled code loads
    are added."""
    found = set()

    def walk(table, top):
        for sym in table.get_symbols():
            if not sym.is_referenced():
                continue
            if top:
                read = sym.is_imported() or not sym.is_assigned()
            else:
                read = sym.is_global()
            if read:
                found.add(sym.get_name())
        for child in table.get_children():
            walk(child, False)

    walk(symtable.symtable(source, "<module>", "exec"), True)
    found |= _loaded(compile(source, "<module>", "exec"))
    for node in ast.walk(ast.parse(source)):
        notes = []
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            args = node.args
            notes = [node.returns] + [a.annotation for a in args.posonlyargs + args.args
                                      + args.kwonlyargs + [args.vararg, args.kwarg] if a]
        elif isinstance(node, ast.AnnAssign):
            notes = [node.annotation]
        for note in filter(None, notes):
            found.update(n.id for n in ast.walk(note) if isinstance(n, ast.Name))
    return found - set(dir(builtins)) - MODULE_ATTRS


def imported(tree):
    """The names that the top-level imports of *tree* bind, `from __future__` aside."""
    names = set()
    for node in tree.body:
        if isinstance(node, ast.Import):
            names.update(a.asname or a.name.split(".")[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module != "__future__":
            names.update(a.asname or a.name for a in node.names)
    return names


def import_mismatch(path):
    """(the imported names that the code of *path* never reads, the names that it reads but neither
    defines nor imports), each sorted. Both are empty when it imports exactly what it reads."""
    source = path.read_text(encoding="utf-8")
    read, bound = reads(source), imported(ast.parse(source))
    return sorted(bound - read), sorted(read - bound - bound_at_top(path))


def docstring_only(path):
    """True when *path* holds one statement, its docstring."""
    body = ast.parse(path.read_text(encoding="utf-8")).body
    return (len(body) == 1 and isinstance(body[0], ast.Expr)
            and isinstance(getattr(body[0].value, "value", None), str))


def instrument_files(path):
    """The value of `INSTRUMENT_FILES` in *path*, read by AST."""
    for node in ast.parse(path.read_text(encoding="utf-8")).body:
        if (isinstance(node, ast.Assign) and len(node.targets) == 1
                and getattr(node.targets[0], "id", "") == "INSTRUMENT_FILES"):
            return ast.literal_eval(node.value)
    raise AssertionError(f"{path.name} binds no INSTRUMENT_FILES")
