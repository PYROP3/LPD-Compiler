class MealyMachine:
    def __init__(self, rules, default_rules=None):
        self.machine = {}
        for state in rules:
            _aux = {}
            for chars in rules[state]:
                if chars != 'def':
                    for char in chars:
                        _aux[char] = rules[state][chars]
                else:
                    _aux['def'] = rules[state]['def']
            if default_rules:
                if 'def' not in _aux:
                    for chars in default_rules:
                        if chars != 'def':
                            for char in chars:
                                if char not in _aux:
                                    #print("Filling with default for {} in {}".format(char, default_rules[chars].next_state))
                                    _aux[char] = default_rules[chars]
                        else:
                            _aux['def'] = default_rules['def']

            self.machine[state] = _aux
        #print(self.machine)

    def getMachine(self):
        return self.machine