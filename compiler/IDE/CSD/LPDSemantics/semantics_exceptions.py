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
    def __init__(self, program_name, line, col, symbol, stype='symbol'):
        self.symbol = symbol
        self.message = "error: found duplicated {}: {}".format(stype, symbol)
        super().__init__(program_name, line, col, msg=self.message)

class DuplicatedVariableException(DuplicatedSymbolException):
    def __init__(self, program_name, line, col, symbol):
        super().__init__(program_name, line, col, symbol, stype='variable')

class DuplicatedProcedureException(DuplicatedSymbolException):
    def __init__(self, program_name, line, col, symbol):
        super().__init__(program_name, line, col, symbol, stype='procedure')

class DuplicatedFunctionException(DuplicatedSymbolException):
    def __init__(self, program_name, line, col, symbol):
        super().__init__(program_name, line, col, symbol, stype='function')

class UndeclaredSymbolException(SemanticsException):
    def __init__(self, program_name, line, col, symbol, stype='symbol'):
        self.symbol = symbol
        self.message = "error: {} {} used without being declared".format(stype, symbol)
        super().__init__(program_name, line, col, msg=self.message)
