try:
    # `readline` is not part of the standard library on Windows.  Import it
    # when available so POSIX users keep line editing/history support, but do
    # not prevent the REPL from starting elsewhere.
    import readline  # noqa: F401
except ImportError:
    pass

from skime.compiler.compiler import Compiler
from skime.compiler.parser import parse
from skime.errors import Error
from skime.vm import VM


def main():
    print("Welcome to Skime!")
    compiler = Compiler()
    vm = VM()
    while True:
        try:
            code = input("-> ")
        except (EOFError, KeyboardInterrupt):
            print()
            return
        try:
            proc = compiler.compile(parse(code), vm.env)
            print("=>", vm.run(proc))
        except Error as e:
            print("!>", e)


if __name__ == "__main__":
    main()
