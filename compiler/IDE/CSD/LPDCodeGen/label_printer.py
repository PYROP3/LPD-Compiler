class LabelPrinter:
    def __init__(self, prefix="L", debug=False):
        self.prefix = prefix
        self.debug = debug
        self.it = 0

    def label(self):
        while True:
            yield "{}{}".format(self.prefix, self.it)
            self.it += 1
