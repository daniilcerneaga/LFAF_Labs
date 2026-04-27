"""
parser.py — Recursive-descent parser for TinyLang

Takes the token list produced by Lexer and builds an AST
made of nodes from ast_nodes.py.

Grammar (simplified, informal):

  program      := statement* EOF
  statement    := var_decl | assign | if_stmt | while_stmt
               |  for_stmt | fn_def | return_stmt
               |  print_stmt | break_stmt | continue_stmt
               |  expr_stmt
  var_decl     := 'let' IDENTIFIER '=' expression NEWLINE
  assign       := IDENTIFIER '=' expression NEWLINE
  if_stmt      := 'if' expression block ('elif' expression block)* ('else' block)?
  while_stmt   := 'while' expression block
  for_stmt     := 'for' IDENTIFIER 'in' expression block
  fn_def       := 'fn' IDENTIFIER '(' params ')' block
  return_stmt  := 'return' expression NEWLINE
  print_stmt   := 'print' '(' expression ')' NEWLINE
  break_stmt   := 'break' NEWLINE
  continue_stmt:= 'continue' NEWLINE
  block        := '{' NEWLINE? statement* '}'
  params       := (IDENTIFIER (',' IDENTIFIER)*)?

  expression   := logical_or
  logical_or   := logical_and ('or' logical_and)*
  logical_and  := equality   ('and' equality)*
  equality     := comparison (('==' | '!=') comparison)*
  comparison   := addition   (('<' | '>' | '<=' | '>=') addition)*
  addition     := term       (('+' | '-') term)*
  term         := power      (('*' | '/' | '%') power)*
  power        := unary      ('**' unary)*
  unary        := ('not' | '-') unary | primary
  primary      := INTEGER | FLOAT | STRING | BOOLEAN | 'null'
               |  IDENTIFIER '(' args ')' | IDENTIFIER
               |  '(' expression ')' | '[' list_items ']'
"""

from lexer import TokenType
from ast_nodes import (
    ProgramNode, VarDeclNode, AssignNode, ReturnNode, PrintNode,
    BreakNode, ContinueNode, BlockNode, IfNode, WhileNode, ForNode,
    FunctionDefNode, BinaryOpNode, UnaryOpNode, FunctionCallNode,
    ListLiteralNode, IntLiteralNode, FloatLiteralNode, StringLiteralNode,
    BoolLiteralNode, NullLiteralNode, IdentifierNode,
)


# ------------------------------------------------------------------ #
#  ParseError                                                          #
# ------------------------------------------------------------------ #

class ParseError(Exception):
    def __init__(self, message: str, token):
        super().__init__(
            f"ParseError at line {token.line}, col {token.col} "
            f"(token {token.type} {token.value!r}): {message}"
        )
        self.token = token


# ------------------------------------------------------------------ #
#  Parser                                                              #
# ------------------------------------------------------------------ #

