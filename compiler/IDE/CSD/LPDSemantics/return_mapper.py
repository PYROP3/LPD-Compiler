COND_IF = 0
COND_ELSE = 1

class ReturnMapperWrapper:
    def __init__(self):
        self.returnMappers = []
        self.functionNames = []

    def push(self, function_name):
        self.returnMappers.append(ReturnMapper())
        self.functionNames.append(function_name)

    def pop(self):
        mapper = self.returnMappers.pop()
        _ = self.functionNames.pop()
        return mapper

    def try_ret(self, variable_name):
        if len(self.returnMappers) > 0:
            if self.functionNames[-1] == variable_name:
                self.returnMappers[-1].ret()

    def in_while(self):
        if len(self.returnMappers) > 0:
            self.returnMappers[-1].in_while()

    def out_while(self):
        if len(self.returnMappers) > 0:
            self.returnMappers[-1].out_while()

    def in_if(self):
        if len(self.returnMappers) > 0:
            self.returnMappers[-1].in_if()

    def in_else(self):
        if len(self.returnMappers) > 0:
            self.returnMappers[-1].in_else()

    def wrap_conditional(self):
        if len(self.returnMappers) > 0:
            self.returnMappers[-1].wrap()

    def validate_command(self):
        if len(self.returnMappers) > 0:
            return self.returnMappers[-1].validate_command()
        return True # If not in function body, any command is valid

class ReturnMapper:
    def __init__(self):
        self._ret = [False]
        self._idx = 0
        self._ign_depth = 0

    def ret(self):
        if self._ign_depth == 0:
            self._ret[self._idx] = True

    def in_while(self):
        self._ign_depth += 1

    def out_while(self):
        assert self._ign_depth > 0, "Not in while"
        self._ign_depth -= 1

    def in_if(self):
        self._idx = self._idx * 2 + 1
        self._ret += [False] * (self._idx + 2 - len(self._ret))

    def in_else(self):
        assert self._idx % 2 == 1, "Not in IF"
        self._idx += 1

    def wrap(self):
        _i = self._idx + (self._idx % 2)
        self._ret[_i // 2 - 1] = self._ret[_i] and self._ret[_i - 1]
        self._idx = _i // 2 - 1

    def validate_end(self):
        return self._idx == 0 and self._ret[0] == True

    def validate_command(self):
        return self._ret[self._idx] == False
