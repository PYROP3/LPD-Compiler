import re
from . import lexerhelper
from . import lexer_exceptions
from ..Automata import mealy_machine

class MealyLexerState(mealy_machine.MealyState):
    def __init__(self, next_state, reset_token=False, append_char=False, wrap_token=False, exception=None):
        super().__init__(next_state)
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
                '{': MealyLexerState('in_bracket'),
                '/': MealyLexerState('in_c-like_start'),
                '0123456789': MealyLexerState('digit', reset_token=True, append_char=True),
                'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZí': MealyLexerState('word', reset_token=True, append_char=True),
                ':': MealyLexerState('attribution', reset_token=True, append_char=True),
                '+-*;.,()': MealyLexerState('symbol', reset_token=True, append_char=True),
                '!<>=': MealyLexerState('rel_op', reset_token=True, append_char=True),
                ' \n\t': MealyLexerState('normal'),
            },
            'in_bracket': {
                '}': MealyLexerState('normal'),
                'def': MealyLexerState('in_bracket')
            },
            'in_c-like_start': {
                '*': MealyLexerState('in_c-like'),
                'def': MealyLexerState('error', exception=(lexer_exceptions.InvalidSymbolException, "/{char}"))
            },
            'in_c-like': {
                '*': MealyLexerState('in_c-like_end'),
                'def': MealyLexerState('in_c-like')
            },
            'in_c-like_end': {
                '/': MealyLexerState('normal'),
                'def': MealyLexerState('in_c-like')
            },
            'digit': {
                '0123456789': MealyLexerState('digit', append_char=True)
            },
            'word': {
                'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZí_0123456789': MealyLexerState('word', append_char=True)
            },
            'attribution': {
                '=': MealyLexerState('normal', append_char=True, wrap_token=True)
            },
            'rel_op': {
                '=': MealyLexerState('normal', append_char=True, wrap_token=True)
            },
            'symbol': { }
        },
        default_rules={
                '{': MealyLexerState('in_bracket', wrap_token=True),
                '/': MealyLexerState('in_c-like_start', wrap_token=True),
                '0123456789': MealyLexerState('digit', wrap_token=True),
                'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZí': MealyLexerState('word', wrap_token=True),
                ':': MealyLexerState('attribution', wrap_token=True),
                '+-*;.,()': MealyLexerState('symbol', wrap_token=True),
                '!<>=': MealyLexerState('rel_op', wrap_token=True),
                ' \n\t.': MealyLexerState('normal', wrap_token=True),
        },
        raw=False).getMachine()
        self.identifier_prog = re.compile(lexerhelper.format_identifier)
        self.number_prog = re.compile(lexerhelper.format_number)

    def tokenGenerator(self):
        _state = 'normal'
        for char in self.working_program + [' ']:
            _mealy_state = self.machine[_state]

            if char is not None:
                if char not in _mealy_state and 'def' not in _mealy_state:
                    raise lexer_exceptions.InvalidSymbolException(
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
                _next = MealyLexerState('normal', wrap_token=True)

            # Add token to list if its finished
            if _next.wrap_token:
                self.log("*** Wrapping token [{}] ***".format(self.current_token))
                if self.current_token in lexerhelper.special_tokens:
                    _tok = self.createToken(lexerhelper.special_tokens[self.current_token])
                    self.appendToken(_tok)
                    yield _tok
                elif self.number_prog.match(self.current_token): # Check if is a number or an identifier
                    _tok = self.createToken('snúmero')
                    self.appendToken(_tok)
                    yield _tok
                elif self.identifier_prog.match(self.current_token):
                    _tok = self.createToken('sidentificador')
                    self.appendToken(_tok)
                    yield _tok
                else: # Unknown format
                    raise lexer_exceptions.InvalidTokenException(
                        self.program_name,
                        self.original_program[self.current_line],
                        self.current_line,
                        self.current_col-1,
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
        return self.parsed_tokens

    def createToken(self, _type):
        return {
            'lexeme': self.current_token,
            'type': _type,
            'line': self.current_line,
            'col': self.current_col - len(self.current_token)
            }

    # TODO is this necessary?
    def appendToken(self, token):
        self.parsed_tokens.append(token)

    def print_lexem_table(self):
        assert self.parsed_tokens is not None, "Parser has not been executed"
        print("{:20s}|{:15s}|{:6s}|{:6s}".format("Tipo", "Lexema", "Linha", "Coluna"))
        print("-" * 20 + "+" + "-" * 15 + "+" + "-" * 6 + "+" + "-" * 6)
        for token in self.parsed_tokens:
            print("{:20s}|{:15s}|{:6d}|{:6d}".format(token['type'], token['lexeme'], token['line'], token['col']))

    def log(self, line, end='\n'):
        if (self.debug):
            print(line, end=end)
