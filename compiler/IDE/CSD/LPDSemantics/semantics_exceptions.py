from ..LPDExceptions import lpd_exceptions

class SemanticsException(lpd_exceptions.LPDException):
    def __init__(self, program_name, line, col, msg):
        super().__init__(program_name, line, col, msg=msg)

class UnreachableCodeException(SemanticsException):
    def __init__(self, program_name, line, col):
        self.message = "error: unreachable code!"
        super().__init__(program_name, line, col, msg=self.message)

class NonDeterministicFunctionException(SemanticsException):
    def __init__(self, program_name, line, col):
        self.message = "error: function can be executed without a return statement"
        super().__init__(program_name, line, col, msg=self.message)

class MismatchedTypeException(SemanticsException):
    def __init__(self, program_name, line, col, expected, actual):
        self.expected = expected
        self.actual = actual
        self.message = "error: operator expected {} but got {} instead".format(expected, actual)
        super().__init__(program_name, line, col, msg=self.message)

class MismatchedAttributionException(SemanticsException):
    def __init__(self, program_name, line, col, expected, actual):
        self.expected = expected
        self.actual = actual
        self.message = "error: result of expression should be {}, but is {} instead".format(expected, actual)
        super().__init__(program_name, line, col, msg=self.message)

class InvalidConditionalException(SemanticsException):
    def __init__(self, program_name, line, col):
        self.message = "error: conditional trigger should return a boolean"
        super().__init__(program_name, line, col, msg=self.message)

class DuplicatedSymbolException(SemanticsException):
    def __init__(self, program_name, line, col, symbol, first_line, first_col, stype='symbol'):
        self.symbol = symbol
        self.message = "error: found duplicated {} '{}' - first declared at {}:{}".format(stype, symbol, first_line, first_col)
        super().__init__(program_name, line, col, msg=self.message)

class UndeclaredSymbolException(SemanticsException):
    def __init__(self, program_name, line, col, symbol, stype='symbol'):
        self.symbol = symbol
        self.message = "error: {} '{}' used without being declared".format(stype, symbol)
        super().__init__(program_name, line, col, msg=self.message)

class UnexpectedTypeException(SemanticsException):
    def __init__(self, program_name, line, col, symbol, expectedType, symbolType='symbol'):
        self.symbol = symbol
        self.message = "error: expected a {} but found {} '{}' instead".format(expectedType, symbolType, symbol)
        super().__init__(program_name, line, col, msg=self.message)

class InvalidVariableTypeException(SemanticsException):
    def __init__(self, program_name, line, col, expectedType='integer', unexpectedType='boolean'):
        self.message = "error: expected a {} variable but found a {} variable instead".format(expectedType, unexpectedType)
        super().__init__(program_name, line, col, msg=self.message)
