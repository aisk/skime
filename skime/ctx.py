class Context(object):
    def __init__(self, form, env, parent=None, vm=None):
        self.form = form
        self.env = env
        self.parent = parent
        if parent is not None:
            self.vm = parent.vm
        elif vm is not None:
            self.vm = vm
        else:
            raise ValueError("A root context requires a VM")

        self.ip = 0
        if self.form is not None:
            self.bytecode = form.bytecode
        else:
            self.bytecode = []
        self.stack = []

    def clone(self):
        "Make a clone of the context object."
        ctx = Context(self.form, self.env, self.parent, vm=self.vm)
        ctx.ip = self.ip
        ctx.stack = list(self.stack)
        return ctx

    def push(self, val):
        "Push a value onto the stack."
        self.stack.append(val)

    def pop(self):
        "Pop a value from the top of the stack."
        return self.stack.pop()

    def pop_n(self, n):
        "Remove n values from the top of the stack."
        if n > 0:
            del self.stack[-n:]

    def top(self, idx=1):
        "Get a value from the stack."
        return self.stack[-idx]

    def insert(self, idx, val):
        """\
        Insert value into particular position.
          [1, 2, 3] => insert(-1, 5) => [1, 2, 5, 3]
        """
        self.stack.insert(idx, val)

    def insert_n(self, idx, val):
        """\
        Insert a list of values into particular position.
          [1, 2] => insert(-1, [7, 8]) => [1, 7, 8, 2]
        """
        self.stack[idx:idx] = val

    def __str__(self):
        return "<Context stack_size=%d, ip=%d>" % (len(self.stack), self.ip)
