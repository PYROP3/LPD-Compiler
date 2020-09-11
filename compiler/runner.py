import compiler

if __name__ == '__main__':
    for i in range(9):
        try:
            this = compiler.Compiler('Programs/prog{}.lpd'.format(i+1))
            this.exec()
            print("prog{}.lpd OK".format(i+1))
        except Exception as e:
            print("prog{}.lpd FAIL: {}".format(i+1, e))
