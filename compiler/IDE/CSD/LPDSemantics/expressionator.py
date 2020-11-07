from . import semantics_exceptions

PREC_PAREN = -1
PREC_OP_UNARY = 6
PREC_NOT = 6
PREC_MULT = 5
PREC_DIV = 5
PREC_MINUS = 4
PREC_PLUS = 4
PREC_RELATIONAL = 3
PREC_COMPARE = 2
PREC_AND = 1
PREC_OR = 0

operatorRequirements = {
    'smenos': ('inteiro', 'inteiro'),
    'smais': ('inteiro', 'inteiro'),
    'snao': ('booleano', 'booleano'),
    'smult': ('inteiro', 'inteiro'),
    'sdiv': ('inteiro', 'inteiro'),
    'smaior': ('inteiro', 'booleano'),
    'smenor': ('inteiro', 'booleano'),
    'smaiorig': ('inteiro', 'booleano'),
    'smenorig': ('inteiro', 'booleano'),
    'sig': ('inteiro', 'booleano'),
    'sdif': ('inteiro', 'booleano'),
    'se': ('booleano', 'booleano'),
    'sou': ('booleano', 'booleano')
}

def getPrecedence(opType, isUnary=False):
    if isUnary:
        return PREC_OP_UNARY
    return {
    'smenos': PREC_MINUS,
    'smais': PREC_PLUS,
    'snao': PREC_NOT,
    'smult': PREC_MULT,
    'sdiv': PREC_DIV,
    'smaior': PREC_RELATIONAL,
    'smenor': PREC_RELATIONAL,
    'smaiorig': PREC_RELATIONAL,
    'smenorig': PREC_RELATIONAL,
    'sig': PREC_COMPARE,
    'sdif': PREC_COMPARE,
    'se': PREC_AND,
    'sou': PREC_OR
    }[opType]

class StackDatagram:
    def __init__(self, op, precedence=None, isUnary=False):
        self.op = op
        self.precedence = precedence
        self.isUnary = isUnary
    
    def __str__(self):
        return "Operation {} (P{}; isUnary={})".format(self.op, self.precedence, self.isUnary)

    def __repr__(self):
        return "Operation {} (P{}; isUnary={})".format(self.op, self.precedence, self.isUnary)

class PostfixDatagram:
    def __init__(self, item, isOperand, isUnary, opType=None):
        self.item = item
        self.isOperand = isOperand
        self.isUnary = isUnary
        self.opType = opType

    def __str__(self):
        return "Datagram {} (isOperand={}; isUnary={}; opType={})".format(self.item, self.isOperand, self.isUnary, self.opType)
        
    def __repr__(self):
        return "Datagram {} (isOperand={}; isUnary={}; opType={})".format(self.item, self.isOperand, self.isUnary, self.opType)

class Expressionator:
    def __init__(self, program_name, debug=False):
        self.program_name = program_name
        self._opStack = []
        self._postfix = []
        self._debug = debug
        self._finished = False

    def log(self, msg, end='\n'):
        if self._debug:
            print("[Expressionator]: " + msg, end=end)

    def exhibit(self):
        self.log("OP stack = [{}]".format(self._opStack))
        self.log("Postfix  = [{}]".format(self._postfix))

    def insertOperand(self, operand, opType):
        self.log("Inserting operand {} (type {})".format(operand, opType))
        self._postfix.append(PostfixDatagram(operand, True, False, opType))
        self.exhibit()

    def openParenthesis(self):
        self.log("Opening parenthesis")
        self._opStack.append(StackDatagram('(', PREC_PAREN))

    def closeParenthesis(self):
        self.log("Closing parenthesis")
        _top = self._opStack.pop()
        while _top.op != '(':
            self._postfix.append(PostfixDatagram(_top.op, False, _top.isUnary))
            _top = self._opStack.pop()

    def register(self, item, precedence=None, isUnary=False):
        if precedence is None:
            precedence = getPrecedence(item['type'], isUnary=isUnary)
        self.log("Inserting operation {} - precedence {} (isUnary = {})".format(item, precedence, isUnary))
        while len(self._opStack) > 0 and self._opStack[-1].precedence >= precedence:
            _a = self._opStack.pop()
            self._postfix.append(PostfixDatagram(_a.op, False, _a.isUnary))
        self._opStack.append(StackDatagram(item, precedence, isUnary))
        self.exhibit()

    def finish(self):
        self.log("Wrapping up postfix ({} elements left)".format(len(self._opStack)))
        while len(self._opStack) > 0:
            _a = self._opStack.pop()
            self._postfix.append(PostfixDatagram(_a.op, False, _a.isUnary))
        self._finished = True

    def validate(self):
        if not self._finished:
            self.log("Warning: validating before finished, finishing automatically...")
            self.finish()
        _aux = self._postfix[:]
        self.log("Starting validation for postfix={}".format(_aux))
        atual = 0
        while len(_aux) > 1:
            while _aux[atual].isOperand:
                atual += 1
            self.log("Validating operation {}".format(_aux[atual]))
            tipoEsperado, tipoRetorno = operatorRequirements[_aux[atual].item['type']]
            self.log("Returns {}".format(tipoRetorno))
            if _aux[atual].isUnary:
                self.log("Requires 1 {}".format(tipoEsperado))
                self.validateType(tipoEsperado, _aux[atual - 1], _aux[atual])
                _aux.pop(atual)
                _aux.pop(atual-1)
                atual -= 1
                _aux.insert(atual, PostfixDatagram(None, True, False, tipoRetorno))
            else:
                self.log("Requires 2 {}".format(tipoEsperado))
                self.validateType(tipoEsperado, _aux[atual - 1], _aux[atual])
                self.validateType(tipoEsperado, _aux[atual - 2], _aux[atual])
                _aux.pop(atual)
                _aux.pop(atual-1)
                _aux.pop(atual-2)
                atual -= 2
                _aux.insert(atual, PostfixDatagram(None, True, False, tipoRetorno))
            self.log("Aux is now {}".format(_aux))
        return _aux[0].opType

    def getPostfix(self):
        return self._postfix

    def validateType(self, expected, got, anchor):
        if expected != got.opType:
            raise semantics_exceptions.MismatchedTypeException(
                self.program_name,
                anchor.item['line'],
                anchor.item['col'],
                expected,
                got.opType)