class Parser:
    """
    Recursive-descent parser.

    self.tokens  — flat list of tokens from the Lexer (NEWLINE + COMMENT kept)
    self.pos     — index of the current token
    """

    def __init__(self, tokens: list):
        # Strip COMMENT tokens; keep NEWLINE as statement separators
        self.tokens = [t for t in tokens if t.type != TokenType.COMMENT]
        self.pos    = 0

    # ---------------------------------------------------------------- #
    #  Low-level helpers                                                 #
    # ---------------------------------------------------------------- #

    def current(self):
        return self.tokens[self.pos]

    def peek(self, offset: int = 1):
        idx = self.pos + offset
        if idx < len(self.tokens):
            return self.tokens[idx]
        return self.tokens[-1]   # EOF

    def advance(self):
        tok = self.tokens[self.pos]
        if self.pos < len(self.tokens) - 1:
            self.pos += 1
        return tok

    def skip_newlines(self):
        while self.current().type == TokenType.NEWLINE:
            self.advance()

    def expect(self, token_type: str, value: str = None):
        """
        Consume the current token if it matches; raise ParseError otherwise.
        """
        tok = self.current()
        if tok.type != token_type:
            raise ParseError(
                f"expected {token_type}" + (f" '{value}'" if value else ""),
                tok,
            )
        if value is not None and tok.value != value:
            raise ParseError(f"expected '{value}' got '{tok.value}'", tok)
        return self.advance()

    def match(self, token_type: str, value: str = None) -> bool:
        """Return True (and advance) if current token matches."""
        tok = self.current()
        if tok.type != token_type:
            return False
        if value is not None and tok.value != value:
            return False
        self.advance()
        return True

    def check(self, token_type: str, value: str = None) -> bool:
        """Peek without consuming."""
        tok = self.current()
        if tok.type != token_type:
            return False
        if value is not None and tok.value != value:
            return False
        return True

    # ---------------------------------------------------------------- #
    #  Program / Statement dispatch                                      #
    # ---------------------------------------------------------------- #

    def parse(self) -> ProgramNode:
        statements = []
        self.skip_newlines()
        while not self.check(TokenType.EOF):
            stmt = self.parse_statement()
            if stmt is not None:
                statements.append(stmt)
            self.skip_newlines()
        return ProgramNode(statements)

    def parse_statement(self):
        self.skip_newlines()
        tok = self.current()

        # --- let ---
        if tok.type == TokenType.KEYWORD and tok.value == "let":
            return self.parse_var_decl()

        # --- fn ---
        if tok.type == TokenType.KEYWORD and tok.value == "fn":
            return self.parse_fn_def()

        # --- if ---
        if tok.type == TokenType.KEYWORD and tok.value == "if":
            return self.parse_if()

        # --- while ---
        if tok.type == TokenType.KEYWORD and tok.value == "while":
            return self.parse_while()

        # --- for ---
        if tok.type == TokenType.KEYWORD and tok.value == "for":
            return self.parse_for()

        # --- return ---
        if tok.type == TokenType.KEYWORD and tok.value == "return":
            return self.parse_return()

        # --- print ---
        if tok.type == TokenType.KEYWORD and tok.value == "print":
            return self.parse_print()

        # --- break ---
        if tok.type == TokenType.KEYWORD and tok.value == "break":
            self.advance()
            self.skip_newlines()
            return BreakNode()

        # --- continue ---
        if tok.type == TokenType.KEYWORD and tok.value == "continue":
            self.advance()
            self.skip_newlines()
            return ContinueNode()

        # --- assignment:  IDENTIFIER = expr  (look-ahead to '=') ---
        if (tok.type == TokenType.IDENTIFIER
                and self.peek().type == TokenType.ASSIGN):
            return self.parse_assign()

        # --- expression statement (function calls, etc.) ---
        expr = self.parse_expression()
        self.skip_newlines()
        return expr

    # ---------------------------------------------------------------- #
    #  Statement parsers                                                 #
    # ---------------------------------------------------------------- #

    def parse_var_decl(self) -> VarDeclNode:
        self.expect(TokenType.KEYWORD, "let")
        name_tok = self.expect(TokenType.IDENTIFIER)
        self.expect(TokenType.ASSIGN)
        value = self.parse_expression()
        self.skip_newlines()
        return VarDeclNode(name_tok.value, value)

    def parse_assign(self) -> AssignNode:
        name_tok = self.expect(TokenType.IDENTIFIER)
        self.expect(TokenType.ASSIGN)
        value = self.parse_expression()
        self.skip_newlines()
        return AssignNode(name_tok.value, value)

    def parse_fn_def(self) -> FunctionDefNode:
        self.expect(TokenType.KEYWORD, "fn")
        name_tok = self.expect(TokenType.IDENTIFIER)
        self.expect(TokenType.LPAREN)
        params = self.parse_params()
        self.expect(TokenType.RPAREN)

        # optional  -> ReturnType  hint — just skip it
        if self.check(TokenType.ARROW):
            self.advance()
            self.advance()  # skip the type identifier

        body = self.parse_block()
        return FunctionDefNode(name_tok.value, params, body)

    def parse_params(self) -> list:
        params = []
        if self.check(TokenType.RPAREN):
            return params
        params.append(self.expect(TokenType.IDENTIFIER).value)
        while self.match(TokenType.COMMA):
            # skip optional type annotation  name: type
            params.append(self.expect(TokenType.IDENTIFIER).value)
            if self.check(TokenType.COLON):
                self.advance()  # :
                self.advance()  # type name
        return params

    def parse_if(self) -> IfNode:
        self.expect(TokenType.KEYWORD, "if")
        condition  = self.parse_expression()
        then_block = self.parse_block()

        elif_clauses = []
        else_block   = None

        while self.check(TokenType.KEYWORD, "elif"):
            self.advance()
            elif_cond  = self.parse_expression()
            elif_block = self.parse_block()
            elif_clauses.append((elif_cond, elif_block))

        if self.check(TokenType.KEYWORD, "else"):
            self.advance()
            else_block = self.parse_block()

        return IfNode(condition, then_block, elif_clauses, else_block)

    def parse_while(self) -> WhileNode:
        self.expect(TokenType.KEYWORD, "while")
        condition = self.parse_expression()
        body      = self.parse_block()
        return WhileNode(condition, body)

    def parse_for(self) -> ForNode:
        self.expect(TokenType.KEYWORD, "for")
        var_tok = self.expect(TokenType.IDENTIFIER)
        self.expect(TokenType.KEYWORD, "in")
        iterable = self.parse_expression()
        body     = self.parse_block()
        return ForNode(var_tok.value, iterable, body)

    def parse_return(self) -> ReturnNode:
        self.expect(TokenType.KEYWORD, "return")
        value = self.parse_expression()
        self.skip_newlines()
        return ReturnNode(value)

    def parse_print(self) -> PrintNode:
        self.expect(TokenType.KEYWORD, "print")
        self.expect(TokenType.LPAREN)
        value = self.parse_expression()
        self.expect(TokenType.RPAREN)
        self.skip_newlines()
        return PrintNode(value)

    def parse_block(self) -> BlockNode:
        self.skip_newlines()
        self.expect(TokenType.LBRACE)
        self.skip_newlines()

        statements = []
        while not self.check(TokenType.RBRACE) and not self.check(TokenType.EOF):
            stmt = self.parse_statement()
            if stmt is not None:
                statements.append(stmt)
            self.skip_newlines()

        self.expect(TokenType.RBRACE)
        self.skip_newlines()
        return BlockNode(statements)

    # ---------------------------------------------------------------- #
    #  Expression parsing (Pratt-style precedence climbing)             #
    # ---------------------------------------------------------------- #

    def parse_expression(self):
        return self.parse_logical_or()

    def parse_logical_or(self):
        left = self.parse_logical_and()
        while self.check(TokenType.KEYWORD, "or"):
            op = self.advance().value
            right = self.parse_logical_and()
            left = BinaryOpNode(op, left, right)
        return left

    def parse_logical_and(self):
        left = self.parse_equality()
        while self.check(TokenType.KEYWORD, "and"):
            op = self.advance().value
            right = self.parse_equality()
            left = BinaryOpNode(op, left, right)
        return left

    def parse_equality(self):
        left = self.parse_comparison()
        while self.current().type in (TokenType.EQ, TokenType.NEQ):
            op = self.advance().value
            right = self.parse_comparison()
            left = BinaryOpNode(op, left, right)
        return left

    def parse_comparison(self):
        left = self.parse_addition()
        while self.current().type in (
            TokenType.LT, TokenType.GT, TokenType.LTE, TokenType.GTE
        ):
            op = self.advance().value
            right = self.parse_addition()
            left = BinaryOpNode(op, left, right)
        return left

    def parse_addition(self):
        left = self.parse_term()
        while self.current().type in (TokenType.PLUS, TokenType.MINUS):
            op = self.advance().value
            right = self.parse_term()
            left = BinaryOpNode(op, left, right)
        return left

    def parse_term(self):
        left = self.parse_power()
        while self.current().type in (
            TokenType.STAR, TokenType.SLASH, TokenType.PERCENT
        ):
            op = self.advance().value
            right = self.parse_power()
            left = BinaryOpNode(op, left, right)
        return left

    def parse_power(self):
        base = self.parse_unary()
        if self.check(TokenType.POWER):
            op = self.advance().value
            exp = self.parse_unary()   # right-associative
            return BinaryOpNode(op, base, exp)
        return base

    def parse_unary(self):
        if self.check(TokenType.KEYWORD, "not"):
            op = self.advance().value
            operand = self.parse_unary()
            return UnaryOpNode(op, operand)
        if self.check(TokenType.MINUS):
            op = self.advance().value
            operand = self.parse_unary()
            return UnaryOpNode(op, operand)
        return self.parse_primary()

    def parse_primary(self):
        tok = self.current()

        # Integer literal
        if tok.type == TokenType.INTEGER:
            self.advance()
            return IntLiteralNode(int(tok.value))

        # Float literal
        if tok.type == TokenType.FLOAT:
            self.advance()
            return FloatLiteralNode(float(tok.value))

        # String literal
        if tok.type == TokenType.STRING:
            self.advance()
            return StringLiteralNode(tok.value)

        # Boolean literal
        if tok.type == TokenType.BOOLEAN:
            self.advance()
            return BoolLiteralNode(tok.value == "true")

        # null
        if tok.type == TokenType.KEYWORD and tok.value == "null":
            self.advance()
            return NullLiteralNode()

        # Identifier — or function call
        if tok.type == TokenType.IDENTIFIER:
            self.advance()
            if self.check(TokenType.LPAREN):
                # function call
                self.advance()  # consume '('
                args = self.parse_args()
                self.expect(TokenType.RPAREN)
                return FunctionCallNode(tok.value, args)
            return IdentifierNode(tok.value)

        # Grouped expression  ( expr )
        if tok.type == TokenType.LPAREN:
            self.advance()
            expr = self.parse_expression()
            self.expect(TokenType.RPAREN)
            return expr

        # List literal  [ item, item, ... ]
        if tok.type == TokenType.LBRACKET:
            self.advance()
            elements = []
            if not self.check(TokenType.RBRACKET):
                elements.append(self.parse_expression())
                while self.match(TokenType.COMMA):
                    if self.check(TokenType.RBRACKET):
                        break
                    elements.append(self.parse_expression())
            self.expect(TokenType.RBRACKET)
            return ListLiteralNode(elements)

        raise ParseError("unexpected token in expression", tok)

    def parse_args(self) -> list:
        args = []
        if self.check(TokenType.RPAREN):
            return args
        args.append(self.parse_expression())
        while self.match(TokenType.COMMA):
            if self.check(TokenType.RPAREN):
                break
            args.append(self.parse_expression())
        return args
