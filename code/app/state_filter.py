from time import ticks_ms, ticks_diff


class ABC:
    pass

class AbstractFilter(ABC):

    def filter(value):
        raise NotImplementedError("StateFilter is an abstract class")


class DuplicateFilter(AbstractFilter):

    def __init__(self, _):
        self.last = None

    def filter(self, value):
        if value == self.last:
            return None
        self.last = value
        return value


class AbstolFilter(AbstractFilter):

    def __init__(self, absol):
        self.abstol = absol
        self.last = None

    def filter(self, value):
        if self.last == None:
            self.last = value
            return value
        delta = abs(value - self.last)
        self.last = value
        return value if delta > self.abstol else None


class LpfFilter(AbstractFilter):

    def __init__(self, tau):
        # tau is in seconds, but filter measures time in ms
        self.wc = 0.001/tau
        self.last_v = None
        self.last_t = None

    def filter(self, value):
        t = ticks_ms()
        if self.last_v == None:
            self.last_v = value
            self.last_t = t
            return value
        ts = ticks_diff(t, self.last_t)
        self.last_t = t
        beta = 1/(1 + self.wc*ts)
        self.last_v = beta*self.last_v + (1-beta)*value
        return self.last_v
