from LPDLexer import lexerhelper
import inspect
import traceback
# from Automata import mealy_machine

# class MealySyntaxState(mealy_machine.MealyState):
#     def __init__(self, next_state, exception=None):
#         super().__init__(next_state)
#         self.exception=exception

class Syntax:
    def __init__(self, debug, symbol_table=None):
        self.debug = debug
        self.current_symbol = None
        if symbol_table:
            self.init_symbol_table(symbol_table)
        # self.machine = mealy_machine.MealyMachine({
        #     'start': {
        #         'sprograma': MealySyntaxState('prog_ident'),
        #         'def': MealySyntaxState('error', exception=Exception("Unexpected symbol"))
        #     },
        #     'prog_ident': {
        #         'sidentificador': MealySyntaxState('prog_semicolon')
        #     }
        # },
        # initial_state='start',
        # default_rules={

        # },
        # raw=True)

    def init_symbol_table(self, symbol_table):
        self.validate_symbol_table(symbol_table)
        self.symbol_table = symbol_table
        self.symbols = self.symbols_gen()
        return self

    def symbols_gen(self):
        for symbol in self.symbol_table:
            yield symbol
        yield {'type':None}

    def get_next_symbol(self):
        self.current_symbol = next(self.symbols)
        self.log(self.current_symbol)
        traceback.print_stack()
        print("")

    def get_ctype(self):
        return self.current_symbol['type']

    def get_clexem(self):
        return self.current_symbol['lexem']

    def read_and_assert_is(self, expected):
        self.get_next_symbol()
        if self.get_ctype() != expected:
            self.throw_unexpected_type(expected)

    def read_and_assert_is_permissive(self, expected):
        self.get_next_symbol()
        return self.current_symbol['type'] == expected

    def assert_ctype_is(self, expected):
        if self.get_ctype() != expected:
            self.throw_unexpected_type(expected)

    def assert_ctype_in(self, expected):
        if self.get_ctype() not in expected:
            self.throw_unexpected_type(expected)
        
    def run(self):
        try:
            self.read_and_assert_is('sprograma')
            self.read_and_assert_is('sidentificador')
            self.read_and_assert_is('sponto_vírgula')
            self.lpd_analisa_bloco()
            self.read_and_assert_is('sponto')
            self.log("Done!")
        except StopIteration:
            raise Exception("Program finished before formal end")

    def lpd_analisa_bloco(self):
        self.log("LPD: " + inspect.currentframe().f_code.co_name)
        self.get_next_symbol()
        self.lpd_analisa_et_variaveis()
        self.lpd_analisa_subrotinas()
        self.lpd_analisa_comandos()

    def lpd_analisa_et_variaveis(self):
        self.log("LPD: " + inspect.currentframe().f_code.co_name)
        if self.get_ctype() == 'svar':
            self.read_and_assert_is('sidentificador')
            while self.get_ctype() == 'sidentificador':
                self.lpd_analisa_variaveis()
                self.assert_ctype_is('sponto_vírgula')
                self.get_next_symbol()

    def lpd_analisa_variaveis(self):
        self.log("LPD: " + inspect.currentframe().f_code.co_name)
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
        self.lpd_analisa_tipo()

    def lpd_analisa_tipo(self):
        self.log("LPD: " + inspect.currentframe().f_code.co_name)
        self.assert_ctype_in(['sinteiro', 'sbooleano'])
        self.get_next_symbol()

    def lpd_analisa_comandos(self):
        self.log("LPD: " + inspect.currentframe().f_code.co_name)
        self.assert_ctype_is('sinício')
        self.get_next_symbol()
        self.lpd_analisa_comando_simples()
        while self.get_ctype() != 'sfim':
            self.assert_ctype_is('sponto_vírgula')
            self.get_next_symbol()
            if self.get_ctype() != 'sfim':
                self.lpd_analisa_comando_simples()
        self.get_next_symbol()

    def lpd_analisa_comando_simples(self):
        self.log("LPD: " + inspect.currentframe().f_code.co_name)
        try:
            {
                'sidentificador': self.lpd_analisa_atrib_chprocedimento,
                'sse': self.lpd_analisa_se,
                'senquanto': self.lpd_analisa_enquanto,
                'sleia': self.lpd_analisa_leia,
                'sescreva': self.lpd_analisa_escreva
            }[self.get_ctype()]()
        except KeyError:
            self.lpd_analisa_comandos()

    def lpd_analisa_atrib_chprocedimento(self):
        self.log("LPD: " + inspect.currentframe().f_code.co_name)
        self.log("analisa_atrib_chprocedimento")
        self.get_next_symbol()
        if self.get_ctype() == 'satribuição':
            self.lpd_analisa_atribuicao()
        else:
            self.lpd_analisa_chprocedimento()

    def lpd_analisa_leia(self):
        self.log("LPD: " + inspect.currentframe().f_code.co_name)
        self.read_and_assert_is('sabre_parênteses')
        self.read_and_assert_is('sidentificador')
        self.read_and_assert_is('sfecha_parênteses')
        self.get_next_symbol()

    def lpd_analisa_escreva(self):
        self.log("LPD: " + inspect.currentframe().f_code.co_name)
        self.read_and_assert_is('sabre_parênteses')
        self.read_and_assert_is('sidentificador')
        self.read_and_assert_is('sfecha_parênteses')
        self.get_next_symbol()

    def lpd_analisa_enquanto(self):
        self.log("LPD: " + inspect.currentframe().f_code.co_name)
        self.get_next_symbol()
        self.lpd_analisa_expressao()
        self.assert_ctype_is('sfaca')
        self.get_next_symbol()
        self.lpd_analisa_comando_simples()

    def lpd_analisa_se(self):
        self.log("LPD: " + inspect.currentframe().f_code.co_name)
        self.get_next_symbol()
        self.lpd_analisa_expressao()
        self.assert_ctype_is('sentao')
        self.get_next_symbol()
        self.lpd_analisa_comando_simples()
        if self.get_ctype() == 'ssenao':
            self.get_next_symbol()
            self.lpd_analisa_comando_simples()

    def lpd_analisa_subrotinas(self):
        self.log("LPD: " + inspect.currentframe().f_code.co_name)
        if self.get_ctype() in ['sprocedimento', 'sfuncao']:
            pass
        while self.get_ctype() in ['sprocedimento', 'sfuncao']:
            if self.get_ctype() == 'sprocedimento':
                self.lpd_analisa_declaracao_procedimento()
            else:
                self.lpd_analisa_declaracao_funcao()
            self.assert_ctype_is('sponto_vírgula')
            self.get_next_symbol()

    def lpd_analisa_declaracao_procedimento(self):
        self.log("LPD: " + inspect.currentframe().f_code.co_name)
        self.read_and_assert_is('sidentificador')
        self.read_and_assert_is('sponto_vírgula')

    def lpd_analisa_declaracao_funcao(self):
        self.log("LPD: " + inspect.currentframe().f_code.co_name)
        self.read_and_assert_is('sidentificador')
        self.read_and_assert_is('sdoispontos')
        self.get_next_symbol()
        self.assert_ctype_in(['sinteiro', 'sbooleano'])
        self.get_next_symbol()
        if self.get_ctype() == 'sponto_vírgula':
            self.lpd_analisa_bloco()

    def lpd_analisa_expressao(self):
        self.log("LPD: " + inspect.currentframe().f_code.co_name)
        self.lpd_analisa_expressao_simples()
        if self.get_ctype() in ['smaior', 'smaiorig', 'sig', 'smenorig', 'smenor', 'sdif']:
            self.get_next_symbol()
            self.lpd_analisa_expressao_simples()

    def lpd_analisa_expressao_simples(self):
        self.log("LPD: " + inspect.currentframe().f_code.co_name)
        if self.get_ctype() in ['smais', 'smenos']: # Weird
            self.get_next_symbol()
        self.lpd_analisa_termo()
        while self.get_ctype() in ['smais', 'smenos', 'sou']:
            self.get_next_symbol()
            self.lpd_analisa_termo()

    def lpd_analisa_termo(self):
        self.log("LPD: " + inspect.currentframe().f_code.co_name)
        self.lpd_analisa_fator()
        while self.get_ctype() in ['smult', 'sdiv', 'se']:
            self.get_next_symbol()
            self.lpd_analisa_fator()

    def lpd_analisa_fator(self):
        self.log("LPD: " + inspect.currentframe().f_code.co_name)
        if self.get_ctype() == 'sidentificador':
            self.lpd_analisa_chfuncao()
        elif self.get_ctype() == 'snúmero':
            self.get_next_symbol()
        elif self.get_ctype() == 'snao':
            self.get_next_symbol()
            self.lpd_analisa_fator()
        elif self.get_ctype() == 'sabre_parênteses':
            self.get_next_symbol()
            self.lpd_analisa_expressao()
            self.assert_ctype_is('sfecha_parênteses')
        elif self.get_clexem() in ['verdadeiro', 'falso']:
            self.get_next_symbol()
        else:
            self.throw_unexpected_type("one of {}".format(', '.join(['sidentificador', 'snúmero', 'snao', 'sabre_parênteses', 'verdadeiro', 'falso'])))

    def lpd_analisa_atribuicao(self):
        self.log("LPD: " + inspect.currentframe().f_code.co_name)
        while self.get_ctype() != "sponto_vírgula":
            self.get_next_symbol()
        pass

    def lpd_analisa_chprocedimento(self):
        self.log("LPD: " + inspect.currentframe().f_code.co_name)
        self.get_next_symbol()
        pass

    def lpd_analisa_chfuncao(self):
        self.log("LPD: " + inspect.currentframe().f_code.co_name)
        self.get_next_symbol()
        pass

    def throw_unexpected_type(self, expected, unexpected=None):
        if unexpected is None:
            unexpected = self.get_ctype()
        raise Exception("Unexpected type {} (expected {}): {}".format(unexpected, expected, self.current_symbol))

    def validate_symbol_table(self, symbol_table):
        if len(symbol_table) == 0:
            raise Exception("Invalid length for symbol table")
        _aux = [lexerhelper.special_tokens[key] for key in lexerhelper.special_tokens]
        for symbol in symbol_table:
            if symbol['type'] not in _aux + ['sidentificador', 'snúmero']:
                raise Exception("Unknown type {}".format(symbol['type']))

    def log(self, line, end='\n'):
        if (self.debug):
            print(line, end=end)

if __name__ == '__main__':
    this = Syntax(debug=True)
    this.run()