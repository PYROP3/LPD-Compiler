special_tokens = {
    'programa': 'sprograma',
    'inicio': 'sinício',
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
    'verdadeiro': 'sverdadeiro',
    'falso': 'sfalso',
    ':': 'sdoispontos'
}

valid_characters = r"a-zA-Z0-9:=.;,()<>!+\-*:_í"

symbol_list = r":;.,()\-+*<>=!"

special_symbols = [":=", "!=", "<=", ">="]

format_identifier = r'[a-zA-Z][a-zA-Z0-9_]*'

format_number = r'[0-9]+'