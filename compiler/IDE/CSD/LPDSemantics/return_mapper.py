COND_IF = 0
COND_ELSE = 1

class ReturnMapperWrapper:
    def __init__(self, debug=False):
        self.returnMappers = []
        self.functionNames = []
        self._debug = debug

    def log(self, msg, end='\n'):
        if self._debug:
            print("[ReturnMapperWrapper]: " + msg, end=end)

    def push(self, function_name):
        self.returnMappers.append(ReturnMapper(debug=self._debug))
        self.functionNames.append(function_name)
        self.log("Pushing new ReturnMapper (now {})".format(len(self.returnMappers)))

    def pop(self):
        mapper = self.returnMappers.pop()
        _ = self.functionNames.pop()
        self.log("Popped ReturnMapper={} (now {})".format(mapper, len(self.returnMappers)))
        return mapper

    def try_ret(self, variable_name):
        if len(self.returnMappers) > 0:
            if self.functionNames[-1] == variable_name:
                self.returnMappers[-1].ret()
                return True
        return False

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
    def __init__(self, debug=False):
        self._ret = [False]
        self._idx = 0
        self._ign_depth = 0
        self._debug = debug
        self.log("New ReturnMapper")

    def log(self, msg, end='\n'):
        if self._debug:
            print("[ReturnMapper]: " + msg, end=end)

    def outputReturn(self):
        self.log("_ret=[{}]; idx={}, ign={}".format(",".join(["T" if v else "F" for v in self._ret]), self._idx, self._ign_depth))

    def ret(self):
        self.log("In ret")
        if self._ign_depth == 0:
            self._ret[self._idx] = True
        self.outputReturn()

    def in_while(self):
        self.log("In while")
        self._ign_depth += 1
        self.outputReturn()

    def out_while(self):
        self.log("Out while")
        assert self._ign_depth > 0, "Not in while"
        self._ign_depth -= 1
        self.outputReturn()

    def in_if(self):
        self.log("In if")
        self._idx = self._idx * 2 + 1
        self._ret += [False] * (self._idx + 2 - len(self._ret))
        self.outputReturn()

    def in_else(self):
        self.log("In else")
        assert self._idx % 2 == 1, "Not in IF"
        self._idx += 1
        self.outputReturn()

    def wrap(self):
        self.log("Wrapping...")
        _i = self._idx + (self._idx % 2)
        self._ret[_i // 2 - 1] = self._ret[_i] and self._ret[_i - 1]
        self._idx = _i // 2 - 1
        # Cleanup
        self._ret[_i] = False
        self._ret[_i-1] = False
        self.outputReturn()

    def validate_end(self):
        self.log("Validating end")
        self.outputReturn()
        return self._idx == 0 and self._ret[0] == True

    def validate_command(self):
        self.log("Validating command")
        self.outputReturn()
        return self._ret[self._idx] == False
