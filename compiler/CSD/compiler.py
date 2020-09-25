import argparse

from .LPDLexer.mealy_lexer import MealyLexer
from .LPDSyntax.syntax import Syntax

class Compiler:
    def __init__(self, program_name, debug=False):
        self.lexer = MealyLexer(program_name, debug=debug)
        self.syntax = Syntax(program_name, lexer=self.lexer, debug=debug)

    def run(self, debug=False, always_print_lexem_table=True):
        self.syntax.run()
        # if always_print_lexem_table:
        #     try:
        #         _tokens = self.lexer.run()
        #     except Exception as e:
        #         self.lexer.print_lexem_table()
        #         print(e)
        # else:
        #     _tokens = self.lexer.run()
        #     if debug:
        #         self.lexer.print_lexem_table()
        # if self.do_syntax:
        #     self.syntax.init_symbol_table(_tokens).run()

def get_args():
    parser = argparse.ArgumentParser(description="Compilador de 'Linguagem de Programação Didática'")
    parser.add_argument('arquivo', help="Arquivo-fonte a ser compilado")
    parser.add_argument('--verbose', help="Exibir informações durante a execução para debug", action='store_true')
    return parser.parse_args()

if __name__ == '__main__':
    args = get_args()
    this = Compiler(args.arquivo, args.verbose)
    this.run(debug=False)