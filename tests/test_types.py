import pytest

from skime.types.pair import Pair
from skime.types.symbol import Symbol


def test_mutable_pairs_are_unhashable():
    with pytest.raises(TypeError):
        hash(Pair(1, None))


def test_symbol_name_cannot_be_changed():
    symbol = Symbol("name")

    with pytest.raises(AttributeError):
        symbol.name = "other"
