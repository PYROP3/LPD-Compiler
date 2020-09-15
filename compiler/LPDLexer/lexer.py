import re
from . import lexerhelper
from . import lexer_exceptions
import argparse 

class Lexer:
    def __init__(self, program_name, debug=False):
        self.program_name = program_name
        self.valid_characters = re.compile('[^{}]'.format(lexerhelper.valid_characters))
        self.working_program = open(self.program_name, 'r', encoding='utf-8').read()
        self.original_program = self.working_program.split('\n')
        self.parsed_tokens = []
        self.debug = debug

    def exec(self):
        routine = [
            self.remove_comments,
            self.break_lines,
            self.remove_whitespaces,
            self.space_symbols,
            self.explode_boundaries,
            self.rejoin_symbols,
            self.split_tokens
        ]

        for func in routine:
            self.log(func)
            func()
            if self.debug:
                self.print_working_program()

        verify_routine = [
            self.verify_symbols,
            self.verify_tokens
        ]

        for func in verify_routine:
            func()

        if (self.debug):
            self.print_lexem_table()

        return self.parsed_tokens

    def remove_comments(self):
        _aux = list(self.working_program)
        _rules = {
            'normal': {
                '{': ('in_bracket', True, False),
                '/': ('in_c-like_start', False, False),
                'def': ('normal', False, False)
            },
            'in_bracket': {
                '}': ('normal', True, False),
                'def': ('in_bracket', True, False)
            },
            'in_c-like_start': {
                '*': ('in_c-like', True, True),
                'def': ('normal', False, False)
            },
            'in_c-like': {
                '*': ('in_c-like_end', True, False),
                'def': ('in_c-like', True, False)
            },
            'in_c-like_end': {
                '/': ('normal', True, True),
                'def': ('in_c-like', True, False)
            }
        }
        _state = 'normal'
        _prev_in_comment = False
        _in_comment = False
        _lineno = 0
        _colno = 0
        _comment_line = 0
        _comment_col = 0
        for idx, c in enumerate(_aux):
            if c in _rules[_state]:
                _state, _in_comment, _remove_prev = _rules[_state][c]
            else:
                _state, _in_comment, _remove_prev = _rules[_state]['def']
            if _in_comment:
                _aux[idx] = '\n' if c == '\n' else ' '
                if not _prev_in_comment:
                    _comment_line = _lineno
                    _comment_col = _colno
            if _remove_prev:
                _aux[idx-1] = ' '
            _colno += 1
            if c == '\n':
                _lineno += 1
                _colno = 0
            _prev_in_comment = _in_comment
            
        if _state != 'normal':
            raise Exception("Terminei com estado {} ({}:{})".format(_state, _comment_line, _comment_col))
        self.working_program = ''.join(_aux)

    def break_lines(self):
        self.working_program = self.working_program.split('\n')

    def remove_whitespaces(self):
        _prog = re.compile(r"[ \n\t]+")
        self.working_program = [_prog.sub(' ', line) for line in self.working_program]

    def space_symbols(self):
        _symb = lexerhelper.symbol_list
        _prog = re.compile(f"([{_symb}])")
        self.working_program = [_prog.sub(r" \1 ", line) for line in self.working_program]

    def rejoin_symbols(self):
        _symb = lexerhelper.special_symbols
        for symbol in _symb:
            self.working_program = [re.sub(f"({symbol[0]}) *({symbol[1]})", r"\1\2", line) for line in self.working_program]

    def explode_boundaries(self):
        _progws = re.compile(r"([ía-zA-Z0-9_])([^ía-zA-Z0-9_ ])")
        _progsw = re.compile(r"([^ía-zA-Z0-9_ ])([ía-zA-Z0-9_])")
        self.working_program = [_progws.sub(r"\1 \2", line) for line in self.working_program]
        self.working_program = [_progsw.sub(r"\1 \2", line) for line in self.working_program]

    def split_tokens(self):
        self.tokens = [line.split() for line in self.working_program]
        self.line_translation = [idx for (idx, val) in enumerate(self.tokens) if len(val)]
        if self.debug:
            for no, thing in enumerate(self.line_translation):
                print("Original: {} | Translated: {}".format(no, thing))
        self.tokens = [line for line in self.tokens if line != []]

    def verify_symbols(self):
        for lineno, line in enumerate(self.tokens):
            for tokenno, token in enumerate(line):
                res = self.valid_characters.search(token)
                if res is not None:
                    line_format = '.*?' + '.*?'.join([re.escape(_tok) for _tok in line[:tokenno]]) + ".*?({})".format(re.escape(token))
                    self.log(line_format)

                    line_trans = self.get_translated_lineno(lineno)
                    orig_line = self.get_translated_line(lineno)
                    m = re.match(line_format, orig_line)
                    self.log(m)

                    match_col = res.start(0) + m.end() - len(m.groups(1)[0])
                    raise lexer_exceptions.InvalidSymbolException(self.program_name, orig_line, line_trans, match_col, res.string[res.start(0):res.end(0)])

    def verify_tokens(self):
        prog_number = re.compile(lexerhelper.format_number)
        prog_ident = re.compile(lexerhelper.format_identifier)
        self.parsed_tokens = []

        for lineno, line in enumerate(self.tokens):
            line_trans = self.get_translated_lineno(lineno)
            orig_line = self.get_translated_line(lineno)

            self.log("\nLine {} (from {}): {}".format(line_trans, lineno, orig_line.rstrip()))

            for tokenno, token in enumerate(line):
                line_format = '.*?' + '.*?'.join([re.escape(_tok) for _tok in line[:tokenno]]) + ".*?({})".format(re.escape(token))
                self.log(line_format)

                m = re.match(line_format, orig_line)

                token_col = m.end() - len(m.groups(1)[0])

                if (token in lexerhelper.special_tokens):
                    tok = {'lexeme':token, 'type':lexerhelper.special_tokens[token], 'line': line_trans, 'col': token_col}
                else:
                    m = prog_number.match(token)
                    if m is not None:
                        tok = {'lexeme':token, 'type':'snúmero', 'line': line_trans, 'col': token_col}
                    else:
                        m = prog_ident.match(token)
                        if m is not None:
                            tok = {'lexeme':token, 'type':'sidentificador', 'line': line_trans, 'col': token_col}
                        else:
                            raise lexer_exceptions.InvalidTokenException(self.program_name, orig_line, line_trans, token_col, token)
                self.parsed_tokens.append(tok)

    def print_working_program(self, tokens=False):
        if type(self.working_program) == type([]):
            print('\n'.join(["{}: {}".format(lineno, " ".join(line) if tokens else line) for lineno, line in enumerate(self.working_program)]))
        else:
            print(self.working_program)

    def print_lexem_table(self):
        assert self.parsed_tokens is not None, "Parser has not been executed"
        print("{:20s}|{:15s}|{:6s}|{:6s}".format("Tipo", "Lexema", "Linha", "Coluna"))
        print("-" * 20 + "+" + "-" * 15 + "+" + "-" * 6 + "+" + "-" * 6)
        for token in self.parsed_tokens:
            print("{:20s}|{:15s}|{:6d}|{:6d}".format(token['type'], token['lexeme'], token['line'], token['col']))

    def get_translated_lineno(self, lineno):
        return self.line_translation[lineno]

    def get_translated_line(self, lineno):
        return self.original_program[self.get_translated_lineno(lineno)].rstrip()

    def log(self, line, end='\n'):
        if (self.debug):
            print(line, end=end)

if __name__ == '__main__':
    lexer = Lexer("prog1.lpd")
    lexer.exec()