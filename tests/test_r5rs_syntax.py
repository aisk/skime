import pytest
from helper import HelperVM

from skime.errors import SyntaxError


class TestR5RSSyntax(HelperVM):
    def test_named_let(self):
        assert self.eval("""
                (let loop ((numbers '(1 2 3 4)) (sum 0))
                  (if (null? numbers)
                      sum
                      (loop (cdr numbers) (+ sum (car numbers)))))
                """) == 10

    def test_case(self):
        assert self.eval(
            "(case (* 2 3) ((2 3 5 7) 'prime) ((1 4 6 8) 'composite))"
        ) == self.eval("'composite")
        assert self.eval("(case 'unknown ((a b) 1) (else 2))") == 2
        assert self.eval("(case 'unknown ((a b) 1))") is None
        pytest.raises(SyntaxError, self.eval, "(case 1 (else 1) ((1) 2))")

    def test_quasiquote(self):
        assert self.eval("`(list ,(+ 1 2) 4)") == self.eval("'(list 3 4)")
        assert self.eval("`(a ,@(list 1 2) b)") == self.eval("'(a 1 2 b)")
        assert self.eval("`(a . ,(+ 1 2))") == self.eval("'(a . 3)")
        assert self.eval("`(a `(b ,(+ 1 2)))") == self.eval(
            "'(a (quasiquote (b (unquote (+ 1 2)))))"
        )

    def test_invalid_quasiquote(self):
        pytest.raises(SyntaxError, self.eval, "(quasiquote)")
        pytest.raises(SyntaxError, self.eval, "`,@'(a b)")
