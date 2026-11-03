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

    def test_equal_compares_atoms_with_eqv(self):
        assert self.eval("(equal? #t 1)") is False
        assert self.eval("(equal? 1 1.0)") is False
        assert self.eval('(equal? "ab" "ab")') is True
        assert self.eval("(equal? #\\a #\\a)") is True
        assert self.eval("(member #t '(1))") is False
        assert self.eval("(assoc 1 '((#t . x)))") is False

    def test_equal_handles_long_lists(self):
        assert self.eval("""
            (let loop ((i 0) (a '()) (b '()))
              (if (= i 100000)
                  (equal? a b)
                  (loop (+ i 1) (cons i a) (cons i b))))
            """) is True

    def test_similar_literals_are_not_merged(self):
        assert self.eval("(equal? '(1) '(1.0))") is False
        assert self.eval("(eq? '(1) '(1))") is False
        assert self.eval("(equal? '#(1) '#(1.0))") is False
