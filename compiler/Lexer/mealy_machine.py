class MealyMachine:
    def __init__(self, rules):
        self.machine = {}
        for key in rules:
            _aux = {}
            for chars in rules[key]:
                for char in chars:
                    _aux[char] = rules[key][chars]
            self.machine[key] = _aux
        print(self.machine)