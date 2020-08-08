class VM:
    def __init__(self):
        self._registers = { 'i':0, 's':-1 }
        self._stack = []
        self._prog = []
        self._state = False
        self.__exec = {
            'LDC': self._LDC,
            'LDV': self._LDV,
            'ADD': self._ADD,
            'SUB': self._SUB,
            'MULT': self._MULT,
            'DIVI': self._DIVI,
            'INV': self._INV,
            'AND': self._AND,
            'OR': self._OR,
            'NEG': self._NEG,
            'CME': self._CME,
            'CMA': self._CMA,
            'CEQ': self._CEQ,
            'CDIF': self._CDIF,
            'CMEQ': self._CMEQ,
            'CMAQ': self._CMAQ,
            'START': self._START,
            'HLT': self._HLT,
            'STR': self._STR,
            'JMP': self._JMP,
            'JMPF': self._JMPF,
            'NULL': self._NULL,
            'RD': self._RD,
            'PRN': self._PRN,
            'ALLOC': self._ALLOC,
            'DALLOC': self._DALLOC,
            'CALL': self._CALL,
            'RETURN': self._RETURN
        }
        self._implicitIncI = True
        self._debugMode = False
        
    def _incI(self):
        self._registers['i'] += 1
        
    def _decI(self):
        self._registers['i'] -= 1
        
    def _incS(self):
        self._registers['s'] += 1
        
    def _decS(self):
        self._registers['s'] -= 1
        
    def _getI(self):
        return self._registers['i']
        
    def _getS(self):
        return self._registers['s']
    
    def _parseInt(self, x):
        return int(x)
    
    def _parseTuple(self, x, d=0):
        a, b = x.split(',')
        return int(a), int(b)
    
    def _parseLabel(self, x): # TODO implement this mess
        for idx, line in enumerate(self._prog):
            if x == line[0]:
                return idx
        return 0
    
    def _push(self, x, d=0):
        try:
            self._stack[self._getS()+d] = x
        except IndexError:
            self._stack.append(x)
    
    def _pushAt(self, x, p):
        self._stack[p] = x
        
    def _fetch(self, x):
        try:
            return self._stack[x]
        except IndexError:
            return 0
    
    def _pop(self, d=0):
        return self._stack[self._getS()+d]
    
    def _true(self, d=0):
        return self._pop(d=d) == 1
    
    def _false(self, d=0):
        return self._pop(d=d) == 0
    
    def _dbg(self, txt):
        if self._debugMode:
            print(txt)
        
    def _LDC(self, x):
        self._incS()
        self._push(self._parseInt(x))
        
    def _LDV(self, x):
        self._incS()
        self._push(self._fetch(self._parseInt(x)))
        
    def _ADD(self, x):
        self._push(self._pop(d=-1) + self._pop(), d=-1)
        self._decS()
        
    def _SUB(self, x):
        self._push(self._pop(d=-1) - self._pop(), d=-1)
        self._decS()
        
    def _MULT(self, x):
        self._push(self._pop(d=-1) * self._pop(), d=-1)
        self._decS()
        
    def _DIVI(self, x):
        self._push(self._pop(d=-1) // self._pop(), d=-1)
        self._decS()
        
    def _INV(self, x):
        self._push(-1 * self._pop())
        
    def _AND(self, x):
        self._push(1 if self._true() and self._true(d=-1) else 0, d=-1)
        self._decS()
        
    def _OR(self, x):
        self._push(1 if self._true() or self._true(d=-1) else 0, d=-1)
        self._decS()
        
    def _NEG(self, x):
        self._push(1 - self._pop())
        
    def _CME(self, x):
        self._push(1 if self._pop(d=-1) < self._pop() else 0, d=-1)
        self._decS()
        
    def _CMA(self, x):
        self._push(1 if self._pop(d=-1) > self._pop() else 0, d=-1)
        self._decS()
        
    def _CEQ(self, x):
        self._push(1 if self._pop(d=-1) == self._pop() else 0, d=-1)
        self._decS()
        
    def _CDIF(self, x):
        self._push(1 if self._pop(d=-1) != self._pop() else 0, d=-1)
        self._decS()
        
    def _CMEQ(self, x):
        self._push(1 if self._pop(d=-1) <= self._pop() else 0, d=-1)
        self._decS()
        
    def _CMAQ(self, x):
        self._push(1 if self._pop(d=-1) >= self._pop() else 0, d=-1)
        self._decS()
        
    def _START(self, x):
        self._registers['s'] = -1
        
    def _HLT(self, x):
        self._state = False
        
    def _STR(self, x):
        self._stack[self._parseInt(x)] = self._pop()
        self._decS()
        
    def _JMP(self, x):
        self._registers['i'] = self._parseLabel(x)
        self._implicitIncI = False
        
    def _JMPF(self, x):
        self._registers['i'] = self._parseLabel(x) if self._false() else self._registers['i'] + 1
        self._decS()
        self._implicitIncI = False
        
    def _NULL(self, x):
        pass
    
    def _RD(self, x):
        self._incS()
        self._push(int(input(">"))) #TODO add input logic
        
    def _PRN(self, x):
        print(self._pop()) #TODO add output logic
        self._decS()
        
    def _ALLOC(self, x):
        m, n = self._parseTuple(x)
        for k in range(n):
            self._incS()
            self._push(self._fetch(m + k))
        
    def _DALLOC(self, x):
        m, n = self._parseTuple(x)
        for k in range(n-1, -1, -1):
            self._dbg("Dealoccing {} ({})".format(self._pop(), k))
            self._pushAt(self._pop(), m + k)
            self._decS()
            
    def _CALL(self, x):
        self._incS()
        self._push(self._getI() + 1)
        self._registers['i'] = self._parseLabel(x)
        self._implicitIncI = False
        
    def _RETURN(self, x):
        self._registers['i'] = self._pop()
        self._decS()
        self._implicitIncI = False
        
    def toStackString(self):
        return "["+",".join([str(item) for item in self._stack[:self._registers['s']+1]])+"]"
        
    def toString(self):
        return "VM [i={}, s={}]".format(self._registers['i'], self._registers['s']) + self.toStackString()
        
    def loadProgram(self, program):
        self._prog = program
        
    def execute(self):
        self._state = True
        while self._state:
            self.step()
            
    def step(self):
        if not self._state:
            return 0
        cmd = self._prog[self._getI()]
        aux = cmd[2] if len(cmd) > 2 else None
        args = cmd[1] if len(cmd) > 1 else None
        cmd = cmd[0]
        self._dbg("CMD={}, ARGS={}, AUX={}".format(cmd, args, aux))
        if cmd in self.__exec:
            self.__exec[cmd](args)
        else:
            self._dbg("CMD {} not found in list".format(cmd))
            self.__exec[args](aux)
        if self._implicitIncI:
            self._incI()
        self._implicitIncI = True