
class InvalidDispersalException(Exception):

    def __init__(self, model: str, msg='dispersal not recognised!'):
        self.model = model
        self.msg = msg

    def __str__(self):
        return f'{self.model} {self.msg}'


class InvalidDispersalParamsException(Exception):

    def __init__(self, model: str):
        self.model = model
        if model == 'power_law':
            self.msg = "Pl dispersal params not set correctly, expected numeric types: (ell, a)"
        elif model == 'gaussian':
            self.msg = "Ga dispersal params not set correctly, expected numeric type: ell"

    def __str__(self):
        return f'{self.model} {self.msg}'


class IncorrectHostNumber(Exception):

    def __init__(self, expected, actual, msg: str = 'Incorrect number of hosts'):
        self.expected = expected
        self.actual = actual
        self.msg = msg

    def __str__(self):
        return f'{self.msg}: expected sum total S+I+R = {self.expected}, found {self.actual}'
