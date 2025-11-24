# ast_nodes.py
from dataclasses import dataclass
from typing import List, Optional, Union

# --- Basic expression nodes ---

@dataclass
class Expr:
    pass

@dataclass
class ColumnRef(Expr):
    name: str

@dataclass
class Literal(Expr):
    value: Union[int, float, str]

@dataclass
class Comparison(Expr):
    left: ColumnRef     # only column on left for now
    op: str             # "=", "!=", "<", "<=", ">", ">="
    right: Literal

@dataclass
class BooleanOp(Expr):
    op: str             # "AND" or "OR"
    left: Expr
    right: Expr

# --- Query structure nodes ---

@dataclass
class FromClause:
    filename: str       # e.g. "students.csv"

@dataclass
class SelectClause:
    columns: List[str]  # list of column names

@dataclass
class OrderByClause:
    column: str
    ascending: bool     # True for ASC, False for DESC

@dataclass
class LimitClause:
    count: int

@dataclass
class Query:
    from_clause: FromClause
    select_clause: SelectClause
    where_expr: Optional[Expr]
    order_by: Optional[OrderByClause]
    limit: Optional[LimitClause]
