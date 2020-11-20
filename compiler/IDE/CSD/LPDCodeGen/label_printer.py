class LabelPrinter:
    def __init__(self, prefix="L", initial=1, debug=False):
        self.prefix = prefix
        self.debug = debug
        self.it = initial

    def label(self):
        while True:
            yield "{}{}".format(self.prefix, self.it)
            self.it += 1
