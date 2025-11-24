# executor.py
from typing import Optional
import pandas as pd

from ast_nodes import (
    Query, FromClause, SelectClause, OrderByClause, LimitClause,
    Expr, ColumnRef, Literal, Comparison, BooleanOp
)


# ---------- Helper: semantic check for columns ----------

def _check_column_exists(df: pd.DataFrame, col: str):
    if col not in df.columns:
        raise ValueError(
            f'Column "{col}" not found in CSV. Available columns: {list(df.columns)}'
        )


# ---------- Helper: WHERE expression evaluation ----------

def eval_where_expr(df: pd.DataFrame, expr: Expr):
    """
    Convert an Expr (BooleanOp or Comparison) into a boolean mask for df.
    """
    if isinstance(expr, BooleanOp):
        left_mask = eval_where_expr(df, expr.left)
        right_mask = eval_where_expr(df, expr.right)
        if expr.op == "AND":
            return left_mask & right_mask
        elif expr.op == "OR":
            return left_mask | right_mask
        else:
            raise ValueError(f"Unknown boolean op {expr.op}")

    elif isinstance(expr, Comparison):
        col = expr.left.name
        _check_column_exists(df, col)
        series = df[col]
        value = expr.right.value
        op = expr.op

        # Perform the comparison
        if op == "=":
            return series == value
        elif op == "!=":
            return series != value
        elif op == "<":
            return series < value
        elif op == "<=":
            return series <= value
        elif op == ">":
            return series > value
        elif op == ">=":
            return series >= value
        else:
            raise ValueError(f"Unknown comparison op {op}")

    else:
        raise TypeError(f"Unsupported expression type in WHERE: {type(expr)}")


# ---------- Main: execute query ----------

def execute_query(query: Query) -> pd.DataFrame:
    # 1. FROM: load CSV
    filename = query.from_clause.filename
    df = pd.read_csv(filename)

    # 🔥 Auto-clean numeric-looking columns
    # - Remove commas (e.g. "28,000,000,000" → "28000000000")
    # - Try to convert to numeric (if fails, leave as string)
    for col in df.columns:
        # Work on a copy as string first
        s = df[col].astype(str).str.replace(",", "", regex=False)
        # Try converting to number
        converted = pd.to_numeric(s, errors="ignore")
        df[col] = converted

    # 2. WHERE: filter rows
    if query.where_expr is not None:
        mask = eval_where_expr(df, query.where_expr)
        df = df[mask]

    # 3. SELECT: choose columns
    select_cols = query.select_clause.columns
    for col in select_cols:
        _check_column_exists(df, col)

    df = df[select_cols]

    # 4. ORDER BY
    if query.order_by is not None:
        ob = query.order_by
        _check_column_exists(df, ob.column)
        df = df.sort_values(by=ob.column, ascending=ob.ascending)

    # 5. LIMIT
    if query.limit is not None:
        df = df.head(query.limit.count)

    return df


# ---------- Quick test ----------

if __name__ == "__main__":
    from parser import parse

    query_text = '''
    FROM "HARGA RUMAH JAKSEL.csv"
    SELECT HARGA, LT
    WHERE HARGA <= 10000000000 AND LT <= 1000
    ORDER BY HARGA DESC
    LIMIT 10
    '''

    q = parse(query_text)
    print("AST:", q)

    result = execute_query(q)
    print("\nResult:")
    print(result)
