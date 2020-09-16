import os

from CSD import compiler

inputdir = "Programs"
linesep = "==================================================================================================================================================================="

if __name__ == '__main__':
    this = compiler.Compiler("Programs/program.lpd")
    this.run()
    verbose = False
    print(linesep)
    for prog in os.listdir(inputdir):
        filename = inputdir + "/" + prog
        try:
            this = compiler.Compiler(filename)
            this.run()
            print("{}\n\t+ OK".format(filename))
        except Exception as e:
            print("{}\n\t- {}".format(filename, e))
        if verbose:
            this.lexer.print_lexem_table()
        print(linesep)
