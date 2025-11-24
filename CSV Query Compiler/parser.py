# parser.py
from typing import List, Optional
from lexer import Token, lex
from ast_nodes import (
    Query, FromClause, SelectClause, OrderByClause, LimitClause,
    Expr, ColumnRef, Literal, Comparison, BooleanOp
)

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0  # current index

    # --- low-level helpers ---

    def current(self) -> Optional[Token]:
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def advance(self) -> Optional[Token]:
        tok = self.current()
        if tok is not None:
            self.pos += 1
        return tok

    def match(self, *types: str) -> Optional[Token]:
        """If current token type is in types, consume and return it; else None."""
        tok = self.current()
        if tok and tok.type in types:
            self.pos += 1
            return tok
        return None

    def expect(self, *types: str) -> Token:
        """Expect one of types; raise SyntaxError if not matched."""
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
        else:
            raise SyntaxError(f"Expected {expected} but reached end of input")
        
        # --- entry point ---

    def parse_query(self) -> Query:
        from_clause = self.parse_from_clause()
        select_clause = self.parse_select_clause()
        where_expr = self.parse_where_clause_opt()
        order_by = self.parse_order_clause_opt()
        limit = self.parse_limit_clause_opt()

        # Optionally check: no extra tokens left
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
        )
    
    def parse_from_clause(self) -> FromClause:
        self.expect("FROM")
        filename_tok = self.expect("STRING")
        return FromClause(filename=filename_tok.value)

    def parse_select_clause(self) -> SelectClause:
        self.expect("SELECT")
        columns: List[str] = []

        ident_tok = self.expect("IDENT")
        columns.append(ident_tok.value)

        # ("," IDENT)*
        while self.match("COMMA"):
            ident_tok = self.expect("IDENT")
            columns.append(ident_tok.value)

        return SelectClause(columns=columns)
    
    def parse_where_clause_opt(self) -> Optional[Expr]:
        if not self.match("WHERE"):
            return None
        # we consumed WHERE if it was there, so parse bool expression
        return self.parse_bool_expr()

    def parse_order_clause_opt(self) -> Optional[OrderByClause]:
        # ORDER BY ...
        if not self.match("ORDER"):
            return None
        self.expect("BY")
        col_tok = self.expect("IDENT")

        ascending = True
        # optional ASC / DESC
        if (tok := self.match("ASC", "DESC")) is not None:
            ascending = (tok.type == "ASC")

        return OrderByClause(column=col_tok.value, ascending=ascending)

    def parse_limit_clause_opt(self) -> Optional[LimitClause]:
        if not self.match("LIMIT"):
            return None
        num_tok = self.expect("NUMBER")
        count = int(float(num_tok.value))  # simple conversion
        return LimitClause(count=count)
    
        # bool_expr := bool_term (OR bool_term)*
    def parse_bool_expr(self) -> Expr:
        left = self.parse_bool_term()
        while self.match("OR"):
            op = "OR"
            right = self.parse_bool_term()
            left = BooleanOp(op=op, left=left, right=right)
        return left

    # bool_term := bool_factor (AND bool_factor)*
    def parse_bool_term(self) -> Expr:
        left = self.parse_bool_factor()
        while self.match("AND"):
            op = "AND"
            right = self.parse_bool_factor()
            left = BooleanOp(op=op, left=left, right=right)
        return left

    # bool_factor := comparison | LPAREN bool_expr RPAREN
    def parse_bool_factor(self) -> Expr:
        if self.match("LPAREN"):
            expr = self.parse_bool_expr()
            self.expect("RPAREN")
            return expr
        else:
            return self.parse_comparison()

    # comparison := IDENT op value
    def parse_comparison(self) -> Comparison:
        col_tok = self.expect("IDENT")
        left = ColumnRef(name=col_tok.value)

        op_tok = self.expect("EQ", "NE", "LT", "LE", "GT", "GE")
        op_map = {
            "EQ": "=",
            "NE": "!=",
            "LT": "<",
            "LE": "<=",
            "GT": ">",
            "GE": ">=",
        }
        op = op_map[op_tok.type]

        val_tok = self.expect("NUMBER", "STRING")
        if val_tok.type == "NUMBER":
            # decide int vs float
            if "." in val_tok.value:
                val = float(val_tok.value)
            else:
                val = int(val_tok.value)
        else:  # STRING
            val = val_tok.value

        right = Literal(value=val)
        return Comparison(left=left, op=op, right=right)

def parse(text: str) -> Query:
    tokens = lex(text)
    parser = Parser(tokens)
    return parser.parse_query()

if __name__ == "__main__":
    query_text = '''
    FROM "students.csv"
    SELECT name, score
    WHERE score >= 80 AND city = "Bandung"
    ORDER BY score DESC
    LIMIT 10
    '''
    q = parse(query_text)
    print(q)




