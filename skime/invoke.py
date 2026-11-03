from .call_cc import Continuation
from .ctx import Context
from .errors import WrongArgNumber, WrongArgType
from .prim import ApplyPrimitive, Primitive
from .proc import Procedure
from .types.pair import Pair


class CallFrame(object):
    """A Scheme procedure invocation that needs bytecode execution."""

    __slots__ = ("context",)

    def __init__(self, context):
        self.context = context


class CallValue(object):
    """A primitive invocation that completed with an immediate value."""

    __slots__ = ("value",)

    def __init__(self, value):
        self.value = value


class ContextTransfer(BaseException):
    """A non-local transfer to a captured continuation context."""

    __slots__ = ("context",)

    def __init__(self, context):
        super().__init__(context)
        self.context = context


def invoke(proc, args, parent, vm):
    """Prepare or perform one call through the shared VM calling convention."""
    # Expand apply here instead of calling back into the VM, so that a
    # procedure invoked through apply runs in the caller's frame and apply in
    # tail position stays a proper tail call.
    while isinstance(proc, ApplyPrimitive):
        proc, args = proc.spread(args)

    if isinstance(proc, Procedure):
        proc.check_arity(len(args))
        ctx = Context(proc, proc.env.dup(), parent)
        for index in range(proc.fixed_argc):
            ctx.env.assign_local(index, args[index])
        if proc.fixed_argc != proc.argc:
            rest = None
            for value in reversed(args[proc.fixed_argc :]):
                rest = Pair(value, rest)
            ctx.env.assign_local(proc.fixed_argc, rest)
        return CallFrame(ctx)

    if isinstance(proc, Primitive):
        proc.check_arity(len(args))
        return CallValue(proc.call(vm, *args))

    if isinstance(proc, Continuation):
        if len(args) != 1:
            raise WrongArgNumber("Continuation expects exactly 1 argument")
        ctx = proc.ctx.clone()
        ctx.push(args[0])
        ctx.parent = parent
        raise ContextTransfer(ctx)

    raise WrongArgType("Not a skime callable: %s" % proc)
