

TYPE_VAR = "var"
TYPE_FUNC = "func"
TYPE_PROC = "proc"
TYPE_PROG = "prog"

class SymbolDatagram:
    def __init__(self, lexem, stype, level=None, rotule=None, sret=None):
        self._sLexem = lexem
        self._sType = stype
        self._sLevel = level
        self._sRot = rotule
        self._sRetType = sret

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

    def setRetType(self, sret):
        self._sRetType = sret

    def getRetType(self):
        return self._sRetType

class SymbolTable:
    def __init__(self, debug=False):
        self._table = []
        self._lvl = 0
        self._debug = debug

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

    def insert(self, lexem, stype, rotule):
        self.log("Inserting lexem {} (type={}, rotule={})".format(lexem, stype, rotule))
        self._table.append(SymbolDatagram(lexem, stype, self._lvl, rotule))

    def pop(self):
        _pop = []
        while self._table[-1].isType("var"):
            _pop.append(self._table.pop())
        return _pop

    def get(self, index):
        return self._table[index]

    def _find(self, matcher):
        for i in reversed(range(len(self._table))):
            if matcher(self._table[i]):
                return i
        return None

    def _findCurrent(self, matcher):
        _aux = [symb for symb in self._table if symb.getLevel() == self._lvl]
        for i in reversed(range(len(_aux))):
            if matcher(_aux[i]):
                return i
        return None

    def pesquisa_tabela(self, lexema, nivel=None):
        return self._find(lambda symb: symb.isLexem(lexema))

    def pesquisa_declvar(self, lexema):
        return self._find(lambda symb: symb.isVar() and symb.isLexem(lexema))

    def pesquisa_declvarfunc(self, lexema):
        return self._find(lambda symb: (symb.isVar() or symb.isFunc()) and symb.isLexem(lexema))

    def pesquisa_declproc(self, lexema):
        return self._find(lambda symb: symb.isProc() and symb.isLexem(lexema))

    def pesquisa_declfunc(self, lexema):
        return self._find(lambda symb: symb.isFunc() and symb.isLexem(lexema))

    def pesquisa_duplicvar(self, lexema):
        return self._findCurrent(lambda symb: symb.isVar() and symb.isLexem(lexema))

    def coloca_tipo_tabela(self, tipo):
        self.log("Setting type {}".format(tipo))
        _i = -1
        while abs(_i) < len(self._table) and self._table[_i].getRetType() == None:
            self.log("Setting type {} for {}:{}".format(tipo, _i, self._table[_i]))
            self._table[_i].setRetType(tipo)
            _i -= 1

    def setLastRetType(self, tipo):
        self.log("Setting type {} for {}:{}".format(tipo, -1, self._table[-1]))
        self._table[-1].setRetType(tipo)