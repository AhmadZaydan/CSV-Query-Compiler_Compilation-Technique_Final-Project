# ast_nodes.py
from dataclasses import dataclass
from typing import List, Optional, Union

# --- Basic expression nodes ---
@dataclass
class SelectItem:
    pass

@dataclass
class Star(SelectItem):
    pass

@dataclass
class ColumnSelect(SelectItem):
    name: str
    alias: Optional[str] = None

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
    distinct: bool
    items: List[SelectItem]

@dataclass
class OrderByClause:
    column: str
    ascending: bool     # True for ASC, False for DESC

@dataclass
class LimitClause:
    count: int

@dataclass
class OffsetClause:
    count: int

@dataclass
class Query:
    from_clause: FromClause
    select_clause: SelectClause
    where_expr: Optional[Expr]
    order_by: Optional[OrderByClause]
    limit: Optional[LimitClause]
    offset: Optional[OffsetClause]

@dataclass
class NotOp(Expr):
    expr: Expr

@dataclass
class InPredicate(Expr):
    column: ColumnRef
    values: List[Literal]

@dataclass
class BetweenPredicate(Expr):
    column: ColumnRef
    low: Literal
    high: Literal

@dataclass
class LikePredicate(Expr):
    column: ColumnRef
    pattern: str  # store the string pattern

@dataclass
class IsNullPredicate(Expr):
    column: ColumnRef
    negate: bool  # False = IS NULL, True = IS NOT NULL


