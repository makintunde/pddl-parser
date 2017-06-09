class InitState(object):
    def __init__(self, state):
        self.states = []
        for s in state:
            if isinstance(s, list):
                self.states.append(s)
            else:
                self.states.append([s])
        self.states = self.flatten(self.states)

    def __str__(self):
        # ('\n '.join(self.eval())) + '\n'
        return str(self.eval())

    def eval(self):
        states = self.states
        states[0] = [s[0] if isinstance(s, list) and len(s) == 1 else s for s in states[0]]
        print 'states:', states
        return [s[1:] if s[0] == 'oneof' else s for s in states]

    def serialise(self):
        result = []
        for s in self.states:
            if s[0] in ['oneof', '=']:
                result.append('#'.join('_'.join(i) for i in s[1:]))
            else:
                result.append('_'.join(s))
        return result

    def flatten(self, s):
        if isinstance(s, str):
            return s.replace('-', '_')
        elif isinstance(s, list):
            return map(self.flatten, s)


