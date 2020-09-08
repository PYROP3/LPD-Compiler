special_tokens = {
    'programa': 'sprograma',
    'início': 'sinício',
    'fim': 'sfim',
    'procedimento': 'sprocedimento',
    'funcao': 'sfuncao',
    'se': 'sse',
    'entao': 'sentao',
    'senao': 'ssenao',
    'enquanto': 'senquanto',
    'faca': 'sfaca',
    ':=': 'satribuição',
    'escreva': 'sescreva',
    'leia': 'sleia',
    'var': 'svar',
    'inteiro': 'sinteiro',
    'booleano': 'sbooleano',
    '.': 'sponto',
    ';': 'sponto_vírgula',
    ',': 'svírgula',
    '(': 'sabre_parênteses',
    ')': 'sfecha_parênteses',
    '>': 'smaior',
    '>=': 'smaiorig',
    '=': 'sig',
    '<': 'smenor',
    '<=': 'smenorig',
    '!=': 'sdif',
    '+': 'smais',
    '-': 'smenos',
    '*': 'smult',
    'div': 'sdiv',
    'e': 'se',
    'ou': 'sou',
    'nao': 'snao',
    ':': 'sdoispontos'
}

valid_characters = r"a-zA-Z0-9:=.;,()<>!+\-*:_í"

symbol_list = r":;.,()\-+*<>=!"

special_symbols = [":=", "!=", "<=", ">="]

format_identifier = '[a-zA-Z][a-zA-Z0-9_]*'

format_number = '[0-9]+'