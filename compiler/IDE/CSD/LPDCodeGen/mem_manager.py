class StackManager:
    def __init__(self, code_generator, debug=False):
        self.stack = []
        self.isFunc = []
        self.intents = []
        self.acc = 0
        self.code_generator = code_generator
        self._skip = False
        self._debug = debug

    def log(self, msg, end='\n'):
        if self._debug:
            print("[StackManager]: " + msg, end=end)

    def set_intent(self, contextIntent):
        self.log("Setting intent={}".format(contextIntent))
        self.intents.append(contextIntent)

    def new_context(self):
        if not self._skip:
            self.stack.append([])
            try:
                self.isFunc.append(self.intents.pop())
                self.log("Appended {}".format(self.isFunc[-1]))
            except:
                self.log("Popping unknown intent")
                self.isFunc.append(False)
        else:
            self.log("Skipping new context")
            self.isFunc.append(self.intents.pop())
        self._skip = False

    def add_to_current(self, n):
        self.log("Adding {} to current ctx".format(n))
        if len(self.stack) == 0:
            self.stack.append([])
            self._skip = True
        self.stack[-1].append(n)
        self.code_generator.gera_ALLOC(self.acc, n)
        self.acc += n
        return [self.acc - n + i for i in range(n)]

    def just_dalloc(self):
        self.log("Just DALLOCing")
        _acc = self.acc
        for n in self.stack[-1][::-1]:
            _acc -= n
            self.code_generator.gera_DALLOC(_acc, n)

    def pop_context(self):
        self.log("Pop context for stack={}, isFunc={}".format(self.stack, self.isFunc))
        _ctx = self.stack.pop()
        _isFunc = self.isFunc.pop()
        self.log("Popping context={} (isFunc={})".format(_ctx, _isFunc))
        for n in _ctx[::-1]:
            self.acc -= n
            try:
                if not _isFunc:
                    self.log("Popping context with DALLOC")
                    self.code_generator.gera_DALLOC(self.acc, n)
                else:
                    self.log("Popping context without DALLOC")
            except IndexError: # FIXME isso tá errado
                self.code_generator.gera_DALLOC(self.acc, n)