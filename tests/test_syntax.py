import pytest
from helper import HelperVM

from skime.errors import SyntaxError, UnboundVariable
from skime.types.pair import Pair as pair
from skime.types.symbol import Symbol as sym


class TestSyntax(HelperVM):
    def test_atom(self):
        assert self.eval("1") == 1
        assert self.eval('"foo"') == "foo"

    def test_begin(self):
        assert self.eval("(begin 1 2 3)") == 3
        assert self.eval("(begin 1)") == 1
        assert self.eval("(begin)") == None

    def test_if(self):
        assert self.eval("(if #t 1 2)") == 1
        assert self.eval("(if #f 1 2)") == 2
        assert self.eval("(if #t 1)") == 1
        assert self.eval("(if #f 1)") == None
        pytest.raises(SyntaxError, self.eval, "(if #t)")
        pytest.raises(SyntaxError, self.eval, "(if)")
        pytest.raises(SyntaxError, self.eval, "(if #t 1 2 3)")

    def test_lambda(self):
        assert self.eval("((lambda (x) x) 5)") == 5
        assert self.eval("((lambda (x) (+ x 1)) 5)") == 6
        assert self.eval("((lambda () 5))") == 5
        assert self.eval("((lambda x (first x)) 1 2)") == 1
        assert self.eval("((lambda x (first x)) 1 2 3 4 5)") == 1
        assert self.eval("((lambda x (first x)) 1)") == 1
        assert self.eval("((lambda x x) 1 2)") == pair(1, pair(2, None))
        assert self.eval("((lambda (x . y) x) 1)") == 1
        assert self.eval("((lambda (x . y) y) 1)") == None
        assert self.eval("((lambda (x . y) (first y)) 1 2 3)") == 2

    def test_call(self):
        assert self.eval("(- 5 4)") == 1

    def test_define(self):
        assert self.eval("(begin (define foo 5) foo)") == 5
        pytest.raises(SyntaxError, self.eval, "(define)")
        pytest.raises(SyntaxError, self.eval, "(define foo)")
        pytest.raises(SyntaxError, self.eval, "(define foo 5 6)")

        assert self.eval("(begin (define (foo x) x) (foo 5))") == 5
        assert self.eval("(begin (define (foo)) (foo))") == None

        assert self.eval("(begin (define (foo . x) (first x)) (foo 1))") == 1
        assert self.eval("(begin (define (foo . x) (first x)) (foo 1 2))") == 1

    def test_set_x(self):
        assert (
            self.eval(
                """
        (begin
          (define foo 5)
          (define bar foo)
          (set! foo 6)
          (pair foo bar))"""
            )
            == pair(6, 5)
        )
        assert self.eval("(set! pair 10)") == 10
        pytest.raises(UnboundVariable, self.eval, "(set! var-not-exist 10)")

    def test_let(self):
        assert (
            self.eval(
                """
        (let ((a 3) (b 2))
          (+ a b)
          (- a b))"""
            )
            == 1
        )

        assert (
            self.eval(
                """
        (begin
          (define a 5)
          (let ((a 10) (b a))
            (- a b)))"""
            )
            == 5
        )

        assert self.eval("(let () #t)") == True
        assert self.eval("(let ())") == None

    def test_do(self):
        assert (
            self.eval(
                """
        (do ((a 6 b) (b 9 (remainder a b)))
            ((= b 0) a))"""
            )
            == 3
        )

    def test_cond(self):
        assert (
            self.eval(
                """
        (cond (#f 5 6)
              ((> 7 8) (+ 3 4))
              ((< 7 8)))"""
            )
            == True
        )

        assert (
            self.eval(
                """
        (cond (#f 5 6)
              ((> 7 8) (+ 3 4))
              ((< 7 8) (+ 5 6) (+ 6 7)))"""
            )
            == 13
        )

        assert (
            self.eval(
                """
        (cond (#f 5 6)
              ((+ 2 3) => (lambda (x) (* x x)))
              (else 10))"""
            )
            == 25
        )

        assert (
            self.eval(
                """
        (cond (#f 5 6)
              (else))"""
            )
            == None
        )

        pytest.raises(SyntaxError, self.eval, "(cond)")
        pytest.raises(
            SyntaxError,
            self.eval,
            """
        (cond (else 5)
              (#t 6))""",
        )
