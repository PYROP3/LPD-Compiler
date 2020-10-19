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
        self.message = "error: expected {}{} but found {} instead".format('one of ' if len(self.expects) > 1 else '', ', '.join(self.expects), got)
        super().__init__(program_name, line, col, msg=self.message)

class ExpectedAnythingElseException(SyntaxException):
    def __init__(self, program_name, line, col, unexpected):
        self.unexpected = unexpected
        self.message = "error: expected anything other than {}".format(unexpected)
        super().__init__(program_name, line, col, msg=self.message)

class UnexpectedTokenException(SyntaxException):
    def __init__(self, program_name, line, col, token):
        self.token = token
        self.message = "error: found unexpected token {} after program end".format(self.token["lexeme"])
        super().__init__(program_name, line, col, msg=self.message)

class NoMoreTokensException(SyntaxException):
    def __init__(self, program_name, line, col):
        self.message = "error: no more tokens available upon request"
        super().__init__(program_name, line, col, msg=self.message)