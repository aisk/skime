from skime.vm import VM


class HelperVM(object):
    def eval(self, code):
        return VM().eval_string(code)
