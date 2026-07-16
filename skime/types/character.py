class Character(object):
    __slots__ = ("value",)

    def __init__(self, value):
        if not isinstance(value, str) or len(value) != 1:
            raise ValueError("A character must contain exactly one code point")
        self.value = value

    def __eq__(self, other):
        return isinstance(other, Character) and self.value == other.value

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.value)

    def __str__(self):
        names = {" ": "space", "\n": "newline"}
        return "#\\" + names.get(self.value, self.value)

    def __repr__(self):
        return "Character(%r)" % self.value
