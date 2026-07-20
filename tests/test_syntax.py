import pytest
from helper import HelperVM

from skime.errors import SyntaxError, UnboundVariable
from skime.types.pair import Pair as pair
from skime.vm import VM


class TestSyntax(HelperVM):
    def test_atom(self):
        assert self.eval("1") == 1
        assert self.eval('"foo"') == "foo"

    def test_begin(self):
        assert self.eval("(begin 1 2 3)") == 3
        assert self.eval("(begin 1)") == 1
        assert self.eval("(begin)") == None
        pytest.raises(SyntaxError, self.eval, "(begin 1 . 2)")

    def test_if(self):
        assert self.eval("(if #t 1 2)") == 1
        assert self.eval("(if #f 1 2)") == 2
        assert self.eval("(if #t 1)") == 1
        assert self.eval("(if #f 1)") == None
        pytest.raises(SyntaxError, self.eval, "(if #t)")
        pytest.raises(SyntaxError, self.eval, "(if)")
        pytest.raises(SyntaxError, self.eval, "(if #t 1 2 3)")

    def test_boolean_and_short_circuit_forms(self):
        assert self.eval("(boolean? #t)") is True
        assert self.eval("(boolean? 0)") is False
        assert self.eval("(not #f)") is True
        assert self.eval("(not '())") is False
        assert self.eval("(or)") is False
        assert self.eval("(or #f 2 3)") == 2
        assert self.eval("(and)") is True
        assert self.eval("(and #t 2 3)") == 3
        assert self.eval("""
            (begin
              (define value 2)
              (or #f (set! value 3) (set! value 4))
              value)
        """) == 3
        assert self.eval("""
            (begin
              (define value 2)
              (and #t (set! value 3) (set! value 4))
              value)
        """) == 4

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
        pytest.raises(SyntaxError, self.eval, "(lambda)")
        pytest.raises(SyntaxError, self.eval, "(lambda (x x) x)")
        pytest.raises(SyntaxError, self.eval, "(lambda (x . x) x)")

    def test_closures_from_the_same_lambda_have_independent_environments(self):
        assert self.eval("""
        (begin
          (define (make-value value) (lambda () value))
          (define first (make-value 1))
          (define second (make-value 2))
          (list (first) (second)))
        """) == pair(1, pair(2, None))

    def test_closures_keep_independent_mutable_state(self):
        assert self.eval("""
        (begin
          (define (make-counter)
            (let ((value 0))
              (lambda ()
                (set! value (+ value 1))
                value)))
          (define first (make-counter))
          (define second (make-counter))
          (list (first) (first) (second)))
        """) == pair(1, pair(2, pair(1, None)))

    def test_call(self):
        assert self.eval("(- 5 4)") == 1
        assert self.eval("(pair 1 ((lambda () 2)))") == pair(1, 2)
        pytest.raises(SyntaxError, self.eval, "(+ 1 . 2)")

    def test_define(self):
        assert self.eval("(begin (define foo 5) foo)") == 5
        pytest.raises(SyntaxError, self.eval, "(define)")
        pytest.raises(SyntaxError, self.eval, "(define foo)")
        pytest.raises(SyntaxError, self.eval, "(define foo 5 6)")
        pytest.raises(SyntaxError, self.eval, "(define (1 x) x)")

        assert self.eval("(begin (define (foo x) x) (foo 5))") == 5
        assert self.eval("(begin (define (foo)) (foo))") == None

        assert self.eval("(begin (define (foo . x) (first x)) (foo 1))") == 1
        assert self.eval("(begin (define (foo . x) (first x)) (foo 1 2))") == 1

    def test_mutually_recursive_internal_definitions(self):
        assert self.eval("""
                ((lambda (value)
                   (define (even-value? n)
                     (if (= n 0) #t (odd-value? (- n 1))))
                   (define (odd-value? n)
                     (if (= n 0) #f (even-value? (- n 1))))
                   (even-value? value))
                 10)
                """) is True

    def test_set_x(self):
        assert self.eval("""
        (begin
          (define foo 5)
          (define bar foo)
          (set! foo 6)
          (pair foo bar))""") == pair(6, 5)
        assert self.eval("(set! pair 10)") == 10
        pytest.raises(UnboundVariable, self.eval, "(set! var-not-exist 10)")
        vm = VM()
        vm.eval_string("(define value 0)")
        pytest.raises(SyntaxError, vm.eval_string, "(set! 1 (set! value 1))")
        assert vm.eval_string("value") == 0

    def test_let(self):
        assert self.eval("""
        (let ((a 3) (b 2))
          (+ a b)
          (- a b))""") == 1

        assert self.eval("""
        (begin
          (define a 5)
          (let ((a 10) (b a))
            (- a b)))""") == 5

        assert self.eval("(let () #t)") == True
        assert self.eval("(let ())") == None
        pytest.raises(SyntaxError, self.eval, "(let ((a 1 2)) a)")
        pytest.raises(SyntaxError, self.eval, "(let ((a 1) (a 2)) a)")

    def test_named_let(self):
        assert self.eval("""
            (let loop ((numbers '(1 2 3 4)) (sum 0))
              (if (null? numbers)
                  sum
                  (loop (cdr numbers) (+ sum (car numbers)))))
        """) == 10
        pytest.raises(SyntaxError, self.eval, "(let loop ((a 1) (a 2)) a)")

    def test_quote(self):
        pytest.raises(SyntaxError, self.eval, "(quote)")
        pytest.raises(SyntaxError, self.eval, "(quote 1 2)")

    def test_quasiquote(self):
        assert self.eval("`(list ,(+ 1 2) 4)") == self.eval("'(list 3 4)")
        assert self.eval("`(a ,@(list 1 2) b)") == self.eval("'(a 1 2 b)")
        assert self.eval("`(a . ,(+ 1 2))") == self.eval("'(a . 3)")
        assert self.eval("`(a `(b ,(+ 1 2)))") == self.eval(
            "'(a (quasiquote (b (unquote (+ 1 2)))))"
        )
        pytest.raises(SyntaxError, self.eval, "(quasiquote)")
        pytest.raises(SyntaxError, self.eval, "`,@'(a b)")
        pytest.raises(SyntaxError, self.eval, ",value")
        pytest.raises(SyntaxError, self.eval, ",@value")

    def test_do(self):
        assert self.eval("""
        (do ((a 6 b) (b 9 (remainder a b)))
            ((= b 0) a))""") == 3
        pytest.raises(SyntaxError, self.eval, "(do ((a 1) (a 2)) (#t))")

    def test_letrec_duplicate_binding(self):
        pytest.raises(SyntaxError, self.eval, "(letrec ((a 1) (a 2)) a)")

    def test_define_syntax_requires_transformer(self):
        pytest.raises(SyntaxError, self.eval, "(define-syntax name)")

    def test_cond(self):
        assert self.eval("""
        (cond (#f 5 6)
              ((> 7 8) (+ 3 4))
              ((< 7 8)))""") == True

        assert self.eval("""
        (cond (#f 5 6)
              ((> 7 8) (+ 3 4))
              ((< 7 8) (+ 5 6) (+ 6 7)))""") == 13

        assert self.eval("""
        (cond (#f 5 6)
              ((+ 2 3) => (lambda (x) (* x x)))
              (else 10))""") == 25

        assert self.eval("""
        (cond (#f 5 6)
              (else))""") == None

        assert self.eval("(cond (#f 1) (else 2))") == 2

        pytest.raises(SyntaxError, self.eval, "(cond)")
        pytest.raises(
            SyntaxError,
            self.eval,
            """
        (cond (else 5)
              (#t 6))""",
        )

    def test_case(self):
        assert self.eval(
            "(case (* 2 3) ((2 3 5 7) 'prime) ((1 4 6 8) 'composite))"
        ) == self.eval("'composite")
        assert self.eval("(case 'unknown ((a b) 1) (else 2))") == 2
        assert self.eval("(case 'unknown ((a b) 1))") is None
        pytest.raises(SyntaxError, self.eval, "(case 1 (else 1) ((1) 2))")
