import argparse

from .LPDLexer.mealy_lexer import MealyLexer
from .LPDSyntax.syntax import Syntax

class Compiler:
    def __init__(self, program_name, debug=False, do_syntax=False):
        self.lexer = MealyLexer(program_name, debug=debug)
        self.do_syntax = do_syntax
        if self.do_syntax:
            self.syntax = Syntax(program_name, debug=debug)

    def run(self, debug=False):
        _tokens = self.lexer.run()
        if debug:
            self.lexer.print_lexem_table()
        if self.do_syntax:
            self.syntax.init_symbol_table(_tokens).run()

def get_args():
    parser = argparse.ArgumentParser(description="Compilador de 'Linguagem de Programação Didática'")
    parser.add_argument('arquivo', help="Arquivo-fonte a ser compilado")
    parser.add_argument('--verbose', help="Exibir informações durante a execução para debug", action='store_true')
    return parser.parse_args()

if __name__ == '__main__':
    args = get_args()
    this = Compiler(args.arquivo, args.verbose)
    this.run(debug=False)