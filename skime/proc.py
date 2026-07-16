from io import StringIO

from .compiler.disasm import disasm
from .errors import WrongArgNumber


class ProcedureTemplate(object):
    """Compiled procedure code that can create independent closures."""

    def __init__(self, builder, bytecode):
        # This environment describes the procedure's local slots. It belongs
        # to the template and must never be rebound to a runtime environment.
        self.env = builder.env
        self.bytecode = bytecode
        self.argc = len(builder.args)
        if builder.rest_arg:
            self.fixed_argc = self.argc - 1
        else:
            self.fixed_argc = self.argc
        self.literals = list(builder.literals)

    def close(self, lexical_parent):
        "Create a runtime closure over lexical_parent."
        env = self.env.dup()
        env.parent = lexical_parent
        return Procedure(self, env)


class Procedure(object):
    """A runtime closure created from a compiled procedure template."""

    def __init__(self, template, env):
        self.template = template
        self.env = env
        self.bytecode = template.bytecode
        self.argc = template.argc
        self.fixed_argc = template.fixed_argc
        self.literals = template.literals

    def check_arity(self, argc):
        if self.fixed_argc == self.argc:
            if argc != self.argc:
                raise WrongArgNumber(
                    "Expecting %d arguments, but got %d" % (self.argc, argc)
                )
        else:
            if argc < self.fixed_argc:
                raise WrongArgNumber(
                    "Expecting at least %d arguments, but got %d"
                    % (self.fixed_argc, argc)
                )

    def disasm(self):
        "Show the disassemble of the instructions of the proc. Useful for debug."
        io = StringIO()
        io.write("=" * 60)
        io.write("\n")
        io.write("Diasassemble of proc at %X\n" % id(self))

        io.write("arguments: ")
        args = [self.env.get_name(i) for i in range(self.argc)]
        if self.fixed_argc != self.argc:
            args[-1] = "*" + args[-1]
        io.write(", ".join(args))
        io.write("\n")

        io.write("literals:\n")
        for i in range(len(self.literals)):
            io.write("%4d: %s\n" % (i, self.literals[i]))

        io.write("\ninstructions:\n")
        io.write("-" * 50)
        io.write("\n")

        disasm(io, self)

        content = io.getvalue()
        io.close()

        return content
