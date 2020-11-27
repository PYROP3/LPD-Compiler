TYPE_VAR = "var"
TYPE_FUNC = "func"
TYPE_PROC = "proc"
TYPE_PROG = "prog"

class SymbolDatagram:
    def __init__(self, lexem, stype, token, level=None, rotule=None, sret=None):
        self._sLexem = lexem
        self._sType = stype
        self._sLevel = level
        self._sRot = rotule
        self._sRetType = sret
        self._sToken = token

    def isLexem(self, lexem):
        return self._sLexem == lexem

    def isType(self, sType):
        return self._sType == sType

    def isVar(self):
        return self.isType(TYPE_VAR)

    def isProc(self):
        return self.isType(TYPE_PROC)

    def isFunc(self):
        return self.isType(TYPE_FUNC)

    def getLevel(self):
        return self._sLevel

    def setRotule(self, srot):
        self._sRot = srot

    def getRotule(self):
        return self._sRot

    def getType(self):
        return self._sType

    def setRetType(self, sret):
        self._sRetType = sret

    def getRetType(self):
        return self._sRetType

    def getToken(self):
        return self._sToken

    def __str__(self):
        return "[{}] {} (level={}, rotule={}, ret={})".format(self._sType, self._sLexem, self._sLevel, self._sRot, self._sRetType)
        
    def __repr__(self):
        return "[{}] {} (level={}, rotule={}, ret={})".format(self._sType, self._sLexem, self._sLevel, self._sRot, self._sRetType)

class SymbolTable:
    def __init__(self, debug=False):
        self._table = []
        self._lvl = 0
        self._debug = debug

    def __str__(self):
        return "[Symbol Table]:\n\t{}".format('\n\t'.join(self._table))

    def __repr__(self):
        return "[Symbol Table (lvl={}, debug={})]:\n\t{}".format(self._lvl, self._debug, '\n\t'.join([str(item) for item in self._table]))

    def log(self, msg, end='\n'):
        if self._debug:
            print("[SymbolTable]: " + msg, end=end)

    def inLvl(self):
        self.log("In level (currently {})".format(self._lvl))
        self._lvl += 1

    def outLvl(self):
        self.log("Out level (currently {})".format(self._lvl))
        assert self._lvl > 0, "Level is already 0"
        self._lvl -= 1
        return self.pop()

    def insert(self, lexem, stype, rotule, token):
        self.log("Inserting lexem {} (type={}, rotule={}, level={})".format(lexem, stype, rotule, self._lvl))
        self._table.append(SymbolDatagram(lexem, stype, token, self._lvl, rotule))

    def pop(self):
        _pop = []
        # Remove everything above current level (if any)
        while self._table[-1].getLevel() > self._lvl + 1:
            _pop.append(self._table.pop())
        # Remove old variables
        while self._table[-1].isType(TYPE_VAR):
            _pop.append(self._table.pop())
        self.log("Popping {} from symbol table".format(_pop))
        return _pop

    def get(self, index):
        return self._table[index]

    def register_rotules(self, rotules):
        for _i in range(-1, -1*(len(rotules) + 1), -1):
            self.log("Setting rotule {} for item {}".format(rotules[_i], self._table[_i]))
            self._table[_i].setRotule(rotules[_i])

    def _find(self, matcher):
        for i in reversed(range(len(self._table))):
            if matcher(self._table[i]):
                return i
        return None

    def _findCurrent(self, matcher):
        _aux = [symb for symb in self._table if symb.getLevel() == self._lvl]
        for i in reversed(range(len(_aux))):
            if matcher(_aux[i]):
                self.log("Matcher success for {}".format(_aux[i]))
                return i
        return None

    def pesquisa_tabela(self, lexema, nivel=None):
        return self._find(lambda symb: symb.isLexem(lexema))

    def pesquisa_existe_var(self, lexema):
        return self._find(lambda symb: symb.isVar() and symb.isLexem(lexema))

    def pesquisa_existe_var_ou_func(self, lexema):
        return self._find(lambda symb: (symb.isVar() or symb.isFunc()) and symb.isLexem(lexema))

    def pesquisa_existe_proc(self, lexema):
        return self._find(lambda symb: symb.isProc() and symb.isLexem(lexema))

    def pesquisa_existe_var_nivel(self, lexema, nivel=None):
        nivel = nivel or self._lvl
        return self._find(lambda symb: symb.isLexem(lexema) and symb.getLevel() == nivel)

    def coloca_tipo_tabela(self, tipo):
        self.log("Setting type {}".format(tipo))
        _i = -1
        while abs(_i) < len(self._table) and self._table[_i].getRetType() == None and (self._table[_i].isFunc() or self._table[_i].isVar()):
            self.log("Setting type {} for {}:{}".format(tipo, _i, self._table[_i]))
            self._table[_i].setRetType(tipo)
            _i -= 1

    def setLastRetType(self, tipo):
        self.log("Setting type {} for {}:{}".format(tipo, -1, self._table[-1]))
        self._table[-1].setRetType(tipo)