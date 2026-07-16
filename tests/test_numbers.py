import math

import pytest
from helper import HelperVM

from skime.errors import MiscError, WrongArgNumber, WrongArgType


class TestArithmetic(HelperVM):
    def test_basic_arithmetic(self):
        assert self.eval("(+ 1 2 3)") == 6
        assert self.eval("(+ -1 1)") == 0
        assert self.eval("(+ 1)") == 1
        assert self.eval("(+)") == 0
        pytest.raises(WrongArgType, self.eval, '(+ 1 "foo")')

        assert self.eval("(- 3 2 1)") == 0
        assert self.eval("(- 2)") == -2
        with pytest.raises(WrongArgNumber) as error:
            self.eval("(-)")
        assert str(error.value) == "minus expects at least 1 arguments, but got 0"

        assert self.eval("(* -2 -3)") == 6
        assert self.eval("(*)") == 1
        assert self.eval("(/ 6 3)") == 2
        assert self.eval("(/ 2)") == 0.5
        pytest.raises(WrongArgNumber, self.eval, "(/)")

    def test_integer_arithmetic(self):
        assert self.eval("(quotient -5 2)") == -2
        assert self.eval("(remainder -5 -2)") == -1
        assert self.eval("(modulo -5 2)") == 1
        assert self.eval("(gcd)") == 0
        assert self.eval("(gcd -18 24)") == 6
        assert self.eval("(lcm)") == 1
        assert self.eval("(lcm 0 0)") == 0

    def test_numeric_comparisons(self):
        assert self.eval("(= 1 1 1)") is True
        assert self.eval("(= 1 1 2)") is False
        assert self.eval("(< 1 2 3 4 5)") is True
        assert self.eval("(< 1 2 3 4 4)") is False
        assert self.eval("(> 5 4 3 2 1)") is True
        assert self.eval("(> 5 4 3 1 1)") is False
        assert self.eval("(<= 1 2 3 4 4)") is True
        assert self.eval("(<= 2 1)") is False
        assert self.eval("(>= 5 4 3 1 1)") is True
        assert self.eval("(>= 1 2)") is False

    def test_numeric_bounds_and_signs(self):
        assert self.eval("(max -3 8 2)") == 8
        assert self.eval("(min -3 8 2)") == -3
        assert self.eval("(zero? 0)") is True
        assert self.eval("(positive? 2)") is True
        assert self.eval("(negative? -2)") is True
        assert self.eval("(even? 4)") is True
        assert self.eval("(odd? 5)") is True


class TestNumericTypes(HelperVM):
    def test_numeric_predicates(self):
        assert self.eval("(number? 2+3i)") is True
        assert self.eval("(complex? 2+3i)") is True
        assert self.eval("(real? 2.5)") is True
        assert self.eval("(rational? 2.5)") is True
        assert self.eval("(integer? 2)") is True
        assert self.eval("(exact? 2)") is True
        assert self.eval("(inexact? 2.0)") is True

    def test_booleans_are_not_numbers(self):
        assert self.eval("(number? #t)") is False
        assert self.eval("(integer? #f)") is False
        pytest.raises(WrongArgType, self.eval, "(+ 1 #t)")
        pytest.raises(WrongArgType, self.eval, "(< 0 #f)")


class TestNumericFunctions(HelperVM):
    def test_rounding(self):
        assert self.eval("(floor 2.9)") == 2
        assert self.eval("(ceiling 2.1)") == 3
        assert self.eval("(truncate -2.9)") == -2
        assert self.eval("(round 2.5)") == 2
        assert self.eval("(round 3.5)") == 4

    def test_transcendental_functions(self):
        assert self.eval("(abs -3)") == 3
        assert self.eval("(sqrt 9)") == 3
        assert self.eval("(expt 2 5)") == 32
        assert self.eval("(exp 0)") == 1
        assert self.eval("(log 1)") == 0
        assert self.eval("(sin 0)") == 0
        assert self.eval("(cos 0)") == 1
        assert self.eval("(tan 0)") == 0
        assert self.eval("(asin 0)") == 0
        assert self.eval("(acos 1)") == 0
        assert self.eval("(atan 1)") == pytest.approx(math.atan(1))
        assert self.eval("(atan 1 -1)") == pytest.approx(math.atan2(1, -1))

    def test_complex_number_accessors(self):
        assert self.eval("(make-rectangular 3 4)") == 3 + 4j
        assert self.eval("(real-part 3+4i)") == 3
        assert self.eval("(imag-part 3+4i)") == 4
        assert self.eval("(magnitude 3+4i)") == 5
        assert self.eval("(angle -1)") == pytest.approx(math.pi)
        assert self.eval("(magnitude (make-polar 2 1))") == pytest.approx(2)


class TestNumberConversion(HelperVM):
    def test_number_to_string(self):
        assert self.eval("(number->string 5 2)") == "101"
        assert self.eval("(number->string 0 2)") == "0"
        assert self.eval("(number->string 255 16)") == "FF"
        pytest.raises(MiscError, self.eval, "(number->string 1 3)")

    def test_string_to_number(self):
        assert self.eval('(string->number "")') is False
        assert self.eval('(string->number "FF" 16)') == 255
        assert self.eval('(string->number "not-a-number")') is False

    def test_complex_number_string_round_trip(self):
        assert self.eval("(string->number (number->string 3+4i))") == 3 + 4j
        assert self.eval("(string->number (number->string 3-4i))") == 3 - 4j
        pytest.raises(WrongArgType, self.eval, "(number->string #t)")
