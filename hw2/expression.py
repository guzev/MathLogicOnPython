mod = (10 ** 9) + 5


class Expression(object):
    hash = 0

    def __hash__(self):
        return self.hash

    def __eq__(self, other):
        return self.__hash__() == other.__hash__()


class Unary(Expression):
    def __init__(self, value):
        self.val = value


class Var(Unary):
    def __init__(self, value):
        self.hash = value.__hash__() % mod
        super().__init__(value)

    def __str__(self):
        return self.val

    def rehash(self):
        self.hash = self.val.__hash__()

    def eval(self, dictionary):
        return dictionary[self.val]


class Not(Unary):
    name = "!"

    def __init__(self, value):
        super().__init__(value)
        self.rehash()

    def __str__(self):
        return "(!" + self.val.__str__() + ")"

    def rehash(self):
        self.hash = (3 * self.val.__hash__() ** 2 + 7 * self.name.__hash__()) % mod

    def eval(self, dictionary):
        return not self.val.eval(dictionary)


class Any(Unary):
    name = "@"

    def __init__(self, var, value):
        super().__init__(value)
        self.var = var
        self.rehash()

    def __str__(self):
        return "(@" + self.var.__str__() + self.val.__str__() + ")"

    def rehash(self):
        self.hash = (17 * self.var.__hash__() ** 3 + 3 * self.val.__hash__() ** 2 + 7 * self.name.__hash__()) % mod


class Exists(Unary):
    name = "?"

    def __init__(self, var, value):
        super().__init__(value)
        self.var = var
        self.rehash()

    def __str__(self):
        return "(?" + self.var.__str__() + self.val.__str__() + ")"

    def rehash(self):
        self.hash = (17 * self.var.__hash__() ** 3 + 3 * self.val.__hash__() ** 2 + 7 * self.name.__hash__()) % mod


class Predicate(Unary):
    def __init__(self, name, values):
        self.name = name
        super().__init__(values)
        self.rehash()

    def __str__(self):
        if len(self.val) == 0:
            return self.name
        result = self.name + "("
        for i in range(len(self.val)):
            if i == len(self.val) - 1:
                result += self.val[i].__str__() + ")"
            else:
                result += self.val[i].__str__() + ","
        return result

    def rehash(self):
        self.hash = self.name.__hash__() % mod
        for e in self.val:
            self.hash *= 37
            self.hash += e.__hash__()


class Next(Unary):
    name = "'"

    def __init__(self, value):
        super().__init__(value)
        self.rehash()

    def __str__(self):
        return self.val.__str__() + self.name

    def rehash(self):
        self.hash = (self.val.__hash__() * 31 + self.name.__hash__()) % mod


class Binary(Expression):
    def __init__(self, left, right):
        self.left = left
        self.right = right
        self.rehash()

    def __str__(self):
        return "(" + self.left.__str__() + self.name + self.right.__str__() + ")"

    def rehash(self):
        self.hash = (3 * self.name.__hash__() + 11 * self.left.__hash__()**3 + 23 * self.right.__hash__()**4) % mod

    def calc(self, left, right):
        raise NotImplementedError

    def eval(self, dictionary):
        return self.calc(self.left.eval(dictionary), self.right.eval(dictionary))


class Implication(Binary):
    name = "->"

    def __init__(self, left, right):
        super().__init__(left, right)

    def calc(self, left, right):
        return (not left) or right


class Conjuction(Binary):
    name = "&"

    def __init__(self, left, right):
        super().__init__(left, right)

    def calc(self, left, right):
        return left and right


class Disjuction(Binary):
    name = "|"

    def __init__(self, left, right):
        super().__init__(left, right)

    def calc(self, left, right):
        return left or right


class Equals(Binary):
    name = "="

    def __init__(self, left, right):
        super().__init__(left, right)


class Sum(Binary):
    name = "+"

    def __init__(self, left, right):
        super().__init__(left, right)


class Mul(Binary):
    name = "*"

    def __init__(self, left, right):
        super().__init__(left, right)


def match(exp, axiom, dictionary):
    if type(axiom) is Var:
        if axiom in dictionary:
            return dictionary[axiom] == exp
        else:
            dictionary[axiom] = exp
            return True
    elif type(exp) is type(axiom):
        if isinstance(axiom, Unary):
            return match(exp.val, axiom.val, dictionary)
        else:
            sub = match(exp.left, axiom.left, dictionary)
            if sub:
                sub = match(exp.right, axiom.right, dictionary)

            return sub
    else:
        return False

def is_axiom(exp, checking_axiom):
    return match(exp, checking_axiom, {})


def get_variables(exp, dictionary: dict):
    if type(exp) is Var:
        if exp.val not in dictionary:
            dictionary[exp.val] = len(dictionary)
    elif isinstance(exp, Unary):
        get_variables(exp.val, dictionary)
    else:
        get_variables(exp.left, dictionary)
        get_variables(exp.right, dictionary)


def get_free_variables(exp, dictionary: dict, result: set):
    if type(exp) is Var:
        if exp not in dictionary.keys():
            result.add(exp.val)
    elif type(exp) is Predicate:
        for e in exp.val:
            get_free_variables(e, dictionary, result)
    elif type(exp) is Any or type(exp) is Exists:
        if exp.var in dictionary.keys():
            dictionary[exp.var] += 1
        else:
            dictionary[exp.var] = 1
        get_free_variables(exp.val,dictionary, result)
        dictionary[exp.var] -= 1
        if dictionary[exp.var] == 0:
            dictionary.pop(exp.var)
    elif isinstance(exp, Unary):
        get_free_variables(exp.val, dictionary, result)
    else:
        get_free_variables(exp.left, dictionary, result)
        get_free_variables(exp.right, dictionary, result)
    return result

def new_match(template, exp, locked : set, dictionary):
    if type(template) is Var:
        if template in locked:
            return template == exp
        else:
            if template in dictionary:
                return dictionary[template] == exp
            else:
                dictionary[template] = exp
                return True
    elif type(template) is type(exp):
        if type(template) is Any or type(template) is Exists:
            locked.add(template.var)
            result = new_match(template.val, exp.val, locked, dictionary)
            locked.remove(template.var)
            return result
        elif type(template) is Predicate:
            if len(template.val) != len(exp.val):
                return False
            for i in range(template.val):
                if not new_match(template.val[i], exp.val[i], locked, dictionary):
                    return False
            return True
        elif isinstance(template, Unary):
            return new_match(template.val, exp.val, locked, dictionary)
        else:
            if not new_match(template.left, exp.left, locked, dictionary):
                return False
            return new_match(template.right, exp.right, locked, dictionary)
    else:
        return False


def is_tautology(exp):
    temp = dict()
    get_variables(exp, temp)
    dictionary = dict()
    for e in temp:
        dictionary[temp[e]] = e

    for bits in range(0, 2 ** len(dictionary)):
        temp = dict()
        for j in range(0, len(dictionary)):
            if bits & (2 ** j) == 0:
                temp[dictionary[j]] = False
            else:
                temp[dictionary[j]] = True

        if not exp.eval(temp):
            return temp

    return dict()
