import unittest
import compiler
from Lexer import lexer_exceptions

def run(program_name):
    try:
        compiler.Compiler(program_name, True).run()
        print("=======================================================================")
        return None
    except Exception as e:
        print("=======================================================================")
        return e

class VerifyProgramTests(unittest.TestCase):

    def test_return_true_pattern_program(self):
        result = run('Programs/program.lpd')
        self.assertEqual(result, None)

    def test_return_false_with_unrecognized_symbols(self):
        result = run('Programs/program_with_unrecognized_symbols.lpd')
        self.assertEqual(type(result), lexer_exceptions.InvalidSymbolException)
        self.assertEqual(3, result.line)
        self.assertEqual(0, result.col)

    def test_return_true_program_with_recognized_symbols(self):
        result = run('Programs/program_with_recognized_symbols.lpd')
        self.assertEqual(result, None)

    def test_return_false_program_with_exclamation_mark_without_equal(self):
        result = run('Programs/program_with_exclamation_mark_without_equal.lpd')
        self.assertEqual(type(result), lexer_exceptions.InvalidTokenException)
        self.assertEqual(9, result.line)
        self.assertEqual(6, result.col) 

    def test_return_false_program_with_close_braces(self):
        result = run('Programs/program_with_close_braces.lpd')
        self.assertEqual(type(result), lexer_exceptions.InvalidTokenException)
        self.assertEqual(3, result.line)
        self.assertEqual(8, result.col)

    def test_return_false_program_with_close_braces2(self):
        result = run('Programs/program_with_close_braces2.lpd')
        self.assertEqual(type(result), lexer_exceptions.InvalidTokenException)
        self.assertEqual(0, result.line)
        self.assertEqual(0, result.col)

    def test_return_true_program_with_repeated_symbols(self):
        result = run('Programs/program_with_repeated_symbols.lpd')
        self.assertEqual(result, None)

    def test_return_true_program_with_colon_without_equal(self):
        result = run('Programs/program_with_colon_without_equal.lpd')
        self.assertEqual(result, None)

    def test_return_true_program_number_with_point(self):
        result = run('Programs/program_number_with_point.lpd')
        self.assertEqual(result, None)

    def test_return_true_program_number_with_point2(self):
        result = run('Programs/program_number_with_point2.lpd')
        self.assertEqual(result, None)

    def test_return_false_program_number_with_point_and_unclose_braces(self):
        result = run('Programs/program_number_with_point_and_unclose_braces.lpd')
        self.assertEqual(type(result), lexer_exceptions.UnexpectedEOFException)
        self.assertEqual(36, result.line) #Linha do erro aponta final do programa já que comentário não foi fechado
        self.assertEqual(0, result.col)

    def test_return_false_program_number_with_underlined_at_the_beginning_of_identifier(self):
        result = run('Programs/program_number_with_underlined_at_the_beginning_of_identifier.lpd')
        self.assertEqual(type(result), lexer_exceptions.InvalidTokenException) #Verificar se Exception esta certa
        self.assertEqual(3, result.line)
        self.assertEqual(4, result.col)

    def test_return_true_when_program_finish_with_braces(self):
        result = run('Programs/program_finish_with_braces.lpd')
        self.assertEqual(result, None)

    def test_return_true_when_program_finish_with_slash_asterisk(self):
        result = run('Programs/program_finish_with_slash_asterisk.lpd')
        self.assertEqual(result, None)

    def test_return_true_when_program_finish_with_tab(self):
        result = run('Programs/program_finish_with_tab.lpd')
        self.assertEqual(result, None)

    def test_return_true_when_program_finish_with_enter(self):
        result = run('Programs/program_finish_with_enter.lpd')
        self.assertEqual(result, None)

    def test_return_true_when_program_finish_with_space(self):
        result = run('Programs/program_finish_with_space.lpd')
        self.assertEqual(result, None)