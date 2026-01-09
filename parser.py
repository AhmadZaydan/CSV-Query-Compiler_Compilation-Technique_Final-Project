from __future__ import annotations

from typing import List, Optional

from ast_nodes import (
    BetweenPredicate,
    BooleanOp,
    ColumnRef,
    ColumnSelect,
    Comparison,
    FromClause,
    InPredicate,
    IsNullPredicate,
    LikePredicate,
    LimitClause,
    Literal,
    NotOp,
    OffsetClause,
    OrderByClause,
    Query,
    SelectClause,
    SelectItem,
    Star,
)
from lexer import Token, lex


_OP_MAP = {
    "EQ": "=",
    "NE": "!=",
    "LT": "<",
    "LE": "<=",
    "GT": ">",
    "GE": ">=",
}


class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0

    def current(self) -> Optional[Token]:
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def match(self, *types: str) -> Optional[Token]:
        tok = self.current()
        if tok and tok.type in types:
            self.pos += 1
            return tok
        return None

    def expect(self, *types: str) -> Token:
        tok = self.current()
        if tok and tok.type in types:
            self.pos += 1
            return tok

        expected = " or ".join(types)
        if tok:
            raise SyntaxError(
                f"Expected {expected} at line {tok.line}, col {tok.column}, "
                f"got {tok.type} ({tok.value!r})"
            )
        raise SyntaxError(f"Expected {expected} but reached end of input")

    def parse_query(self) -> Query:
        from_clause = self.parse_from_clause()
        select_clause = self.parse_select_clause()
        where_expr = self.parse_where_clause_opt()
        order_by = self.parse_order_clause_opt()
        limit = self.parse_limit_clause_opt()
        offset = self.parse_offset_clause_opt()

        if self.current() is not None:
            tok = self.current()
            raise SyntaxError(
                f"Unexpected token {tok.type} ({tok.value!r}) at line {tok.line}, col {tok.column}"
            )

        return Query(
            from_clause=from_clause,
            select_clause=select_clause,
            where_expr=where_expr,
            order_by=order_by,
            limit=limit,
            offset=offset,
        )

    def parse_from_clause(self) -> FromClause:
        self.expect("FROM")
        filename = self.expect("STRING").value
        return FromClause(filename=filename)

    def parse_select_clause(self) -> SelectClause:
        self.expect("SELECT")
        distinct = self.match("DISTINCT") is not None

        items = [self.parse_select_item()]
        while self.match("COMMA"):
            items.append(self.parse_select_item())

        return SelectClause(distinct=distinct, items=items)

    def parse_select_item(self) -> SelectItem:
        if self.match("STAR"):
            return Star()

        name = self.expect("IDENT").value
        alias = None
        if self.match("AS"):
            alias = self.expect("IDENT").value
        return ColumnSelect(name=name, alias=alias)

    def parse_where_clause_opt(self):
        if not self.match("WHERE"):
            return None
        return self.parse_bool_expr()

    def parse_order_clause_opt(self):
        if self.match("SORTBY"):
            return self._parse_order_tail()

        if self.match("ORDER"):
            self.expect("BY")
            return self._parse_order_tail()

        return None

    def _parse_order_tail(self) -> OrderByClause:
        col = self.expect("IDENT").value
        ascending = True
        if self.match("ASC"):
            ascending = True
        elif self.match("DESC"):
            ascending = False
        return OrderByClause(column=col, ascending=ascending)

    def parse_limit_clause_opt(self) -> Optional[LimitClause]:
        if not self.match("LIMIT"):
            return None
        count = int(float(self.expect("NUMBER").value))
        return LimitClause(count=count)

    def parse_offset_clause_opt(self) -> Optional[OffsetClause]:
        if not self.match("OFFSET"):
            return None
        count = int(float(self.expect("NUMBER").value))
        return OffsetClause(count=count)

    def parse_bool_expr(self):
        left = self.parse_bool_term()
        while self.match("OR"):
            right = self.parse_bool_term()
            left = BooleanOp(op="OR", left=left, right=right)
        return left

    def parse_bool_term(self):
        left = self.parse_bool_factor()
        while self.match("AND"):
            right = self.parse_bool_factor()
            left = BooleanOp(op="AND", left=left, right=right)
        return left

    def parse_bool_factor(self):
        negate = self.match("NOT") is not None

        if self.match("LPAREN"):
            expr = self.parse_bool_expr()
            self.expect("RPAREN")
        else:
            expr = self.parse_predicate()

        return NotOp(expr=expr) if negate else expr

    def parse_literal(self) -> Literal:
        tok = self.expect("NUMBER", "STRING")
        if tok.type == "NUMBER":
            text = tok.value
            value = float(text) if "." in text else int(text)
        else:
            value = tok.value
        return Literal(value=value)

    def parse_predicate(self):
        column = ColumnRef(name=self.expect("IDENT").value)

        if self.match("IS"):
            negate = self.match("NOT") is not None
            self.expect("NULL")
            return IsNullPredicate(column=column, negate=negate)

        if self.match("IN"):
            self.expect("LPAREN")
            values = [self.parse_literal()]
            while self.match("COMMA"):
                values.append(self.parse_literal())
            self.expect("RPAREN")
            return InPredicate(column=column, values=values)

        if self.match("BETWEEN"):
            low = self.parse_literal()
            self.expect("AND")
            high = self.parse_literal()
            return BetweenPredicate(column=column, low=low, high=high)

        if self.match("LIKE"):
            pattern = self.expect("STRING").value
            return LikePredicate(column=column, pattern=pattern)

        op_tok = self.expect("EQ", "NE", "LT", "LE", "GT", "GE")
        op = _OP_MAP[op_tok.type]
        right = self.parse_literal()
        return Comparison(left=column, op=op, right=right)


def parse(text: str) -> Query:
    return Parser(lex(text)).parse_query()
