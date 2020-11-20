class StackManager:
    def __init__(self, code_generator):
        self.stack = []
        self.isFunc = []
        self.intents = []
        self.acc = 0
        self.code_generator = code_generator
        self._skip = False

    def set_intent(self, contextIntent):
        self.intents.append(contextIntent)

    def new_context(self):
        if not self._skip:
            self.stack.append([])
            try:
                self.isFunc.append(self.intents.pop())
            except:
                print("Popping unknown intent")
                self.isFunc.append(False)
        self._skip = False

    def add_to_current(self, n):
        # assert len(self.stack) > 0, "No current context"
        if len(self.stack) == 0:
            self.stack.append([])
            self._skip = True
        self.stack[-1].append(n)
        self.code_generator.gera_ALLOC(self.acc, n)
        self.acc += n
        return [self.acc - n + i for i in range(n)]

    def just_dalloc(self):
        _acc = self.acc
        for n in self.stack[-1][::-1]:
            _acc -= n
            self.code_generator.gera_DALLOC(_acc, n)

    def pop_context(self):
        _ctx = self.stack.pop()
        for n in _ctx[::-1]:
            self.acc -= n
            try:
                if not self.isFunc.pop():
                    self.code_generator.gera_DALLOC(self.acc, n)
            except IndexError: # FIXME isso tá errado
                self.code_generator.gera_DALLOC(self.acc, n)