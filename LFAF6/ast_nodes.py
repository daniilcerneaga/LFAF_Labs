"""
ast_nodes.py — AST node definitions for TinyLang

Each node represents one syntactic construct.
All nodes inherit from ASTNode which provides a basic __repr__
and a pretty-print helper for visualising the tree.
"""


# ------------------------------------------------------------------ #
#  Base node                                                           #
# ------------------------------------------------------------------ #

class ASTNode:
    """Base class for every AST node."""

    def pretty(self, indent: int = 0) -> str:
        """
        Return a human-readable, indented representation of the subtree.
        Child classes override _children() to expose their sub-nodes.
        """
        pad = "  " * indent
        name = self.__class__.__name__
        attrs = self._attrs()
        children = self._children()

        header = f"{pad}{name}"
        if attrs:
            header += "  " + "  ".join(f"{k}={v!r}" for k, v in attrs.items())

        lines = [header]
        for label, child in children:
            if child is None:
                continue
            if isinstance(child, list):
                lines.append(f"{pad}  [{label}]")
                for item in child:
                    if isinstance(item, ASTNode):
                        lines.append(item.pretty(indent + 2))
                    else:
                        lines.append("  " * (indent + 2) + repr(item))
            elif isinstance(child, ASTNode):
                lines.append(f"{pad}  {label}:")
                lines.append(child.pretty(indent + 2))
            else:
                lines.append(f"{pad}  {label}: {child!r}")

        return "\n".join(lines)

    # Override in subclasses to expose scalar attributes
    def _attrs(self) -> dict:
        return {}

    # Override in subclasses to expose child nodes / lists
    def _children(self) -> list:
        return []


# ------------------------------------------------------------------ #
#  Program                                                             #
# ------------------------------------------------------------------ #

class ProgramNode(ASTNode):
    """Root of every TinyLang program — a list of statements."""

    def __init__(self, statements: list):
        self.statements = statements

    def _children(self):
        return [("statements", self.statements)]


# ------------------------------------------------------------------ #
#  Statements                                                          #
# ------------------------------------------------------------------ #

class VarDeclNode(ASTNode):
    """let <name> = <expr>"""

    def __init__(self, name: str, value):
        self.name  = name
        self.value = value

    def _attrs(self):
        return {"name": self.name}

    def _children(self):
        return [("value", self.value)]


class AssignNode(ASTNode):
    """<name> = <expr>  (re-assignment, no 'let')"""

    def __init__(self, name: str, value):
        self.name  = name
        self.value = value

    def _attrs(self):
        return {"name": self.name}

    def _children(self):
        return [("value", self.value)]


class ReturnNode(ASTNode):
    """return <expr>"""

    def __init__(self, value):
        self.value = value

    def _children(self):
        return [("value", self.value)]


class PrintNode(ASTNode):
    """print(<expr>)"""

    def __init__(self, value):
        self.value = value

    def _children(self):
        return [("value", self.value)]


class BreakNode(ASTNode):
    """break"""


class ContinueNode(ASTNode):
    """continue"""


class BlockNode(ASTNode):
    """A { ... } block containing a list of statements."""

    def __init__(self, statements: list):
        self.statements = statements

    def _children(self):
        return [("statements", self.statements)]


class IfNode(ASTNode):
    """
    if <condition> { <then_block> }
    [elif <condition> { <block> }]*
    [else { <else_block> }]
    """

    def __init__(self, condition, then_block, elif_clauses: list, else_block):
        self.condition    = condition
        self.then_block   = then_block
        self.elif_clauses = elif_clauses   # list of (condition, block)
        self.else_block   = else_block

    def _children(self):
        children = [
            ("condition",  self.condition),
            ("then_block", self.then_block),
        ]
        for i, (cond, blk) in enumerate(self.elif_clauses):
            children.append((f"elif_{i}_cond",  cond))
            children.append((f"elif_{i}_block", blk))
        if self.else_block:
            children.append(("else_block", self.else_block))
        return children


class WhileNode(ASTNode):
    """while <condition> { <body> }"""

    def __init__(self, condition, body):
        self.condition = condition
        self.body      = body

    def _children(self):
        return [("condition", self.condition), ("body", self.body)]


class ForNode(ASTNode):
    """for <var> in <iterable> { <body> }"""

    def __init__(self, var: str, iterable, body):
        self.var      = var
        self.iterable = iterable
        self.body     = body

    def _attrs(self):
        return {"var": self.var}

    def _children(self):
        return [("iterable", self.iterable), ("body", self.body)]


class FunctionDefNode(ASTNode):
    """fn <name>(<params>) { <body> }"""

    def __init__(self, name: str, params: list, body):
        self.name   = name
        self.params = params   # list of str
        self.body   = body

    def _attrs(self):
        return {"name": self.name, "params": self.params}

    def _children(self):
        return [("body", self.body)]


# ------------------------------------------------------------------ #
#  Expressions                                                         #
# ------------------------------------------------------------------ #

class BinaryOpNode(ASTNode):
    """<left> <op> <right>"""

    def __init__(self, op: str, left, right):
        self.op    = op
        self.left  = left
        self.right = right

    def _attrs(self):
        return {"op": self.op}

    def _children(self):
        return [("left", self.left), ("right", self.right)]


class UnaryOpNode(ASTNode):
    """<op> <operand>   (e.g. not x, -y)"""

    def __init__(self, op: str, operand):
        self.op      = op
        self.operand = operand

    def _attrs(self):
        return {"op": self.op}

    def _children(self):
        return [("operand", self.operand)]


class FunctionCallNode(ASTNode):
    """<name>(<args>)"""

    def __init__(self, name: str, args: list):
        self.name = name
        self.args = args

    def _attrs(self):
        return {"name": self.name}

    def _children(self):
        return [("args", self.args)]


class ListLiteralNode(ASTNode):
    """[<item>, <item>, ...]"""

    def __init__(self, elements: list):
        self.elements = elements

    def _children(self):
        return [("elements", self.elements)]


# ------------------------------------------------------------------ #
#  Literals / leaves                                                   #
# ------------------------------------------------------------------ #

class IntLiteralNode(ASTNode):
    def __init__(self, value: int):
        self.value = value

    def _attrs(self):
        return {"value": self.value}


class FloatLiteralNode(ASTNode):
    def __init__(self, value: float):
        self.value = value

    def _attrs(self):
        return {"value": self.value}


class StringLiteralNode(ASTNode):
    def __init__(self, value: str):
        self.value = value

    def _attrs(self):
        return {"value": self.value}


class BoolLiteralNode(ASTNode):
    def __init__(self, value: bool):
        self.value = value

    def _attrs(self):
        return {"value": self.value}


class NullLiteralNode(ASTNode):
    def _attrs(self):
        return {"value": "null"}


class IdentifierNode(ASTNode):
    def __init__(self, name: str):
        self.name = name

    def _attrs(self):
        return {"name": self.name}
