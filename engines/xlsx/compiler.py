"""Turn a short expression into an Excel formula. No Python eval."""

from __future__ import annotations

import ast

from office_skill.plan import PlanError

_BIN = {
    ast.Add: "+",
    ast.Sub: "-",
    ast.Mult: "*",
    ast.Div: "/",
    ast.Pow: "^",
}
_CMP = {
    ast.Eq: "=",
    ast.NotEq: "<>",
    ast.Gt: ">",
    ast.Lt: "<",
    ast.GtE: ">=",
    ast.LtE: "<=",
}
_FUNCS = {
    "MAX": "MAX",
    "MIN": "MIN",
    "ROUND": "ROUND",
    "ROUNDUP": "ROUNDUP",
    "ABS": "ABS",
    "IF": "IF",
}


def _number(value: float | int) -> str:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise PlanError(f"Not a number: {value!r}")
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return repr(value) if isinstance(value, float) else str(value)


def compile_expr(
    expr: str,
    *,
    col_index: int,
    row_cells: dict[str, list[str]],
    assumptions: dict[str, str],
    prev_base: dict[str, str],
) -> str:
    try:
        tree = ast.parse(expr, mode="eval")
    except SyntaxError as exc:
        raise PlanError(f"Cannot parse formula {expr!r}: {exc}") from exc

    def walk(node: ast.AST) -> str:
        if isinstance(node, ast.Expression):
            return walk(node.body)
        if isinstance(node, ast.Constant):
            return _number(node.value)
        if isinstance(node, ast.Name):
            if node.id == "year_index":
                return str(col_index)
            if node.id in row_cells:
                return row_cells[node.id][col_index]
            if node.id in assumptions:
                return assumptions[node.id]
            raise PlanError(f"Unknown name {node.id!r} in {expr!r}.")
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
            return f"(-{walk(node.operand)})"
        if isinstance(node, ast.BinOp) and type(node.op) in _BIN:
            return f"({walk(node.left)}{_BIN[type(node.op)]}{walk(node.right)})"
        if isinstance(node, ast.Compare) and len(node.ops) == 1 and type(node.ops[0]) in _CMP:
            return f"({walk(node.left)}{_CMP[type(node.ops[0])]}{walk(node.comparators[0])})"
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            name = node.func.id.upper()
            if node.keywords:
                raise PlanError("Formula keywords are not allowed.")
            if name == "PREV":
                if len(node.args) != 1 or not isinstance(node.args[0], ast.Name):
                    raise PlanError("prev() takes one row name.")
                target = node.args[0].id
                if target not in row_cells:
                    raise PlanError(f"prev() of unknown row {target}.")
                if col_index == 0:
                    if target not in prev_base:
                        raise PlanError(f"Row {target} needs prev_base for the first year.")
                    return prev_base[target]
                return row_cells[target][col_index - 1]
            if name not in _FUNCS:
                raise PlanError(f"Function {name} is not in the LibreOffice-safe set.")
            return f"{_FUNCS[name]}({','.join(walk(arg) for arg in node.args)})"
        raise PlanError(f"Unsupported formula syntax ({type(node).__name__}) in {expr!r}.")

    return "=" + walk(tree)
