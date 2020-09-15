import re
from . import lexerhelper
from . import lexer_exceptions
from . import mealy_machine

class MealyState:
    def __init__(self, next_state, reset_token=False, append_char=False, wrap_token=False, exception=None):
        self.next_state = next_state
        self.reset_token = reset_token
        self.append_char = append_char
        self.wrap_token = wrap_token
        self.exception = exception

class MealyLexer:
    def __init__(self, program_name, debug=False):
        self.program_name = program_name
        _f = open(self.program_name, 'r', encoding='utf-8')
        self.working_program = _f.read()
        _f.close()
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
                '+-*;.,()': MealyState('symbol', reset_token=True, append_char=True),
                '!<>=': MealyState('rel_op', reset_token=True, append_char=True),
                ' \n\t': MealyState('normal'),
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
                '0123456789': MealyState('digit', append_char=True)
            },
            'word': {
                'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZí_0123456789': MealyState('word', append_char=True)
            },
            'attribution': {
                '=': MealyState('normal', append_char=True, wrap_token=True)
            },
            'rel_op': {
                '=': MealyState('normal', append_char=True, wrap_token=True)
            },
            'symbol': { }
        },
        default_rules={
                '{': MealyState('in_bracket', wrap_token=True),
                '/': MealyState('in_c-like_start', wrap_token=True),
                '0123456789': MealyState('digit', wrap_token=True),
                'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZí': MealyState('word', wrap_token=True),
                ':': MealyState('attribution', wrap_token=True),
                '+-*;.,()': MealyState('symbol', wrap_token=True),
                '!<>=': MealyState('rel_op', wrap_token=True),
                ' \n\t.': MealyState('normal', wrap_token=True),
        }).getMachine()
        self.identifier_prog = re.compile(lexerhelper.format_identifier)
        self.number_prog = re.compile(lexerhelper.format_number)

    def run(self):
        _state = 'normal'
        for char in self.working_program + [' ']:
            _mealy_state = self.machine[_state]

            if char is not None:
                if char not in _mealy_state and 'def' not in _mealy_state:
                    raise lexer_exceptions.InvalidTokenException(
                        self.program_name, 
                        self.original_program[self.current_line], 
                        self.current_line, 
                        self.current_col, 
                        char)

                _next = _mealy_state[char if char in _mealy_state else 'def']
                self.log("Current {}, read {}, next {}".format(_state, char, _next.next_state))

                if _next.exception:
                    _ex, _txt = _next.exception
                    raise _ex(
                        self.program_name, 
                        self.original_program[self.current_line], 
                        self.current_line, 
                        self.current_col, 
                        _txt.format(char=char))

                if _next.reset_token:
                    self.current_token = ''

                if _next.append_char:
                    self.current_token += char

            else:
                _next = MealyState('normal', wrap_token=True)

            # Add token to list if its finished
            if _next.wrap_token:
                self.log("*** Wrapping token [{}] ***".format(self.current_token))
                if self.current_token in lexerhelper.special_tokens:
                    self.appendToken(lexerhelper.special_tokens[self.current_token])
                else: # Check if is a number or a variable
                    if self.number_prog.match(self.current_token):
                        self.appendToken('snúmero')
                    elif self.identifier_prog.match(self.current_token):
                        self.appendToken('sidentificador')
                    else: # Unknown format
                        raise lexer_exceptions.InvalidTokenException(
                        self.program_name, 
                        self.original_program[self.current_line], 
                        self.current_line, 
                        self.current_col, 
                        self.current_token)

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
            raise lexer_exceptions.UnexpectedEOFException(
                self.program_name, 
                self.original_program[self.current_line], 
                self.current_line, 
                self.current_col, 
                _state)
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
    lexer.run()