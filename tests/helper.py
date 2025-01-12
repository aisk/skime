import sys
from os.path import abspath, dirname, join

sys.path.insert(0, abspath(join(dirname(__file__), "..")))

from skime.compiler.compiler import Compiler
from skime.compiler.parser import parse
from skime.vm import VM


class HelperVM(object):
    def eval(self, code):
        compiler = Compiler()
        vm = VM()
        proc = compiler.compile(parse(code), vm.env)
        return vm.run(proc)
