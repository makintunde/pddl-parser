class Predicate(object):
    def __init__(self, name, arguments):
        self.name = name
        self.arguments = arguments

    def __str__(self):
        return '(' + self.name + ', ' + str(self.arguments) + ')'
