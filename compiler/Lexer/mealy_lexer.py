from . import lexerhelper
from . import lexer_exceptions
from . import mealy_machine

class MealyState:
    def __init__(self, next_state, reset_token=False, append_char=False, wrap_token=None, exception=None):
        self.next_state = next_state
        self.reset_token = reset_token
        self.append_char = append_char
        self.wrap_token = wrap_token
        self.exception = exception

class MealyLexer:
    def __init__(self, program_name, debug=False):
        self.program_name = program_name
        self.working_program = open(self.program_name, 'r', encoding='utf-8').read()
        self.original_program = self.working_program.split('\n')
        self.working_program = list(self.working_program)
        self.parsed_tokens = []
        self.debug = debug
        self.state = 'normal'
        self.last_char = ''
        self.current_token = ''
        self.current_line = 0
        self.current_col = 0
        self.machine = mealy_machine.MealyMachine({ #mealy_machine[state][character]
            'normal': {
                '{': MealyState('in_bracket'),
                '/': MealyState('in_c-like_start'),
                '0123456789': MealyState('digit', reset_token=True, append_char=True),
                'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZí': MealyState('word', reset_token=True, append_char=True),
                ':': MealyState('attribution', reset_token=True, append_char=True),
                '+-*': MealyState('arithmetic', reset_token=True, append_char=True),
                '!<>=': MealyState('rel_op', reset_token=True, append_char=True),
                ';': MealyState('semicolon', reset_token=True, append_char=True, wrap_token='auto'),
                ' \n\t': MealyState('normal'),
                '(': MealyState('open_paren', reset_token=True, append_char=True, wrap_token='auto'),
                ')': MealyState('close_paren', reset_token=True, append_char=True, wrap_token='auto'),
            },
            'in_bracket': {
                '}': MealyState('normal'),
                'def': MealyState('in_bracket')
            },
            'in_c-like_start': {
                '*': MealyState('in_c-like'),
                'def': MealyState('error', exception=(lexer_exceptions.InvalidSymbolException, "/{char}"))
            },
            'in_c-like': {
                '*': MealyState('in_c-like_end'),
                'def': MealyState('in_c-like')
            },
            'in_c-like_end': {
                '/': MealyState('normal'),
                'def': MealyState('in_c-like')
            },
            'digit': {
                '0123456789': MealyState('digit', append_char=True),
                ' \n\t': MealyState('normal', wrap_token='snúmero'),
                ';': MealyState('semicolon', wrap_token='snúmero'),
                '+-*': MealyState('arithmetic', wrap_token='snúmero'),
                '(': MealyState('open_paren', wrap_token='auto'),
                ')': MealyState('close_paren', wrap_token='auto'),
                '.': MealyState('normal',  wrap_token='auto')
            },
            'word': {
                'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZí_0123456789': MealyState('word', append_char=True),
                ':': MealyState('attribution', wrap_token='auto'),
                '+-*': MealyState('arithmetic', wrap_token='auto'),
                '!<>=': MealyState('rel_op', wrap_token='auto'),
                ';': MealyState('semicolon', wrap_token='auto'),
                ' \n\t': MealyState('normal', wrap_token='auto'),
                ',': MealyState('colon', wrap_token='auto'),
                '(': MealyState('open_paren', wrap_token='auto'),
                ')': MealyState('close_paren', wrap_token='auto'),
                '.': MealyState('normal', wrap_token='auto')
            },
            'semicolon': {
                '{': MealyState('in_bracket', wrap_token='auto'),
                '/': MealyState('in_c-like_start', wrap_token='auto'),
                '0123456789': MealyState('digit', wrap_token='auto'),
                'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZí': MealyState('word', wrap_token='auto'),
                ':': MealyState('attribution', wrap_token='auto'),
                '+-*': MealyState('arithmetic', wrap_token='auto'),
                '!<>=': MealyState('rel_op', wrap_token='auto'),
                ';': MealyState('semicolon', wrap_token='auto'),
                ' \n\t': MealyState('normal', wrap_token='auto'),
                ',': MealyState('colon', wrap_token='auto')
            },
            'attribution': {
                '=': MealyState('normal', append_char=True, wrap_token='auto'),
                ' \n\t': MealyState('normal', wrap_token='auto'),
                'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZí': MealyState('word', wrap_token='auto'),
            },
            'colon': {
                '{': MealyState('in_bracket', wrap_token='auto'),
                '/': MealyState('in_c-like_start', wrap_token='auto'),
                '0123456789': MealyState('digit', wrap_token='auto'),
                'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZí': MealyState('word', wrap_token='auto'),
                ':': MealyState('attribution', wrap_token='auto'),
                '+-*': MealyState('arithmetic', wrap_token='auto'),
                '!<>=': MealyState('rel_op', wrap_token='auto'),
                ';': MealyState('semicolon', wrap_token='auto'),
                ' \n\t': MealyState('normal', wrap_token='auto'),
                ',': MealyState('colon', wrap_token='auto')
            },
            'rel_op': {
                '=': MealyState('normal', append_char=True, wrap_token='auto'),
                '{': MealyState('in_bracket', wrap_token='auto'),
                '/': MealyState('in_c-like_start', wrap_token='auto'),
                '0123456789': MealyState('digit', wrap_token='auto'),
                'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZí': MealyState('word', wrap_token='auto'),
                ':': MealyState('attribution', wrap_token='auto'),
                '+-*': MealyState('arithmetic', wrap_token='auto'),
                '!<>': MealyState('rel_op', wrap_token='auto'),
                ';': MealyState('semicolon', wrap_token='auto'),
                ' \n\t': MealyState('normal', wrap_token='auto'),
                ',': MealyState('colon', wrap_token='auto')
            },
            'arithmetic': {
                '0123456789': MealyState('digit', wrap_token='auto'),
                'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZí': MealyState('word', wrap_token='auto'),
                ' \n\t': MealyState('normal', wrap_token='auto'),
                '(': MealyState('open_paren', wrap_token='auto'),
                ')': MealyState('close_paren', wrap_token='auto'),
            },
            'open_paren': {
                '{': MealyState('in_bracket', wrap_token='auto'),
                '/': MealyState('in_c-like_start', wrap_token='auto'),
                '0123456789': MealyState('digit', wrap_token='auto'),
                'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZí': MealyState('word', wrap_token='auto'),
                ':': MealyState('attribution', wrap_token='auto'),
                '+-*': MealyState('arithmetic', wrap_token='auto'),
                '!<>=': MealyState('rel_op', wrap_token='auto'),
                ';': MealyState('semicolon', wrap_token='auto'),
                ' \n\t': MealyState('normal', wrap_token='auto'),
                ',': MealyState('colon', wrap_token='auto')
            },
            'close_paren': {
                '{': MealyState('in_bracket', wrap_token='auto'),
                '/': MealyState('in_c-like_start', wrap_token='auto'),
                '0123456789': MealyState('digit', wrap_token='auto'),
                'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZí': MealyState('word', wrap_token='auto'),
                ':': MealyState('attribution', wrap_token='auto'),
                '+-*': MealyState('arithmetic', wrap_token='auto'),
                '!<>=': MealyState('rel_op', wrap_token='auto'),
                ';': MealyState('semicolon', wrap_token='auto'),
                ' \n\t': MealyState('normal', wrap_token='auto'),
                ',': MealyState('colon', wrap_token='auto')
            },
        },
        default_rules={
                '{': MealyState('in_bracket', wrap_token='auto'),
                '/': MealyState('in_c-like_start', wrap_token='auto'),
                '0123456789': MealyState('digit', wrap_token='auto'),
                'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZí': MealyState('word', wrap_token='auto'),
                ':': MealyState('attribution', wrap_token='auto'),
                '+-*': MealyState('arithmetic', wrap_token='auto'),
                '!<>=': MealyState('rel_op', wrap_token='auto'),
                ';': MealyState('semicolon', wrap_token='auto'),
                ' \n\t.': MealyState('normal', wrap_token='auto'),
                ',': MealyState('colon', wrap_token='auto'),
                '(': MealyState('open_paren', wrap_token='auto'),
                ')': MealyState('close_paren', wrap_token='auto')
        }).getMachine()

    def exec(self):
        _state = 'normal'
        for char in self.working_program + [None]:
            _mealy_state = self.machine[_state]

            if char is not None:
                if char not in _mealy_state and 'def' not in _mealy_state:
                    raise Exception("{}:{}:{}: Invalid char '{}'".format(self.program_name, self.current_line, self.current_col, char))

                _next = _mealy_state[char if char in _mealy_state else 'def']
                self.log("Current {}, read {}, next {}".format(_state, char, _next.next_state))

                if _next.exception:
                    _ex, _txt = _next.exception
                    raise _ex(self.program_name, "", self.current_line, self.current_col, _txt.format(char=char))

                if _next.reset_token:
                    self.current_token = ''

                if _next.append_char:
                    self.current_token += char

            # Add token to list if its finished
            if _next.wrap_token:
                self.log("Wrapping token [{}]".format(self.current_token))
                if _next.wrap_token == 'auto':
                    if self.current_token in lexerhelper.special_tokens:
                        self.appendToken(lexerhelper.special_tokens[self.current_token])
                    else:
                        self.appendToken('sidentificador')
                else:
                    self.appendToken(_next.wrap_token)
                #print(self.parsed_tokens)
                self.current_token = char
            
            # Update coords
            if char == '\n':
                self.current_col = 0
                self.current_line += 1
            else:
                self.current_col += 1

            # Update state
            self.last_char = char
            _state = _next.next_state

        if _state != 'normal':
            raise Exception("EOF before finish: " + _state)
        #self.print_lexem_table()

    def appendToken(self, _type):
        self.parsed_tokens.append({
            'lexeme': self.current_token, 
            'type': _type,
            'line': self.current_line, 
            'col': self.current_col - len(self.current_token)})

    def print_lexem_table(self):
        assert self.parsed_tokens is not None, "Parser has not been executed"
        print("{:20s}|{:15s}|{:6s}|{:6s}".format("Tipo", "Lexema", "Linha", "Coluna"))
        print("-" * 20 + "+" + "-" * 15 + "+" + "-" * 6 + "+" + "-" * 6)
        for token in self.parsed_tokens:
            print("{:20s}|{:15s}|{:6d}|{:6d}".format(token['type'], token['lexeme'], token['line'], token['col']))

    def log(self, line, end='\n'):
        if (self.debug):
            print(line, end=end)

if __name__ == '__main__':
    lexer = MealyLexer("prog1.lpd", debug=True)
    lexer.exec()