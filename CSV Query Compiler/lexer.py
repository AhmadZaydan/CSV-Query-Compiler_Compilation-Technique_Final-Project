# lexer.py
import re
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Token:
    type: str   # e.g. 'SELECT', 'IDENT', 'NUMBER', 'STRING', 'EQ', ...
    value: str  # original text
    line: int
    column: int

    def __repr__(self):
        return f"Token({self.type}, {self.value!r}, line={self.line}, col={self.column})"

# Keywords (we’ll detect these after matching IDENT)
KEYWORDS = {
    "FROM", "SELECT", "WHERE", "ORDER", "BY", "LIMIT",
    "AND", "OR", "ASC", "DESC"
}

# Order matters for some tokens (e.g. >= must be checked before >)
TOKEN_SPECIFICATION = [
    ("NUMBER",   r'\d+(\.\d+)?'),        # Integer or decimal number
    ("STRING",   r'"([^"\\]|\\.)*"'),    # "string with \" escapes"
    ("GE",       r'>='),                 # >=
    ("LE",       r'<='),                 # <=
    ("NE",       r'!='),                 # !=
    ("GT",       r'>'),                  # >
    ("LT",       r'<'),                  # <
    ("EQ",       r'='),                  # =
    ("COMMA",    r','),                  # ,
    ("LPAREN",   r'\('),                 # (
    ("RPAREN",   r'\)'),                 # )
    ("IDENT",    r'[A-Za-z_][A-Za-z0-9_]*'),  # Identifiers
    ("NEWLINE",  r'\n'),                 # Line breaks
    ("SKIP",     r'[ \t]+'),             # Spaces and tabs
    ("MISMATCH", r'.'),                  # Any other character (error)
]

# Build the big regex
TOK_REGEX = "|".join(
    f"(?P<{name}>{pattern})" for name, pattern in TOKEN_SPECIFICATION
)
MASTER_RE = re.compile(TOK_REGEX)

def lex(text: str) -> List[Token]:
    """
    Turn the query string into a list of Tokens.
    Raises SyntaxError on invalid characters.
    """
    tokens: List[Token] = []
    line_num = 1
    line_start = 0

    for mo in MASTER_RE.finditer(text):
        kind = mo.lastgroup
        value = mo.group()
        column = mo.start() - line_start + 1

        if kind == "NUMBER":
            # you can keep it as string or convert to float/int later
            tokens.append(Token("NUMBER", value, line_num, column))

        elif kind == "STRING":
            # strip the surrounding quotes, but keep original if you want
            # value[1:-1] removes the first and last quote
            tokens.append(Token("STRING", value[1:-1], line_num, column))

        elif kind == "IDENT":
            upper_val = value.upper()
            if upper_val in KEYWORDS:
                tokens.append(Token(upper_val, value, line_num, column))
            else:
                tokens.append(Token("IDENT", value, line_num, column))

        elif kind in {"GE", "LE", "NE", "GT", "LT", "EQ"}:
            tokens.append(Token(kind, value, line_num, column))

        elif kind == "COMMA":
            tokens.append(Token("COMMA", value, line_num, column))

        elif kind == "LPAREN":
            tokens.append(Token("LPAREN", value, line_num, column))

        elif kind == "RPAREN":
            tokens.append(Token("RPAREN", value, line_num, column))

        elif kind == "NEWLINE":
            line_num += 1
            line_start = mo.end()

        elif kind == "SKIP":
            # ignore whitespace
            continue

        elif kind == "MISMATCH":
            raise SyntaxError(
                f"Unexpected character {value!r} at line {line_num}, column {column}"
            )

    return tokens

# text = '''
#     FROM "students.csv"
#     SELECT name, score
#     WHERE score >= 80 AND city = "Bandung"
#     ORDER BY score DESC
#     LIMIT 10
#     '''

# toks = lex(text)
# for t in toks:
#     print(t)