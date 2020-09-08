import re
from . import lexerhelper
from . import lexer_exceptions
import argparse 

class Lexer:
    def __init__(self, program_name, debug=False):
        self.program_name = program_name
        self.valid_characters = re.compile('[^{}]'.format(lexerhelper.valid_characters))
        self.original_program = open(self.program_name, 'r', encoding='utf-8').readlines()
        self.working_program = self.original_program[:]
        self.debug = debug

    def exec(self):
        routine = [
            self.remove_whitespaces,
            self.remove_comments,
            self.space_symbols,
            self.explode_boundaries,
            self.rejoin_symbols,
            self.split_tokens
        ]

        for func in routine:
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

    def remove_whitespaces(self):
        _prog = re.compile(r"[ \n\t]+")
        self.working_program = [_prog.sub(' ', line) for line in self.working_program]

    def remove_comments(self):
        _prog = re.compile(r"\{[^}]*?\}")
        self.working_program = [_prog.sub('', line) for line in self.working_program]

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
        skip_lines = [bool(len(line) == 0) for line in self.tokens]
        self.line_translation = []
        line_no = 0
        for isSkip in skip_lines:
            if not isSkip:
                self.line_translation.append(line_no)
            line_no += 1
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
        print('\n'.join(["{}: {}".format(lineno, " ".join(line) if tokens else line) for lineno, line in enumerate(self.working_program)]))

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