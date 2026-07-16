import pytest
from helper import HelperVM

from skime.errors import MiscError, WrongArgNumber, WrongArgType
from skime.types.pair import Pair as pair
from skime.vm import VM


class TestApply(HelperVM):
    def test_apply(self):
        assert self.eval("(apply +)") == 0
        assert self.eval("(apply + 1 '())") == 1
        assert self.eval("(apply + 1 '(2))") == 3
        assert self.eval("(apply - 3 '(2 1))") == 0
        assert self.eval("(apply (lambda (x) x) 1 '())") == 1
        assert self.eval("(apply (lambda x x) 1 '(2 3))") == pair(
            1, pair(2, pair(3, None))
        )
        pytest.raises(WrongArgNumber, self.eval, "(apply (lambda (x) x) 1 '(2))")

    def test_nested_scheme_python_scheme_call(self):
        assert self.eval("""
            (begin
              (define (add a b) (+ a b))
              (define (caller n)
                (apply add '(1 2))
                (+ n 4))
              (caller 10))
        """) == 14


class TestIteration(HelperVM):
    def test_map(self):
        assert self.eval("(map + '(1 2) '(3 4))") == pair(4, pair(6, None))
        assert self.eval("(map + '(1 2 3))") == pair(1, pair(2, pair(3, None)))
        assert self.eval("(map (lambda (x y) (cons x y)) '(1 2) '(3 4))") == pair(
            pair(1, 3), pair(pair(2, 4), None)
        )
        pytest.raises(
            WrongArgNumber, self.eval, "(map (lambda (x y) (cons x y)) '(1 2))"
        )
        pytest.raises(WrongArgType, self.eval, "(map + '(1 2 3 . 4))")
        pytest.raises(MiscError, self.eval, "(map + '(1 2) '(3 4 5))")

    def test_for_each(self):
        assert self.eval("""
            (begin
              (define total 0)
              (for-each (lambda (value) (set! total (+ total value)))
                        '(1 2 3 4))
              total)
        """) == 10
        pytest.raises(MiscError, self.eval, "(for-each + '(1 2) '(3))")


class TestProcedures(HelperVM):
    def test_procedure_predicate(self):
        assert self.eval("(procedure? cons)") is True
        assert self.eval("(procedure? (lambda (x) x))") is True
        assert self.eval("(procedure? 5)") is False


class TestContinuations:
    def test_continuation_can_be_invoked_after_capture(self):
        vm = VM()
        vm.eval_string("(define return #f)")

        assert vm.eval_string("""
            (+ 1 (call/cc
                   (lambda (continuation)
                     (set! return continuation)
                     1)))
        """) == 2
        assert vm.eval_string("(return 22)") == 23
