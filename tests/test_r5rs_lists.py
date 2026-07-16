import pytest
from helper import HelperVM

from skime.errors import WrongArgType
from skime.types.pair import Pair as pair


class TestR5RSLists(HelperVM):
    def test_list_construction_and_selection(self):
        assert self.eval("(length '(a b c))") == 3
        assert self.eval("(append '(a b) '(c d))") == pair(
            self.eval("'a"),
            pair(self.eval("'b"), pair(self.eval("'c"), pair(self.eval("'d"), None))),
        )
        assert self.eval("(append '(a b) 'c)") == pair(
            self.eval("'a"), pair(self.eval("'b"), self.eval("'c"))
        )
        assert self.eval("(reverse '(a b c))") == self.eval("'(c b a)")
        assert self.eval("(list-tail '(a b c d) 2)") == self.eval("'(c d)")
        assert self.eval("(list-ref '(a b c d) 2)") == self.eval("'c")

    def test_composed_accessors(self):
        assert self.eval("(caddr '(a b c d))") == self.eval("'c")
        assert self.eval("(caaar '(((value))))") == self.eval("'value")
        assert self.eval("(cadddr '(a b c d))") == self.eval("'d")

    def test_membership(self):
        assert self.eval("(memq 'b '(a b c))") == self.eval("'(b c)")
        assert self.eval("(memv 2 '(1 2 3))") == self.eval("'(2 3)")
        assert self.eval("(member '(a) '(b (a) c))") == self.eval("'((a) c)")
        assert self.eval("(member 'missing '(a b c))") is False

    def test_association_lists(self):
        alist = "'((a 1) (b 2) (c 3))"
        assert self.eval("(assq 'b %s)" % alist) == self.eval("'(b 2)")
        assert self.eval("(assv 2 '((1 a) (2 b)))") == self.eval("'(2 b)")
        assert self.eval("(assoc '(a) '(((a) 1) ((b) 2)))") == self.eval("'((a) 1)")

    def test_invalid_lists_and_indexes(self):
        pytest.raises(WrongArgType, self.eval, "(length '(a . b))")
        pytest.raises(WrongArgType, self.eval, "(list-ref '(a) 1)")
        pytest.raises(WrongArgType, self.eval, "(list-tail '(a) -1)")
