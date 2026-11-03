import builtins

import pytest

from skime.__main__ import main


@pytest.mark.parametrize("exception", [EOFError, KeyboardInterrupt])
def test_repl_exits_cleanly_when_input_is_interrupted(monkeypatch, capsys, exception):
    def interrupt_input(_prompt):
        raise exception

    monkeypatch.setattr(builtins, "input", interrupt_input)

    main()

    assert capsys.readouterr().out == "Welcome to Skime!\n\n"


def test_repl_reports_errors_and_continues(monkeypatch, capsys):
    inputs = iter(
        [
            "(#x)",
            "²",
            "(define (q n) (if (= n 0) 0 (let () (q (- n 1)))))",
            "(q 1)",
            "(define (even-v? n) (if (= n 0) #t (odd-v? (- n 1))))",
            "(define (odd-v? n) (if (= n 0) #f (even-v? (- n 1))))",
            "(even-v? 4)",
        ]
    )

    def fake_input(_prompt):
        try:
            return next(inputs)
        except StopIteration:
            raise EOFError

    monkeypatch.setattr(builtins, "input", fake_input)

    main()

    lines = capsys.readouterr().out.splitlines()
    assert lines[0] == "Welcome to Skime!"
    assert lines[1].startswith("!> ")
    assert lines[2] == "!> Unbound variable ²"
    assert lines[4] == "=> 0"
    assert lines[7] == "=> #t"


def test_repl_prints_scheme_values_and_survives_runtime_errors(monkeypatch, capsys):
    inputs = iter(["'()", '(list #t "a" #\\b)', "(/ 1 0)", '(load "/no/such/file")'])

    def fake_input(_prompt):
        try:
            return next(inputs)
        except StopIteration:
            raise EOFError

    monkeypatch.setattr(builtins, "input", fake_input)

    main()

    lines = capsys.readouterr().out.splitlines()
    assert lines[1] == "=> ()"
    assert lines[2] == '=> (#t "a" #\\b)'
    assert lines[3] == "!> Division by zero"
    assert lines[4].startswith("!> No such file or directory")
