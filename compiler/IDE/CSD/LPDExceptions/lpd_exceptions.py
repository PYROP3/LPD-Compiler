class LPDException(Exception):
    def __init__(self, program_name, line, col, msg=None):
        self.program_name = program_name
        self.line = line
        self.col = col
        if msg is None:
            _msg = "{} at {}:{}:{}".format(type(self).__name__, program_name, self._inc(line), self._inc(col))
        else:
            _msg = "{} at {}:{}:{}: {}".format(type(self).__name__, program_name, self._inc(line), self._inc(col), msg)
        super().__init__(_msg)

    def _inc(self, v):
        if type(v) == type(1):
            return v+1
        return v