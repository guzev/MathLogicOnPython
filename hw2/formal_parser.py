from  hw2.expression import *

class FormalParser:
    def __init__(self):
        self.string = ""
        self.index = 0

    def parseExpr(self, string):
        self.index = 0
        self.string = string
        return self.parseImplication()

    def parse(self):
        if self.index >= len(self.string):
            return None
        return self.parseImplication()

    def readVarName(self):
        j = self.index
        while j < len(self.string) and (
            self.string[j].isdigit() or (self.string[j].isalpha() and self.string[j].islower())):
            j += 1
        result = self.string[self.index:j]
        self.index = j
        return result

    def readPredicateName(self):
        j = self.index
        if not (self.string[j].isalpha() and self.string[j].isupper()):
            return ""
        while j < len(self.string) and (
            self.string[j].isdigit() or (self.string[j].isalpha() and self.string[j].isupper())):
            j += 1
        result = self.string[self.index:j]
        self.index = j
        return result

    def parseImplication(self):
        result = self.parseDisjuction()
        if self.index < len(self.string) and self.string[self.index] == '-':
            self.index += 2
            tmp = self.parseImplication()
            return Implication(result, tmp)
        else:
            return result

    def parseDisjuction(self):
        result = self.parseConjuction()
        while self.index < len(self.string) and self.string[self.index] == '|':
            self.index += 1
            tmp = self.parseConjuction()
            result = Disjuction(result, tmp)
        return result

    def parseConjuction(self):
        result = self.parseUnary()
        while self.index < len(self.string) and self.string[self.index] == '&':
            self.index += 1
            tmp = self.parseUnary()
            result = Conjuction(result, tmp)
        return result

    def parseUnary(self):
        if self.string[self.index] == '!':
            self.index += 1
            tmp = self.parseUnary()
            return Not(tmp)
        elif self.string[self.index] == '@' or self.string[self.index] == '?':
            symbol = self.string[self.index]
            self.index += 1
            word = self.readVarName()
            tmp = self.parseUnary()
            if symbol == '@':
                return Any(Var(word), tmp)
            else:
                return Exists(Var(word), tmp)

        result = self.parsePredicate()
        if not (result is None):
            return result

        if self.index < len(self.string) and self.string[self.index] == '(':
            self.index += 1
            result = self.parseImplication()
            self.index += 1
            return result

        temp = self.readVarName()
        return Var(temp)

    def parsePredicate(self):
        word = self.readPredicateName()
        if word != "":
            args = self.parseArguments()
            return Predicate(word, args)
        else:
            save = self.index
            result = self.parseTerm()
            if self.index >= len(self.string) or self.string[self.index] != '=':
                self.index = save
                return None
            self.index += 1
            return Equals(result, self.parseTerm())

    def parseArguments(self):
        result = list()
        if self.index >= len(self.string) or self.string[self.index] != '(':
            return result
        self.index += 1
        result.append(self.parseTerm())
        while self.index < len(self.string) and self.string[self.index] != ')':
            self.index += 1
            result.append(self.parseTerm())
        self.index += 1
        return result

    def parseTerm(self):
        result = self.parseSum()
        while self.index < len(self.string) and self.string[self.index] == '+':
            self.index += 1
            tmp = self.parseSum()
            result = Sum(result, tmp)

        return result

    def parseSum(self):
        result = self.parseMul()
        while self.index < len(self.string) and self.string[self.index] == '*':
            self.index += 1
            tmp = self.parseMul()
            result = Mul(result, tmp)

        return result

    def parseMul(self):
        result = None
        if self.index < len(self.string) and self.string[self.index] == '(':
            self.index += 1
            result = self.parseTerm()
            self.index += 1
            return self.parseNext(result)
        word = self.readVarName()
        if self.index < len(self.string) and self.string[self.index] == '(':
            values = self.parseArguments()
            result = Predicate(word, values)
        else:
            result = Var(word)
        return self.parseNext(result)

    def parseNext(self, val):
        while self.index < len(self.string) and self.string[self.index] == '\'':
            self.index += 1
            val = Next(val)
        return val
