import lexerhelper
import lexer_exceptions
import mealy_machine

class MealyLexer:
    def __init__(self, program_name, debug=False):
        self.program_name = program_name
        self.working_program = open(self.program_name, 'r', encoding='utf-8').read()
        self.original_program = self.working_program.split('\n')
        self.working_program = list(self.working_program)
        self.parsed_tokens = []
        self.debug = debug
        self.state = 'normal'
        self.current_token = ''
        self.machine = mealy_machine.MealyMachine({ #mealy_machine[state][character] => next_state, reset_token, append_char, wrap_token (None or token type), exception
            'normal': {
                '{': ('in_bracket', False, False, None, ),
                '/': ('in_c-like_start', False, False, None, ),
                '0123456789': ('digit', True, True, None, ),
                'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZí': ('word', True, True, None, ),
                ':': ('attribution', True, True, None, ),
                '+-*': ('arithmetic', True, True, None, ),
                '<>=': ('rel_op', True, True, None, ),
                'def': ('error', False, False, None, Exception('Unknown token'))
            },
            'in_bracket': {
                '}': ('normal', False, False, None, ),
                'def': ('in_bracket', False, False, None, )
            },
            'in_c-like_start': {
                '*': ('in_c-like', False, False, None, ),
                'def': ('normal', False, False, None, )
            },
            'in_c-like': {
                '*': ('in_c-like_end', False, False, None, ),
                'def': ('in_c-like', False, False, None, )
            },
            'in_c-like_end': {
                '/': ('normal', False, False, None, ),
                'def': ('in_c-like', False, False, None, )
            },
            'digit': {
                '0123456789': ('digit', False, True, None, ),
                'def': ('normal', False, False, 'snúmero')
            },
            'word': {
                'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZí_': ('word', False, True, None, ),
                'def': ('normal', False, False, 'keyword')
            }
        })

    def exec(self):
        for char in self.working_program:
            pass

if __name__ == '__main__':
    lexer = MealyLexer("prog1.lpd")
    #lexer.exec()