from ..LPDLexer import lexerhelper
from ..LPDSemantics import expressionator
from ..LPDSemantics import symbol_table
from ..LPDSemantics import semantics_exceptions
from . import syntax_exceptions

class Syntax:
    def __init__(self, program_name, debug=False, lexer=None):
        self.debug = debug
        self.current_symbol = None
        self.previous_symbol = None
        self._indent = 0
        self.program_name = program_name
        self.lexer = lexer
        self.symbols = self.lexer.tokenGenerator()
        self.symbol_table = symbol_table.SymbolTable(debug=debug)
        self.expressionator = None

    def get_next_symbol(self):
        try:
            self.previous_symbol = self.current_symbol
            self.current_symbol = next(self.symbols)
            self.log('\t' * self._indent + str(self.current_symbol))
        except StopIteration:
            raise syntax_exceptions.NoMoreTokensException(
                self.program_name,
                self.current_symbol['line'],
                self.current_symbol['col'])

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
        self.call(self.lpd_analisa_programa)
        self.log("Done!")

    def lpd_analisa_programa(self):
        self.read_and_assert_is('sprograma')
        self.read_and_assert_is('sidentificador')
        self.symbol_table.insert(self.get_clexem(), symbol_table.TYPE_PROG, None)
        self.read_and_assert_is('sponto_vírgula')
        self.call(self.lpd_analisa_bloco)
        self.assert_ctype_is('sponto')
        try:
            self.get_next_symbol()
            raise syntax_exceptions.UnexpectedTokenException(
                self.program_name, 
                self.current_symbol['line'], 
                self.current_symbol['col'], 
                self.current_symbol)
        except syntax_exceptions.NoMoreTokensException:
            pass # Expected

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
            self.tabela_pesquisa_duplicvar()
            self.symbol_table.insert(self.get_clexem(), symbol_table.TYPE_VAR, None)
            self.get_next_symbol()
            self.assert_ctype_in(['svírgula', 'sdoispontos'])
            if self.get_ctype() == 'svírgula':
                self.get_next_symbol()
                if self.get_ctype() == 'sdoispontos':
                    self.throw_expected_anything_else('sdoispontos')
            if self.get_ctype() == 'sdoispontos':
                break
        self.get_next_symbol()
        self.call(self.lpd_analisa_tipo)

    def lpd_analisa_tipo(self):
        self.assert_ctype_in(['sinteiro', 'sbooleano'])
        self.symbol_table.coloca_tipo_tabela({'sinteiro':'inteiro', 'sbooleano':'booleano'}[self.get_ctype()])
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
        _aux = {
                'sidentificador': self.lpd_analisa_atrib_chprocedimento,
                'sse': self.lpd_analisa_se,
                'senquanto': self.lpd_analisa_enquanto,
                'sleia': self.lpd_analisa_leia,
                'sescreva': self.lpd_analisa_escreva
            }
        _type = self.get_ctype()

        if _type in _aux:
            self.call(_aux[_type])
        else:
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
        self.tabela_pesquisa_declvar()
        self.read_and_assert_is('sfecha_parênteses')
        self.get_next_symbol()

    def lpd_analisa_escreva(self):
        self.read_and_assert_is('sabre_parênteses')
        self.read_and_assert_is('sidentificador')
        if self.symbol_table.pesquisa_declvarfunc(self.get_clexem()) == None:
            raise semantics_exceptions.UndeclaredSymbolException(
                self.program_name,
                self.current_symbol['line'],
                self.current_symbol['col'],
                self.current_symbol['lexeme'])
        self.read_and_assert_is('sfecha_parênteses')
        self.get_next_symbol()

    def lpd_analisa_enquanto(self):
        self.get_next_symbol()
        self.call(self.lpd_analisa_expressao_primer)
        self.validate_conditional()
        self.assert_ctype_is('sfaca')
        self.get_next_symbol()
        self.call(self.lpd_analisa_comando_simples)

    def lpd_analisa_se(self):
        self.get_next_symbol()
        self.call(self.lpd_analisa_expressao_primer)
        self.validate_conditional()
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
        self.symbol_table.inLvl()
        self.tabela_pesquisa_declproc()
        self.symbol_table.insert(self.get_clexem(), symbol_table.TYPE_PROC, None)
        self.read_and_assert_is('sponto_vírgula')
        self.call(self.lpd_analisa_bloco)
        self.symbol_table.outLvl()

    def lpd_analisa_declaracao_funcao(self):
        self.read_and_assert_is('sidentificador')
        self.symbol_table.inLvl()
        self.tabela_pesquisa_declfunc()
        self.symbol_table.insert(self.get_clexem(), symbol_table.TYPE_FUNC, None)
        self.read_and_assert_is('sdoispontos')
        self.get_next_symbol()
        self.assert_ctype_in(['sinteiro', 'sbooleano'])
        self.symbol_table.setLastRetType({'sinteiro':'inteiro', 'sbooleano':'booleano'}[self.get_ctype()])
        self.get_next_symbol()
        if self.get_ctype() == 'sponto_vírgula':
            self.call(self.lpd_analisa_bloco)
        self.symbol_table.outLvl()

    def lpd_analisa_expressao_primer(self):
        self.expressionator = expressionator.Expressionator(self.program_name, debug=self.debug)
        self.call(self.lpd_analisa_expressao)

    def lpd_analisa_expressao(self):
        self.call(self.lpd_analisa_expressao_simples)
        if self.get_ctype() in ['smaior', 'smaiorig', 'sig', 'smenorig', 'smenor', 'sdif']:
            self.expressionator.register(self.current_symbol)
            self.get_next_symbol()
            self.call(self.lpd_analisa_expressao_simples)

    def lpd_analisa_expressao_simples(self):
        if self.get_ctype() in ['smais', 'smenos']:
            self.expressionator.register(self.current_symbol, isUnary=True)
            self.get_next_symbol()
        self.call(self.lpd_analisa_termo)
        while self.get_ctype() in ['smais', 'smenos', 'sou']:
            self.expressionator.register(self.current_symbol)
            self.get_next_symbol()
            self.call(self.lpd_analisa_termo)

    def lpd_analisa_termo(self):
        self.call(self.lpd_analisa_fator)
        while self.get_ctype() in ['smult', 'sdiv', 'se']:
            self.expressionator.register(self.current_symbol)
            self.get_next_symbol()
            self.call(self.lpd_analisa_fator)

    def lpd_analisa_fator(self):
        if self.get_ctype() == 'sidentificador':
            _index = self.symbol_table.pesquisa_tabela(self.get_clexem())
            _symbol = self.symbol_table.get(_index)
            _type = _symbol.getRetType()
            self.expressionator.insertOperand(self.current_symbol, _type)
            if _symbol.isFunc():
                self.call(self.lpd_analisa_chfuncao)
            else:
                self.get_next_symbol()
        elif self.get_ctype() == 'snúmero':
            self.expressionator.insertOperand(self.current_symbol, 'inteiro')
            self.get_next_symbol()
        elif self.get_ctype() == 'snao':
            self.expressionator.register(self.current_symbol, isUnary=True)
            self.get_next_symbol()
            self.call(self.lpd_analisa_fator)
        elif self.get_ctype() == 'sabre_parênteses':
            self.expressionator.openParenthesis()
            self.get_next_symbol()
            self.call(self.lpd_analisa_expressao)
            self.assert_ctype_is('sfecha_parênteses')
            self.expressionator.closeParenthesis()
            self.get_next_symbol()
        elif self.get_clexem() in ['verdadeiro', 'falso']:
            self.expressionator.insertOperand(self.current_symbol, 'booleano')
            self.get_next_symbol()
        else:
            self.throw_unexpected_type(['sidentificador', 'snúmero', 'snao', 'sabre_parênteses', 'verdadeiro', 'falso'])

    def lpd_analisa_atribuicao(self):
        _aux_symbol = self.previous_symbol
        _index = self.symbol_table.pesquisa_tabela(_aux_symbol['lexeme'])
        if _index == None:
            raise semantics_exceptions.UndeclaredSymbolException(
                self.program_name,
                _aux_symbol['line'],
                _aux_symbol['col'],
                _aux_symbol['lexeme'])
        _expectedReturnType = self.symbol_table.get(_index).getRetType()
        self.get_next_symbol()
        self.call(self.lpd_analisa_expressao_primer)
        _actualReturnType = self.expressionator.validate()
        if _actualReturnType != _expectedReturnType:
            raise semantics_exceptions.MismatchedAttributionException(
                self.program_name,
                _aux_symbol['line'],
                _aux_symbol['col'],
                _expectedReturnType, 
                _actualReturnType)

    def lpd_analisa_chprocedimento(self):
        pass

    def lpd_analisa_chfuncao(self):
        self.assert_ctype_is('sidentificador')
        self.get_next_symbol()

    def tabela_pesquisa_duplicvar(self):            
        if self.symbol_table.pesquisa_duplicvar(self.get_clexem()) != None:
            raise semantics_exceptions.DuplicatedVariableException(
                self.program_name,
                self.current_symbol['line'],
                self.current_symbol['col'],
                self.current_symbol['lexeme'])

    def tabela_pesquisa_declvar(self):
        if self.symbol_table.pesquisa_declvar(self.get_clexem()) == None:
            raise semantics_exceptions.UndeclaredSymbolException(
                self.program_name,
                self.current_symbol['line'],
                self.current_symbol['col'],
                self.current_symbol['lexeme'])

    def tabela_pesquisa_declproc(self):
        if self.symbol_table.pesquisa_declproc(self.get_clexem()) != None:
            raise semantics_exceptions.DuplicatedProcedureException(
                self.program_name,
                self.current_symbol['line'],
                self.current_symbol['col'],
                self.current_symbol['lexeme'])

    def tabela_pesquisa_declfunc(self):
        if self.symbol_table.pesquisa_declfunc(self.get_clexem()) != None:
            raise semantics_exceptions.DuplicatedFunctionException(
                self.program_name,
                self.current_symbol['line'],
                self.current_symbol['col'],
                self.current_symbol['lexeme'])

    def validate_conditional(self):
        _ret = self.expressionator.validate()
        if _ret != 'booleano':
            raise semantics_exceptions.InvalidConditionalException(
                self.program_name,
                self.current_symbol['line'],
                self.current_symbol['col'])

    def throw_unexpected_type(self, expected, unexpected=None):
        if unexpected is None:
            unexpected = self.get_ctype()

        if 'line' not in self.current_symbol or 'col' not in self.current_symbol:
            self.current_symbol['line'] = '?'
            self.current_symbol['col'] = '?'

        if type(expected) == type('a'):
            expected = [expected]

        _rev = {lexerhelper.special_tokens[key]:key for key in lexerhelper.special_tokens}
        _rev.update({
            'sidentificador': 'identificador',
            'snúmero': 'número'
        })

        _expected = ["'" + (_rev[key] if key in _rev else key) + "'"  for key in expected]
        _unexpected = "'" + _rev[unexpected] + "'" if unexpected in _rev else "'" + self.current_symbol['lexeme'] + "'"
        self.log("Throwing with expected={}, unexpected={}".format(_expected, _unexpected))

        raise syntax_exceptions.UnexpectedTypeException(
            self.program_name, 
            self.current_symbol['line'], 
            self.current_symbol['col'], 
            _expected, 
            _unexpected)

    def throw_expected_anything_else(self, but):
        raise syntax_exceptions.ExpectedAnythingElseException(
            self.program_name, 
            self.current_symbol['line'], 
            self.current_symbol['col'], 
            but)

    # def validate_symbol_table(self, symbol_table):
    #     if len(symbol_table) == 0:
    #         raise Exception("Invalid length for symbol table")
    #     _aux = [lexerhelper.special_tokens[key] for key in lexerhelper.special_tokens] + ['sidentificador', 'snúmero']
    #     for symbol in symbol_table:
    #         if symbol['type'] not in _aux:
    #             raise Exception("Unknown type {}".format(symbol['type']))

    def log(self, line, end='\n'):
        if (self.debug):
            print(line, end=end)

if __name__ == '__main__':
    this = Syntax("", debug=True)
    this.run()