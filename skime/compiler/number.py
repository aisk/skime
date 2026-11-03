import re

_UREAL = (
    r"(?:\d+/\d+|\d+\.\d*(?:[eE][+-]?\d+)?|\.\d+(?:[eE][+-]?\d+)?|\d+(?:[eE][+-]?\d+)?)"
)

_NUMBER = re.compile(
    r"(?P<real>[+-]?%s)?(?:(?P<imag_sign>[+-])(?P<imag>%s)?i)?" % (_UREAL, _UREAL)
)


def parse_number_text(text):
    """\
    Parse the text of a decimal number literal. Raise ValueError if the text
    is not a valid number.
    """
    match = _NUMBER.fullmatch(text)
    if match is None or not text:
        raise ValueError("Invalid number format: %s" % text)

    real = match.group("real")
    imag_sign = match.group("imag_sign")
    if real is None and imag_sign is None:
        raise ValueError("Invalid number format: %s" % text)

    value = _parse_real(real) if real is not None else 0
    if imag_sign is not None:
        imag = match.group("imag")
        imag = _parse_real(imag) if imag is not None else 1
        if imag_sign == "-":
            imag = -imag
        if imag != 0:
            value = value + imag * 1j
    return value


def _parse_real(text):
    sign = 1
    if text[0] in "+-":
        if text[0] == "-":
            sign = -1
        text = text[1:]
    if "/" in text:
        numerator, denominator = text.split("/")
        if int(denominator) == 0:
            raise ValueError("Invalid number format, denominator cannot be zero")
        return sign * (float(numerator) / int(denominator))
    if "." in text or "e" in text or "E" in text:
        return sign * float(text)
    return sign * int(text)
