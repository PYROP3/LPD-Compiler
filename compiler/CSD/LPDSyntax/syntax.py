from ..LPDLexer import lexerhelper
from . import syntax_exceptions

class Syntax:
    def __init__(self, program_name, debug=False, symbol_table=None):
        self.debug = debug
        self.current_symbol = None
        if symbol_table:
            self.init_symbol_table(symbol_table)
        self._indent = 0
        self.program_name = program_name

    def init_symbol_table(self, symbol_table):
        self.validate_symbol_table(symbol_table)
        self.symbol_table = symbol_table
        self.symbols = self.symbols_gen()
        return self

    def symbols_gen(self):
        for symbol in self.symbol_table:
            yield symbol
        yield {'type':None, 'line':self.symbol_table[-1]['line'], 'col':self.symbol_table[-1]['col'] + len(self.symbol_table[-1]['lexeme'])}

    def get_next_symbol(self):
        self.current_symbol = next(self.symbols)
        self.log('\t' * self._indent + str(self.current_symbol))

    def get_ctype(self):
        return self.current_symbol['type']

    def get_clexem(self):
        return self.current_symbol['lexeme']

    def read_and_assert_is(self, expected):
        self.get_next_symbol()
        if self.get_ctype() != expected:
            self.throw_unexpected_type(expected)

    def assert_ctype_is(self, expected):
        if self.get_ctype() != expected:
            self.throw_unexpected_type(expected)

    def assert_ctype_in(self, expected):
        if self.get_ctype() not in expected:
            self.throw_unexpected_type(expected)

    def call(self, method):
        self._indent += 1
        self.log('\t' * self._indent + ">>> LPD: " + method.__name__)
        method()
        self.log('\t' * self._indent + "<<< LPD: " + method.__name__)
        self._indent -= 1

    def run(self):
        try:
            self.call(self.lpd_analisa_programa)
            self.log("Done!")
        except StopIteration:
            raise Exception("Program finished before formal end")
        
    def lpd_analisa_programa(self):
        self.read_and_assert_is('sprograma')
        self.read_and_assert_is('sidentificador')
        self.read_and_assert_is('sponto_vírgula')
        self.call(self.lpd_analisa_bloco)
        self.assert_ctype_is('sponto')

    def lpd_analisa_bloco(self):
        self.get_next_symbol()
        self.call(self.lpd_analisa_et_variaveis)
        self.call(self.lpd_analisa_subrotinas)
        self.call(self.lpd_analisa_comandos)

    def lpd_analisa_et_variaveis(self):
        if self.get_ctype() == 'svar':
            self.read_and_assert_is('sidentificador')
            while self.get_ctype() == 'sidentificador':
                self.call(self.lpd_analisa_variaveis)
                self.assert_ctype_is('sponto_vírgula')
                self.get_next_symbol()

    def lpd_analisa_variaveis(self):
        while (True):
            self.assert_ctype_is('sidentificador')
            self.get_next_symbol()
            self.assert_ctype_in(['svírgula', 'sdoispontos'])
            if self.get_ctype() == 'svírgula':
                self.get_next_symbol()
                if self.get_ctype() == 'sdoispontos':
                    self.throw_unexpected_type('~sdoispontos')
            if self.get_ctype() == 'sdoispontos':
                break
        self.get_next_symbol()
        self.call(self.lpd_analisa_tipo)

    def lpd_analisa_tipo(self):
        self.assert_ctype_in(['sinteiro', 'sbooleano'])
        self.get_next_symbol()

    def lpd_analisa_comandos(self):
        self.assert_ctype_is('sinício')
        self.get_next_symbol()
        self.call(self.lpd_analisa_comando_simples)
        while self.get_ctype() != 'sfim':
            self.assert_ctype_is('sponto_vírgula')
            self.get_next_symbol()
            if self.get_ctype() != 'sfim':
                self.call(self.lpd_analisa_comando_simples)
        self.get_next_symbol()

    def lpd_analisa_comando_simples(self):
        try:
            self.call({
                'sidentificador': self.lpd_analisa_atrib_chprocedimento,
                'sse': self.lpd_analisa_se,
                'senquanto': self.lpd_analisa_enquanto,
                'sleia': self.lpd_analisa_leia,
                'sescreva': self.lpd_analisa_escreva
            }[self.get_ctype()])
        except KeyError:
            self.call(self.lpd_analisa_comandos)

    def lpd_analisa_atrib_chprocedimento(self):
        self.get_next_symbol()
        if self.get_ctype() == 'satribuição':
            self.call(self.lpd_analisa_atribuicao)
        else:
            self.call(self.lpd_analisa_chprocedimento)

    def lpd_analisa_leia(self):
        self.read_and_assert_is('sabre_parênteses')
        self.read_and_assert_is('sidentificador')
        self.read_and_assert_is('sfecha_parênteses')
        self.get_next_symbol()

    def lpd_analisa_escreva(self):
        self.read_and_assert_is('sabre_parênteses')
        self.read_and_assert_is('sidentificador')
        self.read_and_assert_is('sfecha_parênteses')
        self.get_next_symbol()

    def lpd_analisa_enquanto(self):
        self.get_next_symbol()
        self.call(self.lpd_analisa_expressao)
        self.assert_ctype_is('sfaca')
        self.get_next_symbol()
        self.call(self.lpd_analisa_comando_simples)

    def lpd_analisa_se(self):
        self.get_next_symbol()
        self.call(self.lpd_analisa_expressao)
        self.assert_ctype_is('sentao')
        self.get_next_symbol()
        self.call(self.lpd_analisa_comando_simples)
        if self.get_ctype() == 'ssenao':
            self.get_next_symbol()
            self.call(self.lpd_analisa_comando_simples)

    def lpd_analisa_subrotinas(self):
        if self.get_ctype() in ['sprocedimento', 'sfuncao']:
            pass
        while self.get_ctype() in ['sprocedimento', 'sfuncao']:
            if self.get_ctype() == 'sprocedimento':
                self.call(self.lpd_analisa_declaracao_procedimento)
            else:
                self.call(self.lpd_analisa_declaracao_funcao)
            self.assert_ctype_is('sponto_vírgula')
            self.get_next_symbol()

    def lpd_analisa_declaracao_procedimento(self):
        self.read_and_assert_is('sidentificador')
        self.read_and_assert_is('sponto_vírgula')

    def lpd_analisa_declaracao_funcao(self):
        self.read_and_assert_is('sidentificador')
        self.read_and_assert_is('sdoispontos')
        self.get_next_symbol()
        self.assert_ctype_in(['sinteiro', 'sbooleano'])
        self.get_next_symbol()
        if self.get_ctype() == 'sponto_vírgula':
            self.call(self.lpd_analisa_bloco)

    def lpd_analisa_expressao(self):
        self.call(self.lpd_analisa_expressao_simples)
        if self.get_ctype() in ['smaior', 'smaiorig', 'sig', 'smenorig', 'smenor', 'sdif']:
            self.get_next_symbol()
            self.call(self.lpd_analisa_expressao_simples)

    def lpd_analisa_expressao_simples(self):
        if self.get_ctype() in ['smais', 'smenos']:
            self.get_next_symbol()
        self.call(self.lpd_analisa_termo)
        while self.get_ctype() in ['smais', 'smenos', 'sou']:
            self.get_next_symbol()
            self.call(self.lpd_analisa_termo)

    def lpd_analisa_termo(self):
        self.call(self.lpd_analisa_fator)
        while self.get_ctype() in ['smult', 'sdiv', 'se']:
            self.get_next_symbol()
            self.call(self.lpd_analisa_fator)

    def lpd_analisa_fator(self):
        if self.get_ctype() == 'sidentificador':
            self.call(self.lpd_analisa_chfuncao)
        elif self.get_ctype() == 'snúmero':
            self.get_next_symbol()
        elif self.get_ctype() == 'snao':
            self.get_next_symbol()
            self.call(self.lpd_analisa_fator)
        elif self.get_ctype() == 'sabre_parênteses':
            self.get_next_symbol()
            self.call(self.lpd_analisa_expressao)
            self.assert_ctype_is('sfecha_parênteses')
            self.get_next_symbol()
        elif self.get_clexem() in ['verdadeiro', 'falso']:
            self.get_next_symbol()
        else:
            self.throw_unexpected_type("one of {}".format(', '.join(['sidentificador', 'snúmero', 'snao', 'sabre_parênteses', 'verdadeiro', 'falso'])))

    def lpd_analisa_atribuicao(self):
        while self.get_ctype() != "sponto_vírgula":
            self.get_next_symbol()
        pass

    def lpd_analisa_chprocedimento(self):
        self.get_next_symbol()
        pass

    def lpd_analisa_chfuncao(self):
        self.get_next_symbol()
        pass

    def throw_unexpected_type(self, expected, unexpected=None):
        if unexpected is None:
            unexpected = self.get_ctype()
        if 'line' not in self.current_symbol or 'col' not in self.current_symbol:
            self.current_symbol['line'] = '?'
            self.current_symbol['col'] = '?'
        raise syntax_exceptions.UnexpectedTypeException(self.program_name, self.current_symbol['line'], self.current_symbol['col'], expected, unexpected)

    def validate_symbol_table(self, symbol_table):
        if len(symbol_table) == 0:
            raise Exception("Invalid length for symbol table")
        _aux = [lexerhelper.special_tokens[key] for key in lexerhelper.special_tokens] + ['sidentificador', 'snúmero']
        for symbol in symbol_table:
            if symbol['type'] not in _aux:
                raise Exception("Unknown type {}".format(symbol['type']))

    def log(self, line, end='\n'):
        if (self.debug):
            print(line, end=end)

if __name__ == '__main__':
    this = Syntax("", debug=True)
    this.run()