import argparse

from CSD import compiler

def get_args():
    parser = argparse.ArgumentParser(description="Classe wrapper para Compilador de 'Linguagem de Programação Didática'")
    parser.add_argument('arquivo', help="Arquivo-fonte a ser compilado")
    parser.add_argument('--verbose', action='store_true')
    return parser.parse_args()

if __name__ == '__main__':
    args = get_args()
    this = compiler.Compiler(args.arquivo, args.verbose)
    this.run(debug=args.verbose)