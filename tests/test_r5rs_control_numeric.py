import math

import pytest
from helper import HelperVM

from skime.errors import MiscError, WrongArgType
from skime.vm import VM


class TestR5RSControl(HelperVM):
    def test_for_each(self):
        assert self.eval("""
                (begin
                  (define total 0)
                  (for-each (lambda (value) (set! total (+ total value)))
                            '(1 2 3 4))
                  total)
                """) == 10
        pytest.raises(MiscError, self.eval, "(for-each + '(1 2) '(3))")

    def test_load(self, tmp_path):
        source = tmp_path / "loaded.scm"
        source.write_text("(define loaded-value 42) loaded-value")
        vm = VM()

        assert vm.eval_string('(load "%s")' % source) == 42

    def test_default_output_procedures(self, capsys):
        self.eval("""
            (begin
              (display "hello")
              (display #\\space)
              (display '(1 "two"))
              (newline)
              (write "quoted")
              (write-char #\\!))
            """)

        assert capsys.readouterr().out == 'hello (1 "two")\n"quoted"!'
        pytest.raises(WrongArgType, self.eval, "(write-char 1)")


class TestR5RSNumbers(HelperVM):
    def test_booleans_are_not_numbers(self):
        assert self.eval("(number? #t)") is False
        assert self.eval("(integer? #f)") is False
        pytest.raises(WrongArgType, self.eval, "(+ 1 #t)")
        pytest.raises(WrongArgType, self.eval, "(< 0 #f)")

    def test_complex_number_accessors(self):
        assert self.eval("(make-rectangular 3 4)") == 3 + 4j
        assert self.eval("(real-part 3+4i)") == 3
        assert self.eval("(imag-part 3+4i)") == 4
        assert self.eval("(magnitude 3+4i)") == 5
        assert self.eval("(angle -1)") == pytest.approx(math.pi)
        assert self.eval("(magnitude (make-polar 2 1))") == pytest.approx(2)

    def test_complex_number_string_round_trip(self):
        assert self.eval("(string->number (number->string 3+4i))") == 3 + 4j
        assert self.eval("(string->number (number->string 3-4i))") == 3 - 4j
        pytest.raises(WrongArgType, self.eval, "(number->string #t)")
