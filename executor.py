# executor.py
from typing import Optional
import pandas as pd
import re

from ast_nodes import (
    Query, FromClause, SelectClause, OrderByClause, LimitClause,
    Expr, ColumnRef, Literal, Comparison, BooleanOp, ColumnSelect, Star,
    BooleanOp, NotOp, Comparison, InPredicate, BetweenPredicate,
    LikePredicate, IsNullPredicate, ColumnRef, Literal
)


# ---------- Helper: semantic check for columns ----------

def _check_column_exists(df: pd.DataFrame, col: str):
    if col not in df.columns:
        raise ValueError(
            f'Column "{col}" not found in CSV. Available columns: {list(df.columns)}'
        )


# ---------- Helper: WHERE expression evaluation ----------

def eval_where_expr(df, expr):
    if isinstance(expr, BooleanOp):
        left = eval_where_expr(df, expr.left)
        right = eval_where_expr(df, expr.right)
        return (left & right) if expr.op == "AND" else (left | right)

    if isinstance(expr, NotOp):
        return ~eval_where_expr(df, expr.expr)

    if isinstance(expr, Comparison):
        col = expr.left.name
        _check_column_exists(df, col)
        s = df[col]
        v = expr.right.value
        if expr.op == "=":  return s == v
        if expr.op == "!=": return s != v
        if expr.op == "<":  return s < v
        if expr.op == "<=": return s <= v
        if expr.op == ">":  return s > v
        if expr.op == ">=": return s >= v
        raise ValueError("Unknown op")

    if isinstance(expr, InPredicate):
        col = expr.column.name
        _check_column_exists(df, col)
        values = [lit.value for lit in expr.values]
        return df[col].isin(values)

    if isinstance(expr, BetweenPredicate):
        col = expr.column.name
        _check_column_exists(df, col)
        low = expr.low.value
        high = expr.high.value
        return (df[col] >= low) & (df[col] <= high)

    if isinstance(expr, IsNullPredicate):
        col = expr.column.name
        _check_column_exists(df, col)
        mask = df[col].isna()
        return ~mask if expr.negate else mask

    if isinstance(expr, LikePredicate):
        col = expr.column.name
        _check_column_exists(df, col)
        # simple SQL-like: % -> .*, _ -> .
        pat = re.escape(expr.pattern)
        pat = pat.replace(r"\%", ".*").replace(r"\_", ".")
        return df[col].astype(str).str.match(f"^{pat}$", na=False)

    raise TypeError(f"Unsupported WHERE expr: {type(expr)}")


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
    # select_cols = query.select_clause.columns
    # for col in select_cols:
    #     _check_column_exists(df, col)

    # df = df[select_cols]

    # Build selected columns
    if any(isinstance(it, Star) for it in query.select_clause.items):
        df_selected = df.copy()
    else:
        cols = []
        rename_map = {}
        for it in query.select_clause.items:
            if isinstance(it, ColumnSelect):
                _check_column_exists(df, it.name)
                cols.append(it.name)
                if it.alias:
                    rename_map[it.name] = it.alias

        df_selected = df[cols]
        if rename_map:
            df_selected = df_selected.rename(columns=rename_map)

    df = df_selected

    if query.select_clause.distinct:
        df = df.drop_duplicates()

    # 4. ORDER BY
    if query.order_by is not None:
        ob = query.order_by
        _check_column_exists(df, ob.column)
        df = df.sort_values(by=ob.column, ascending=ob.ascending)

    if query.offset is not None:
        df = df.iloc[query.offset.count:]

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
