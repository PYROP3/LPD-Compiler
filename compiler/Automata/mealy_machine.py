
class MealyState:
    def __init__(self, next_state):
        self.next_state = next_state

class MealyMachine:
    def __init__(self, rules, initial_state=None, default_rules=None, raw=False):
        self.machine = {}
        self.state = initial_state
        for state in rules:
            _aux = {}
            for chars in rules[state]:
                if chars != 'def':
                    if raw:
                        _aux[chars] = rules[state][chars]
                    else:
                        for char in chars:
                            _aux[char] = rules[state][chars]
                else:
                    _aux['def'] = rules[state]['def']
            if default_rules:
                if 'def' not in _aux:
                    for chars in default_rules:
                        if chars != 'def':
                            if raw:
                                _aux[chars] = default_rules[chars]
                            else:
                                for char in chars:
                                    if char not in _aux:
                                        _aux[char] = default_rules[chars]
                        else:
                            _aux['def'] = default_rules['def']

            self.machine[state] = _aux

    def getMachine(self):
        return self.machine

    def step(self, read):
        _next = self.machine[self.state][read]
        self.state = _next.next_state
        return _next