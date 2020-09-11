import re

class LexerException(Exception):
    def __init__(self, msg, program_line, col, length):
        self.program_line = program_line
        self.col = col
        self.length = length
        super().__init__(msg)# + '\n' + self.getCause())

    def getCause(self, ptr='^', trail='~'):
        aux = list(re.sub('[^\t]', ' ', self.program_line))
        aux[self.col] = ptr
        aux[self.col+1:self.col+1+self.length] = [trail] * (self.length - 1)
        aux = ''.join(aux)
        return self.program_line + '\n' + aux

class InvalidSymbolException(LexerException):
    def __init__(self, program_name, program_line, line, col, symbol):
        self.program_name = program_name
        self.line = line
        self.col = col
        self.symbol = symbol
        self.message = "{}:{}:{}: error: unknown symbol \"{}\"".format(
            program_name,
            line + 1,
            col + 1,
            symbol
        )
        super().__init__(self.message, program_line, col, 1)

class InvalidTokenException(LexerException):
    def __init__(self, program_name, program_line, line, col, token):
        self.program_name = program_name
        self.line = line
        self.col = col
        self.token = token
        self.message = "{}:{}:{}: error: invalid token \"{}\"".format(
            program_name,
            line + 1,
            col + 1,
            token
        )
        super().__init__(self.message, program_line, col, len(token))