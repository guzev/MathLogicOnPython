from hw2.expression import *


def addSpaces(string):
    result = ""
    i = 0
    while i < len(string):
        if string[i].isdigit() or string[i].isalpha():
            result += string[i]
            i += 1
        elif string[i] == "-":
            result += " -> "
            i += 2
        else:
            result += " " + string[i] + " "
            i += 1

    return result

def parseExp(string):
    string = addSpaces(string)
    array = string.split()
    result, seq = parseImplication(array)
    return result


def parseImplication(seq):
    result, seq = parseDisjuction(seq)
    while len(seq) > 0 and seq[0] == "->":
        tmp, seq = parseImplication(seq[1:])
        result = Implication(result, tmp)
    return result, seq


def parseDisjuction(seq):
    result, seq = parseConjuction(seq)
    while len(seq) > 0 and seq[0] == "|":
        tmp, seq = parseConjuction(seq[1:])
        result = Disjuction(result, tmp)
    return result, seq


def parseConjuction(seq):
    result, seq = parseNot(seq)
    while len(seq) > 0 and seq[0] == "&":
        tmp, seq = parseNot(seq[1:])
        result = Conjuction(result, tmp)
    return result, seq


def parseNot(seq):
    if seq[0] == "!":
        result, seq = parseNot(seq[1:])
        result = Not(result)
    else:
        result, seq = parseUnary(seq)
    return result, seq


def parseUnary(seq):
    if seq[0] == "(":
        tmp, seq = parseImplication(seq[1:])
        return tmp, seq[1:]
    else:
        tmp = Var(seq[0])
        return tmp, seq[1:]
