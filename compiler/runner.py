import compiler

if __name__ == '__main__':
    verbose = False
    print("=======================================================================")
    for i in range(11):
        try:
            this = compiler.Compiler('Programs/prog{}.lpd'.format(i+1))
            this.exec()
            print("prog{}.lpd OK".format(i+1))
        except Exception as e:
            print("prog{}.lpd FAIL: {}".format(i+1, e))
        if verbose:
            this.lexer.print_lexem_table()
        print("=======================================================================")
