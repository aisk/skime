"""Formatting of skime objects into their external representation."""

from .types.character import Character
from .types.pair import Pair as pair
from .types.vector import Vector


def scheme_write(obj):
    "Return the external representation of obj, as the write procedure."
    return format_object(obj, False, set())


def scheme_display(obj):
    "Return the representation of obj, as the display procedure."
    return format_object(obj, True, set())


def format_object(obj, display, active):
    # active holds the containers on the current printing path, so that
    # circular structures are printed as "..." instead of looping forever.
    if obj is True:
        return "#t"
    if obj is False:
        return "#f"
    if obj is None:
        return "()"
    if isinstance(obj, Character):
        return obj.value if display else str(obj)
    if isinstance(obj, str):
        if display:
            return obj
        escaped = (
            obj.replace("\\", "\\\\")
            .replace('"', '\\"')
            .replace("\n", "\\n")
            .replace("\t", "\\t")
        )
        return '"%s"' % escaped
    if isinstance(obj, complex):
        sign = "+" if obj.imag >= 0 else "-"
        return "%s%s%si" % (obj.real, sign, abs(obj.imag))
    if isinstance(obj, Vector):
        if id(obj) in active:
            return "..."
        active.add(id(obj))
        elements = [format_object(x, display, active) for x in obj.elements]
        active.discard(id(obj))
        return "#(" + " ".join(elements) + ")"
    if isinstance(obj, pair):
        if id(obj) in active:
            return "..."
        elements = []
        visited = []
        value = obj
        while isinstance(value, pair):
            if id(value) in active:
                elements.extend([".", "..."])
                value = None
                break
            active.add(id(value))
            visited.append(id(value))
            elements.append(format_object(value.first, display, active))
            value = value.rest
        if value is not None:
            elements.extend([".", format_object(value, display, active)])
        for key in visited:
            active.discard(key)
        return "(" + " ".join(elements) + ")"
    return str(obj)
