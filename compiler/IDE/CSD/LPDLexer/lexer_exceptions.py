from ..LPDExceptions import lpd_exceptions

class LexerException(lpd_exceptions.LPDException):
    def __init__(self, program_name, line, col, msg):
        super().__init__(program_name, line, col, msg=msg)

class InvalidSymbolException(LexerException):
    def __init__(self, program_name, program_line, line, col, symbol):
        self.symbol = symbol
        self.message = "error: unknown symbol '{}'".format(symbol)
        super().__init__(program_name, line, col, msg=self.message)

class InvalidTokenException(LexerException):
    def __init__(self, program_name, program_line, line, col, token):
        self.token = token
        self.message = "error: invalid token '{}'".format(token)
        super().__init__(program_name, line, col, msg=self.message)

class UnexpectedEOFException(LexerException):
    def __init__(self, program_name, program_line, line, col, end_state):
        self.end_state = end_state
        self.message = "EOF before finish: {}".format(self.end_state)
        super().__init__(program_name, line, col, msg=self.message)