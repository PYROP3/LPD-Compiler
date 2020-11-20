class StackManager:
    def __init__(self, code_generator):
        self.stack = []
        self.acc = 0
        self.code_generator = code_generator

    def new_context(self):
        self.stack.append([])

    def add_to_current(self, n):
        assert len(self.stack) > 0, "No current context"
        self.stack[-1].append(n)
        self.code_generator.gera_ALLOC(self.acc, n)
        self.acc += n
        return [self.acc - n + i for i in range(n)]

    def pop_context(self):
        _ctx = self.stack.pop()
        for n in _ctx[::-1]:
            self.acc -= n
            self.code_generator.gera_DALLOC(self.acc, n)

# ALLOC m,n
# m = addr base da alocação original
# n = numero de variaveis