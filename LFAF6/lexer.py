"""
lexer.py — Lexer for a mini programming language "TinyLang"

TinyLang supports:
  - Variable declarations:   let x = 10
  - Conditionals:            if / else / elif
  - Loops:                   while / for / in
  - Functions:               fn add(a, b) { return a + b }
  - Print:                   print("hello")
  - Types:                   int, float, bool, str
  - Booleans:                true / false
  - Comments:                # single-line comment
  - Arithmetic:              + - * / % **
  - Comparison:              == != < > <= >=
  - Logical:                 and or not
  - Integers and floats:     42  3.14
  - String literals:         "hello world"
"""


# ------------------------------------------------------------------ #
#  Token types                                                         #
# ------------------------------------------------------------------ #

class TokenType:
    # Literals
    INTEGER     = "INTEGER"
    FLOAT       = "FLOAT"
    STRING      = "STRING"
    BOOLEAN     = "BOOLEAN"

    # Identifiers / Keywords
    IDENTIFIER  = "IDENTIFIER"
    KEYWORD     = "KEYWORD"

    # Arithmetic operators
    PLUS        = "PLUS"
    MINUS       = "MINUS"
    STAR        = "STAR"
    SLASH       = "SLASH"
    PERCENT     = "PERCENT"
    POWER       = "POWER"       # **

    # Comparison operators
    EQ          = "EQ"          # ==
    NEQ         = "NEQ"         # !=
    LT          = "LT"          # <
    GT          = "GT"          # >
    LTE         = "LTE"         # <=
    GTE         = "GTE"         # >=

    # Assignment
    ASSIGN      = "ASSIGN"      # =

    # Delimiters
    LPAREN      = "LPAREN"      # (
    RPAREN      = "RPAREN"      # )
    LBRACE      = "LBRACE"      # {
    RBRACE      = "RBRACE"      # }
    LBRACKET    = "LBRACKET"    # [
    RBRACKET    = "RBRACKET"    # ]
    COMMA       = "COMMA"       # ,
    COLON       = "COLON"       # :
    SEMICOLON   = "SEMICOLON"   # ;
    DOT         = "DOT"         # .
    ARROW       = "ARROW"       # ->

    # Special
    NEWLINE     = "NEWLINE"
    COMMENT     = "COMMENT"
    EOF         = "EOF"
    UNKNOWN     = "UNKNOWN"


# Reserved keywords for TinyLang
KEYWORDS = {
    "let", "fn", "return", "if", "elif", "else",
    "while", "for", "in", "break", "continue",
    "print", "and", "or", "not",
    "int", "float", "bool", "str",
    "true", "false", "null",
}


# ------------------------------------------------------------------ #
#  Token                                                               #
# ------------------------------------------------------------------ #

class Token:
    def __init__(self, token_type: str, value: str, line: int = 0, col: int = 0):
        self.type  = token_type
        self.value = value
        self.line  = line
        self.col   = col

    def __repr__(self):
        return f"Token({self.type:<12} {self.value!r:<20} line={self.line}, col={self.col})"


# ------------------------------------------------------------------ #
#  LexerError                                                          #
# ------------------------------------------------------------------ #

class LexerError(Exception):
    def __init__(self, message: str, line: int, col: int):
        super().__init__(f"LexerError at line {line}, col {col}: {message}")
        self.line = line
        self.col  = col


# ------------------------------------------------------------------ #
#  Lexer                                                               #
# ------------------------------------------------------------------ #

