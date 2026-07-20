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
