# A Scheme expression is compiled into a Form. The Form object hold the
# bytecode of the expression. To evaluate the form, a new Context is set up.
# Instruction pointer and operand stack are held in the Context object.
# Local variables are held in an Environment object, which are chained
# through the lexical scope.

import os.path

from .compiler.compiler import Compiler
from .compiler.parser import parse
from .ctx import Context
from .env import Environment
from .insns import run
from .invoke import CallFrame, ContextTransfer, invoke
from .prim import load_primitives


class VM(object):
    def __init__(self):
        self.compiler = Compiler()

        self.env = Environment()
        load_primitives(self.env)

        self.ctx = Context(None, self.env, vm=self)
        self._run_depth = 0

        self.load(os.path.join(os.path.dirname(__file__), "scheme", "prim.scm"))

    def run(self, form):
        return form.eval(self.env, self)

    def load(self, path):
        io = open(path)
        content = io.read()
        io.close()

        return self.eval_string("(begin %s)" % content)

    def eval_string(self, script):
        return self.run(self.compiler.compile(parse(script), self.env))

    def apply(self, proc, args):
        try:
            result = invoke(proc, args, self.ctx, self)
        except ContextTransfer as transfer:
            if self._run_depth > 0:
                raise
            return self.run_context(transfer.context)

        if isinstance(result, CallFrame):
            return self.run_context(result.context)
        return result.value

    def run_context(self, ctx):
        self._run_depth += 1
        try:
            while True:
                try:
                    return run(ctx)
                except ContextTransfer as transfer:
                    if self._run_depth > 1:
                        raise
                    ctx = transfer.context
        finally:
            self._run_depth -= 1