class Lexer:
    """
    Single-pass character-by-character lexer for TinyLang.

    The lexer maintains:
      - self.text   — the full source string
      - self.pos    — current position (index)
      - self.line   — current line number (1-based)
      - self.col    — current column number (1-based)
    """

    def __init__(self, source: str):
        self.text   = source
        self.pos    = 0
        self.line   = 1
        self.col    = 1

    # ---------------------------------------------------------------- #
    #  Helpers                                                           #
    # ---------------------------------------------------------------- #

    def current(self) -> str:
        """Return the character at the current position, or '' if past end."""
        return self.text[self.pos] if self.pos < len(self.text) else ""

    def peek(self, offset: int = 1) -> str:
        """Look ahead by offset characters without advancing."""
        idx = self.pos + offset
        return self.text[idx] if idx < len(self.text) else ""

    def advance(self) -> str:
        """Consume the current character and move forward."""
        ch = self.current()
        self.pos += 1
        if ch == "\n":
            self.line += 1
            self.col = 1
        else:
            self.col += 1
        return ch

    def make_token(self, token_type: str, value: str, line: int, col: int) -> Token:
        return Token(token_type, value, line, col)

    # ---------------------------------------------------------------- #
    #  Skipping                                                          #
    # ---------------------------------------------------------------- #

    def skip_whitespace(self):
        """Skip spaces and tabs (newlines are emitted as NEWLINE tokens)."""
        while self.current() in (" ", "\t", "\r"):
            self.advance()

    # ---------------------------------------------------------------- #
    #  Scanning individual token kinds                                   #
    # ---------------------------------------------------------------- #

    def scan_comment(self, line: int, col: int) -> Token:
        """Consume from '#' to end of line."""
        value = ""
        while self.current() and self.current() != "\n":
            value += self.advance()
        return self.make_token(TokenType.COMMENT, value.strip(), line, col)

    def scan_string(self, line: int, col: int) -> Token:
        """
        Consume a double-quoted string literal.
        Supports escape sequences: \\n  \\"  \\\\
        """
        self.advance()   # consume opening "
        value = ""
        while self.current() and self.current() != '"':
            ch = self.advance()
            if ch == "\\" and self.current() in ('"', "\\", "n", "t"):
                esc = self.advance()
                ch = {"n": "\n", "t": "\t", '"': '"', "\\": "\\"}.get(esc, esc)
            value += ch
        if not self.current():
            raise LexerError("Unterminated string literal", line, col)
        self.advance()   # consume closing "
        return self.make_token(TokenType.STRING, value, line, col)

    def scan_number(self, line: int, col: int) -> Token:
        """
        Consume an integer or float literal.
        Floats are detected by a '.' followed by another digit.
        """
        value = ""
        is_float = False

        while self.current().isdigit():
            value += self.advance()

        if self.current() == "." and self.peek().isdigit():
            is_float = True
            value += self.advance()   # consume '.'
            while self.current().isdigit():
                value += self.advance()

        token_type = TokenType.FLOAT if is_float else TokenType.INTEGER
        return self.make_token(token_type, value, line, col)

    def scan_identifier_or_keyword(self, line: int, col: int) -> Token:
        """
        Consume a word (letters, digits, underscores).
        After reading, check if it's a reserved keyword, boolean, or identifier.
        """
        value = ""
        while self.current().isalnum() or self.current() == "_":
            value += self.advance()

        if value in ("true", "false"):
            return self.make_token(TokenType.BOOLEAN, value, line, col)
        if value in KEYWORDS:
            return self.make_token(TokenType.KEYWORD, value, line, col)
        return self.make_token(TokenType.IDENTIFIER, value, line, col)

    # ---------------------------------------------------------------- #
    #  Main tokenize loop                                                #
    # ---------------------------------------------------------------- #

    def tokenize(self) -> list:
        """
        Walk through the source and return a list of Token objects.
        The last token is always EOF.
        """
        tokens = []

        while self.pos < len(self.text):
            self.skip_whitespace()
            if not self.current():
                break

            ch   = self.current()
            line = self.line
            col  = self.col

            # --- Newline ---
            if ch == "\n":
                self.advance()
                tokens.append(self.make_token(TokenType.NEWLINE, "\\n", line, col))

            # --- Comment ---
            elif ch == "#":
                tokens.append(self.scan_comment(line, col))

            # --- String literal ---
            elif ch == '"':
                tokens.append(self.scan_string(line, col))

            # --- Number ---
            elif ch.isdigit():
                tokens.append(self.scan_number(line, col))

            # --- Identifier / Keyword ---
            elif ch.isalpha() or ch == "_":
                tokens.append(self.scan_identifier_or_keyword(line, col))

            # --- Two-character operators ---
            elif ch == "*" and self.peek() == "*":
                self.advance(); self.advance()
                tokens.append(self.make_token(TokenType.POWER, "**", line, col))
            elif ch == "=" and self.peek() == "=":
                self.advance(); self.advance()
                tokens.append(self.make_token(TokenType.EQ, "==", line, col))
            elif ch == "!" and self.peek() == "=":
                self.advance(); self.advance()
                tokens.append(self.make_token(TokenType.NEQ, "!=", line, col))
            elif ch == "<" and self.peek() == "=":
                self.advance(); self.advance()
                tokens.append(self.make_token(TokenType.LTE, "<=", line, col))
            elif ch == ">" and self.peek() == "=":
                self.advance(); self.advance()
                tokens.append(self.make_token(TokenType.GTE, ">=", line, col))
            elif ch == "-" and self.peek() == ">":
                self.advance(); self.advance()
                tokens.append(self.make_token(TokenType.ARROW, "->", line, col))

            # --- Single-character operators / delimiters ---
            elif ch == "+":
                self.advance()
                tokens.append(self.make_token(TokenType.PLUS, "+", line, col))
            elif ch == "-":
                self.advance()
                tokens.append(self.make_token(TokenType.MINUS, "-", line, col))
            elif ch == "*":
                self.advance()
                tokens.append(self.make_token(TokenType.STAR, "*", line, col))
            elif ch == "/":
                self.advance()
                tokens.append(self.make_token(TokenType.SLASH, "/", line, col))
            elif ch == "%":
                self.advance()
                tokens.append(self.make_token(TokenType.PERCENT, "%", line, col))
            elif ch == "=":
                self.advance()
                tokens.append(self.make_token(TokenType.ASSIGN, "=", line, col))
            elif ch == "<":
                self.advance()
                tokens.append(self.make_token(TokenType.LT, "<", line, col))
            elif ch == ">":
                self.advance()
                tokens.append(self.make_token(TokenType.GT, ">", line, col))
            elif ch == "(":
                self.advance()
                tokens.append(self.make_token(TokenType.LPAREN, "(", line, col))
            elif ch == ")":
                self.advance()
                tokens.append(self.make_token(TokenType.RPAREN, ")", line, col))
            elif ch == "{":
                self.advance()
                tokens.append(self.make_token(TokenType.LBRACE, "{", line, col))
            elif ch == "}":
                self.advance()
                tokens.append(self.make_token(TokenType.RBRACE, "}", line, col))
            elif ch == "[":
                self.advance()
                tokens.append(self.make_token(TokenType.LBRACKET, "[", line, col))
            elif ch == "]":
                self.advance()
                tokens.append(self.make_token(TokenType.RBRACKET, "]", line, col))
            elif ch == ",":
                self.advance()
                tokens.append(self.make_token(TokenType.COMMA, ",", line, col))
            elif ch == ":":
                self.advance()
                tokens.append(self.make_token(TokenType.COLON, ":", line, col))
            elif ch == ";":
                self.advance()
                tokens.append(self.make_token(TokenType.SEMICOLON, ";", line, col))
            elif ch == ".":
                self.advance()
                tokens.append(self.make_token(TokenType.DOT, ".", line, col))

            # --- Unknown character ---
            else:
                tokens.append(self.make_token(TokenType.UNKNOWN, self.advance(), line, col))

        tokens.append(self.make_token(TokenType.EOF, "", self.line, self.col))
        return tokens
