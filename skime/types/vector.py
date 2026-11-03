class Vector(object):
    __slots__ = ("elements",)

    def __init__(self, elements=()):
        self.elements = list(elements)

    def __eq__(self, other):
        return isinstance(other, Vector) and self.elements == other.elements

    def __ne__(self, other):
        return not self.__eq__(other)

    __hash__ = None

    def __len__(self):
        return len(self.elements)

    def __str__(self):
        from ..printer import scheme_write

        return scheme_write(self)

    def __repr__(self):
        return "Vector(%r)" % self.elements
