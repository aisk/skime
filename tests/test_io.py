import pytest
from helper import HelperVM

from skime.errors import WrongArgType
from skime.vm import VM


class TestIO(HelperVM):
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
