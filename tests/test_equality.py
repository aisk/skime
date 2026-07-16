from helper import HelperVM


class TestEquality(HelperVM):
    def test_eq_uses_identity(self):
        assert self.eval("(eq? 'symbol 'symbol)") is True
        assert self.eval("(eq? (list 1) (list 1))") is False

    def test_eqv_observes_numeric_type(self):
        assert self.eval("(eqv? 1 1)") is True
        assert self.eval("(eqv? 1 1.0)") is False

    def test_equal_compares_structures(self):
        assert self.eval("(equal? '(1 (2)) '(1 (2)))") is True
        assert self.eval("(equal? '#(1 2) '#(1 2))") is True
        assert self.eval("(equal? '(1 2) '(1 3))") is False
