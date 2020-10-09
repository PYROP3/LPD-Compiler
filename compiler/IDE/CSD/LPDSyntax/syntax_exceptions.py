from ..LPDExceptions import lpd_exceptions

class SyntaxException(lpd_exceptions.LPDException):
    def __init__(self, program_name, line, col, msg):
        super().__init__(program_name, line, col, msg=msg)

class UnexpectedTypeException(SyntaxException):
    def __init__(self, program_name, line, col, expects, got):
        if type(expects) == type('a'):
            self.expects = [expects]
        else:
            self.expects = expects
        self.got = got
        self.message = "error: expected one of {} but found {} instead".format(', '.join(self.expects), got)
        super().__init__(program_name, line, col, msg=self.message)

class UnexpectedTokenException(SyntaxException):
    def __init__(self, program_name, line, col, token):
        self.token = token
        self.message = "error: found unexpected token {} after program end".format(self.token["lexeme"])
        super().__init__(program_name, line, col, msg=self.message)