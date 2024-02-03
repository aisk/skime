import readline
from skime.compiler.compiler import Compiler
from skime.compiler.parser import parse
from skime.vm import VM
from skime.errors import Error


def main():
    print("Welcome to Skime!")
    compiler = Compiler()
    vm = VM()
    while True:
        code = input('-> ')
        try:
            proc = compiler.compile(parse(code), vm.env)
            print('=>', vm.run(proc))
        except Error as e:
            print('!>', e)


if __name__ == '__main__':
    main()
