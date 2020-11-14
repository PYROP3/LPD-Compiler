from .instructions import *

class LPDGenerator:
    def __init__(self, sep='\t', debug=False):
        self.debug = debug
        self.buffer = []
        self.sep = sep

    def getCodeArray(self):
        return self.buffer

    def getCode(self, end='\n'):
        return end.join(self.buffer)

    def log(self, line, end='\n'):
        if (self.debug):
            print("[LPDGenerator]: " + line, end=end)

    def getInstruction(self, opType):
        return {
            'smenos': INST_SUB,
            'smais': INST_ADD,
            'snao': INST_NEG,
            'smult': INST_MULT,
            'sdiv': INST_DIVI,
            'smaior': INST_CMA,
            'smenor': INST_CME,
            'smaiorig': INST_CMAQ,
            'smenorig': INST_CMEQ,
            'sig': INST_CEQ,
            'sdif': INST_CDIF,
            'se': INST_AND,
            'sou': INST_OR
        }[opType]

    def gera(self, funcao, label="", param1="", param2=""):
        paramString = "{},{}".format(param1, param2) if param2 != "" else param1
        newline = self.sep.join([str(x) for x in [label, funcao, paramString] if x != ""])
        self.log("Generated: [{}]".format(newline))
        self.buffer.append(newline)

    def gera_auto(self, funcao, label="", param1="", param2=""):
        instr = self.getInstruction(funcao)
        self.gera(instr, label, param1, param2)

    def gera_LDC(self, param, label=""):
        self.gera(INST_LDC, label=label, param1=param)

    def gera_LDV(self, param, label=""):
        self.gera(INST_LDV, label=label, param1=param)

    def gera_ADD(self, label=""):
        self.gera(INST_ADD, label=label)

    def gera_SUB(self, label=""):
        self.gera(INST_SUB, label=label)

    def gera_MULT(self, label=""):
        self.gera(INST_MULT, label=label)

    def gera_DIVI(self, label=""):
        self.gera(INST_DIVI, label=label)

    def gera_INV(self, label=""):
        self.gera(INST_INV, label=label)

    def gera_AND(self, label=""):
        self.gera(INST_AND, label=label)

    def gera_OR(self, label=""):
        self.gera(INST_OR, label=label)

    def gera_NEG(self, label=""):
        self.gera(INST_NEG, label=label)

    def gera_CME(self, label=""):
        self.gera(INST_CME, label=label)

    def gera_CMA(self, label=""):
        self.gera(INST_CMA, label=label)

    def gera_CEQ(self, label=""):
        self.gera(INST_CEQ, label=label)

    def gera_CDIF(self, label=""):
        self.gera(INST_CDIF, label=label)

    def gera_CMEQ(self, label=""):
        self.gera(INST_CMEQ, label=label)

    def gera_CMAQ(self, label=""):
        self.gera(INST_CMAQ, label=label)

    def gera_START(self, label=""):
        self.gera(INST_START, label=label)

    def gera_HLT(self, label=""):
        self.gera(INST_HLT, label=label)

    def gera_STR(self, param, label=""):
        self.gera(INST_STR, label=label, param1=param)
        
    def gera_JMP(self, param, label=""):
        self.gera(INST_JMP, label=label, param1=param)
        
    def gera_JMPF(self, param, label=""):
        self.gera(INST_JMPF, label=label, param1=param)
        
    def gera_NULL(self, label=""):
        self.gera(INST_NULL, label=label)

    def gera_RD(self, label=""):
        self.gera(INST_RD, label=label)

    def gera_PRN(self, label=""):
        self.gera(INST_PRN, label=label)
        
    def gera_ALLOC(self, param1, param2, label=""):
        self.gera(INST_ALLOC, label=label, param1=param1, param2=param2)
        
    def gera_DALLOC(self, param1, param2, label=""):
        self.gera(INST_DALLOC, label=label, param1=param1, param2=param2)

    def gera_CALL(self, param, label=""):
        self.gera(INST_CALL, label=label, param1=param)

    def gera_RETURN(self, label=""):
        self.gera(INST_RETURN, label=label)
