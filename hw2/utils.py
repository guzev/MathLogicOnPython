from hw2.formal_parser import *
from hw2.parser import *

axioms = [
    "A -> (B -> A)",
    "(A -> B) -> (A -> B -> C) -> (A -> C)",
    "A -> B -> A & B",
    "A & B -> A",
    "A & B -> B",
    "A -> A | B",
    "A -> B | A",
    "(A -> B) -> (C -> B) -> (A | C -> B)",
    "(A -> B) -> (A -> !B) -> !A",
    "!!A -> A"
]

formal_axioms = [
    "a=b->a'=b'",
    "a=b->a=c->b=c",
    "a'=b'->a=b",
    "!(a'=0)",
    "a+b'=(a+b)'",
    "a+0=a",
    "a*0=0",
    "a*b'=a*b+a"
]

axiomsExp = [parseExp(string) for string in axioms]
expression_parser = FormalParser()
formalAxioms = [expression_parser.parseExpr(string) for string in formal_axioms]


def is_any_axiom(expr):
    for i in range(len(axiomsExp)):
        if is_axiom(expr, axiomsExp[i]):
            return True

    return False


def subtract(expr, values):
    if type(expr) is Var:
        return expr
    elif type(expr) is Predicate:
        if expr.name in values:
            return values[expr.name]
        for i in range(len(expr.val)):
            expr[i] = subtract(expr.val[i], values)
    elif isinstance(expr, Unary):
        expr.val = subtract(expr.val, values)
    else:
        expr.left = subtract(expr.left, values)
        expr.right = subtract(expr.right, values)

    if (type(expr) is Any or type(expr) is Exists) and expr.var.val == "x":
        expr.var = values["x"].val

    expr.rehash()
    return expr


def createExpr(parser : FormalParser, string, values):
    return subtract(parser.parseExpr(string), values)

def free_subtract(template, exp, var, locked: dict, dictionary):
    if type(template) is Var:
        if template != var:
            return template == exp
        if template.val in locked:
            return template == exp
        else:
            if template in dictionary:
                return dictionary[template] == exp
            else:
                tmp = set()
                get_free_variables(exp, dict(), tmp)
                if len(tmp.intersection(locked)) != 0:
                    return False
                dictionary[template] = exp
                return True
    elif type(template) is type(exp):
        if type(template) is Any or type(template) is Exists:
            if template.var.val not in locked:
                locked[template.var.val] = 1
            else:
                locked[template.var.val] += 1
            result = free_subtract(template.val, exp.val, var, locked, dictionary)
            locked[template.var.val] -= 1
            if locked[template.var.val] == 0:
                locked.pop(template.var.val, None)
            return result
        elif type(template) is Predicate:
            if len(template.val) != len(exp.val):
                return False
            for i in range(len(template.val)):
                if not free_subtract(template.val[i], exp.val[i], var, locked, dictionary):
                    return False
            return True
        elif isinstance(template, Unary):
            return free_subtract(template.val, exp.val, var, locked, dictionary)
        else:
            if not free_subtract(template.left, exp.left, var, locked, dictionary):
                return False
            return free_subtract(template.right, exp.right, var, locked, dictionary)
    else:
        return False

def is_axiom_any(expr):
    if type(expr) is not Implication or type(expr.left) is not Any:
        return False
    return free_subtract(expr.left.val, expr.right, expr.left.var, dict(), dict())


def is_axiom_exists(expr):
    if type(expr) is not Implication or type(expr.right) is not Exists:
        return False
    return free_subtract(expr.right.val, expr.left, expr.right.var, dict(), dict())


def is_any_formal_axiom(expr: object) -> object:
    for axiom in formalAxioms:
        if new_match(axiom, expr, set(), dict()):
            return True
    if is_axiom_any(expr) or is_axiom_exists(expr):
        return True
    return False
