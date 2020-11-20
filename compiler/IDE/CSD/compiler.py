import argparse

from .LPDLexer.mealy_lexer import MealyLexer
from .LPDLexer.lexer_exceptions import UnexpectedEOFException
from .LPDSyntax.syntax import Syntax
from .LPDExceptions.lpd_exceptions import LPDException

class InformalEndException(LPDException):
    def __init__(self, program_name, program_line, line, col):
        self.message = "Program finished inside a comment"
        super().__init__(program_name, line, col, msg=self.message)

class Compiler:
    def __init__(self, program_name, debug=False):
        self.lexer = MealyLexer(program_name, debug=debug)
        self.syntax = Syntax(program_name, lexer=self.lexer, debug=debug)

    def run(self, debug=False):
        try:
            self.syntax.run()
            return self.syntax.getObjFile()
        except UnexpectedEOFException as e:
            raise InformalEndException(
                e.program_name,
                None,
                e.line,
                e.col)

def get_args():
    parser = argparse.ArgumentParser(description="Compilador de 'Linguagem de Programação Didática'")
    parser.add_argument('arquivo', help="Arquivo-fonte a ser compilado")
    parser.add_argument('--verbose', help="Exibir informações durante a execução para debug", action='store_true')
    return parser.parse_args()

if __name__ == '__main__':
    args = get_args()
    this = Compiler(args.arquivo, args.verbose)
    this.run(debug=False)