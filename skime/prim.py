import cmath
import math
from functools import wraps
from itertools import product

from .call_cc import Continuation
from .errors import MiscError, WrongArgNumber, WrongArgType
from .proc import Procedure
from .types.character import Character
from .types.pair import Pair as pair
from .types.symbol import Symbol as sym
from .types.vector import Vector


class Primitive(object):
    """\
    Base class for all skime primitives.

    When primitive is called with arguments (1, 2, 3), the arity is first checked
    by calling prim.check_arity(3). Then the vm object is inserted as the first
    argument and the primitive called: prim.call(vm, 1, 2, 3). The vm is always
    the first argument of all primitives, but not count as argc.
    """

    def check_arity(self, argc):
        "Check whether this primitive is OK to execute with argc arguments."
        raise TypeError("check_arity is not implemented in abstract class Primitive")

    def call(self, *args):
        "Call the primitive with args."
        raise TypeError("call is not implemented in abstract class Primitive")


class PyPrimitive(Primitive):
    "Primitive wrapping a Python callable."

    def __init__(self, proc, arity):
        """\
        Create a PyPrimitive.

          proc  should be a Python callable.
          arity can be a tuple specifying the min and max number of arguments.
                either min or max or both can be -1, which means it is of no
                bound.
        """
        self.proc = proc
        self.arity = arity

    def check_arity(self, argc):
        min, max = self.arity
        if min > 0 and argc < min:
            raise WrongArgNumber(
                "%s expects at least %d arguments, but got %d"
                % (self.proc.__name__, min, argc)
            )
        if max > 0 and argc > max:
            raise WrongArgNumber(
                "%s expects at most %d arguments, but got %d"
                % (self.proc.__name__, max, argc)
            )

    def call(self, *args):
        return self.proc(*args)

    def __str__(self):
        return "<skime primitive => %s>" % self.proc.__name__


class PyCallable(Primitive):
    def __init__(self, proc):
        self.proc = proc

    def check_arity(self, argc):
        return True

    def call(self, vm, *args):
        return self.proc(*args)


def load_primitives(env):
    "Load primitives into an Environment."
    env.alloc_local("+", PyPrimitive(plus, (-1, -1)))
    env.alloc_local("-", PyPrimitive(minus, (1, -1)))
    env.alloc_local("*", PyPrimitive(mul, (-1, -1)))
    env.alloc_local("/", PyPrimitive(div, (1, -1)))
    env.alloc_local("=", PyPrimitive(equal, (-1, -1)))
    env.alloc_local("<", PyPrimitive(less, (2, -1)))
    env.alloc_local(">", PyPrimitive(more, (2, -1)))
    env.alloc_local("<=", PyPrimitive(less_equal, (2, -1)))
    env.alloc_local(">=", PyPrimitive(more_equal, (2, -1)))

    env.alloc_local("equal?", PyPrimitive(prim_equal, (2, 2)))
    env.alloc_local("eq?", PyPrimitive(prim_eq, (2, 2)))
    env.alloc_local("eqv?", PyPrimitive(prim_eqv, (2, 2)))

    env.alloc_local("log", PyPrimitive(prim_log, (1, 1)))
    env.alloc_local("exp", PyPrimitive(prim_exp, (1, 1)))
    env.alloc_local("sin", PyPrimitive(prim_sin, (1, 1)))
    env.alloc_local("cos", PyPrimitive(prim_cos, (1, 1)))
    env.alloc_local("tan", PyPrimitive(prim_tan, (1, 1)))
    env.alloc_local("abs", PyPrimitive(prim_abs, (1, 1)))

    env.alloc_local("not", PyPrimitive(prim_not, (1, 1)))

    env.alloc_local("first", PyPrimitive(prim_first, (1, 1)))
    env.alloc_local("rest", PyPrimitive(prim_rest, (1, 1)))
    env.alloc_local("pair", PyPrimitive(prim_pair, (2, 2)))
    env.alloc_local("car", PyPrimitive(prim_first, (1, 1)))
    env.alloc_local("cdr", PyPrimitive(prim_rest, (1, 1)))
    env.alloc_local("cons", PyPrimitive(prim_pair, (2, 2)))
    env.alloc_local("set-first!", PyPrimitive(prim_set_first_x, (2, 2)))
    env.alloc_local("set-car!", PyPrimitive(prim_set_first_x, (2, 2)))
    env.alloc_local("set-rest!", PyPrimitive(prim_set_rest_x, (2, 2)))
    env.alloc_local("set-cdr!", PyPrimitive(prim_set_rest_x, (2, 2)))

    env.alloc_local("list", PyPrimitive(prim_list, (-1, -1)))
    env.alloc_local("length", PyPrimitive(prim_length, (1, 1)))
    env.alloc_local("append", PyPrimitive(prim_append, (-1, -1)))
    env.alloc_local("reverse", PyPrimitive(prim_reverse, (1, 1)))
    env.alloc_local("list-tail", PyPrimitive(prim_list_tail, (2, 2)))
    env.alloc_local("list-ref", PyPrimitive(prim_list_ref, (2, 2)))
    env.alloc_local("memq", PyPrimitive(prim_memq, (2, 2)))
    env.alloc_local("memv", PyPrimitive(prim_memv, (2, 2)))
    env.alloc_local("member", PyPrimitive(prim_member, (2, 2)))
    env.alloc_local("assq", PyPrimitive(prim_assq, (2, 2)))
    env.alloc_local("assv", PyPrimitive(prim_assv, (2, 2)))
    env.alloc_local("assoc", PyPrimitive(prim_assoc, (2, 2)))

    for length in range(2, 5):
        for operations in product("ad", repeat=length):
            name = "c%sr" % "".join(operations)
            env.alloc_local(name, PyPrimitive(make_cxr(operations), (1, 1)))

    for t, name in [
        (bool, "boolean?"),
        (pair, "pair?"),
        (sym, "symbol?"),
        (str, "string?"),
        (Character, "char?"),
        (Vector, "vector?"),
        ((int, int, float, complex), "number?"),
        ((int, int, float), "rational?"),
        ((int, int, float), "real?"),
        ((int, int, float, complex), "complex?"),
        ((int, int), "integer?"),
        ((Procedure, Primitive, Continuation), "procedure?"),
    ]:
        env.alloc_local(name, PyPrimitive(make_type_predict(t), (1, 1)))

    env.alloc_local("exact?", PyPrimitive(prim_exact_p, (1, 1)))
    env.alloc_local("inexact?", PyPrimitive(prim_inexact_p, (1, 1)))
    env.alloc_local("zero?", PyPrimitive(prim_zero_p, (1, 1)))
    env.alloc_local("positive?", PyPrimitive(prim_positive_p, (1, 1)))
    env.alloc_local("negative?", PyPrimitive(prim_negative_p, (1, 1)))
    env.alloc_local("even?", PyPrimitive(prim_even_p, (1, 1)))
    env.alloc_local("odd?", PyPrimitive(prim_odd_p, (1, 1)))
    env.alloc_local("max", PyPrimitive(prim_max, (1, -1)))
    env.alloc_local("min", PyPrimitive(prim_min, (1, -1)))
    env.alloc_local("quotient", PyPrimitive(prim_quotient, (2, 2)))
    env.alloc_local("modulo", PyPrimitive(prim_modulo, (2, 2)))
    env.alloc_local("remainder", PyPrimitive(prim_remainder, (2, 2)))
    env.alloc_local("gcd", PyPrimitive(prim_gcd, (-1, -1)))
    env.alloc_local("lcm", PyPrimitive(prim_lcm, (-1, -1)))
    env.alloc_local("floor", PyPrimitive(prim_floor, (1, 1)))
    env.alloc_local("ceiling", PyPrimitive(prim_ceiling, (1, 1)))
    env.alloc_local("truncate", PyPrimitive(prim_truncate, (1, 1)))
    env.alloc_local("round", PyPrimitive(prim_round, (1, 1)))
    env.alloc_local("asin", PyPrimitive(prim_asin, (1, 1)))
    env.alloc_local("acos", PyPrimitive(prim_acos, (1, 1)))
    env.alloc_local("atan", PyPrimitive(prim_atan, (1, 2)))
    env.alloc_local("sqrt", PyPrimitive(prim_sqrt, (1, 1)))
    env.alloc_local("expt", PyPrimitive(prim_expt, (2, 2)))
    env.alloc_local("make-rectangular", PyPrimitive(prim_make_rectangular, (2, 2)))
    env.alloc_local("make-polar", PyPrimitive(prim_make_polar, (2, 2)))
    env.alloc_local("real-part", PyPrimitive(prim_real_part, (1, 1)))
    env.alloc_local("imag-part", PyPrimitive(prim_imag_part, (1, 1)))
    env.alloc_local("magnitude", PyPrimitive(prim_magnitude, (1, 1)))
    env.alloc_local("angle", PyPrimitive(prim_angle, (1, 1)))
    env.alloc_local("null?", PyPrimitive(prim_null_p, (1, 1)))
    env.alloc_local("list?", PyPrimitive(prim_list_p, (1, 1)))

    env.alloc_local("apply", PyPrimitive(prim_apply, (1, -1)))
    env.alloc_local("map", PyPrimitive(prim_map, (2, -1)))
    env.alloc_local("for-each", PyPrimitive(prim_for_each, (2, -1)))
    env.alloc_local("load", PyPrimitive(prim_load, (1, 1)))

    env.alloc_local("string->symbol", PyPrimitive(prim_string_to_symbol, (1, 1)))
    env.alloc_local("symbol->string", PyPrimitive(prim_symbol_to_string, (1, 1)))
    env.alloc_local("number->string", PyPrimitive(prim_number_to_string, (1, 2)))
    env.alloc_local("string->number", PyPrimitive(prim_string_to_number, (1, 2)))
    env.alloc_local("string-append", PyPrimitive(prim_string_append, (-1, -1)))
    env.alloc_local("make-string", PyPrimitive(prim_make_string, (1, 2)))
    env.alloc_local("string", PyPrimitive(prim_string, (-1, -1)))
    env.alloc_local("string-length", PyPrimitive(prim_string_length, (1, 1)))
    env.alloc_local("string-ref", PyPrimitive(prim_string_ref, (2, 2)))
    env.alloc_local("substring", PyPrimitive(prim_substring, (3, 3)))
    env.alloc_local("string-copy", PyPrimitive(prim_string_copy, (1, 1)))
    env.alloc_local("string->list", PyPrimitive(prim_string_to_list, (1, 1)))
    env.alloc_local("list->string", PyPrimitive(prim_list_to_string, (1, 1)))

    for name, relation, case_insensitive in [
        ("string=?", "eq", False),
        ("string<?", "lt", False),
        ("string>?", "gt", False),
        ("string<=?", "le", False),
        ("string>=?", "ge", False),
        ("string-ci=?", "eq", True),
        ("string-ci<?", "lt", True),
        ("string-ci>?", "gt", True),
        ("string-ci<=?", "le", True),
        ("string-ci>=?", "ge", True),
    ]:
        env.alloc_local(
            name,
            PyPrimitive(
                make_string_comparison(name, relation, case_insensitive), (2, -1)
            ),
        )

    for name, relation, case_insensitive in [
        ("char=?", "eq", False),
        ("char<?", "lt", False),
        ("char>?", "gt", False),
        ("char<=?", "le", False),
        ("char>=?", "ge", False),
        ("char-ci=?", "eq", True),
        ("char-ci<?", "lt", True),
        ("char-ci>?", "gt", True),
        ("char-ci<=?", "le", True),
        ("char-ci>=?", "ge", True),
    ]:
        env.alloc_local(
            name,
            PyPrimitive(
                make_char_comparison(name, relation, case_insensitive), (2, -1)
            ),
        )

    env.alloc_local("char-alphabetic?", PyPrimitive(prim_char_alphabetic_p, (1, 1)))
    env.alloc_local("char-numeric?", PyPrimitive(prim_char_numeric_p, (1, 1)))
    env.alloc_local("char-whitespace?", PyPrimitive(prim_char_whitespace_p, (1, 1)))
    env.alloc_local("char-upper-case?", PyPrimitive(prim_char_upper_case_p, (1, 1)))
    env.alloc_local("char-lower-case?", PyPrimitive(prim_char_lower_case_p, (1, 1)))
    env.alloc_local("char->integer", PyPrimitive(prim_char_to_integer, (1, 1)))
    env.alloc_local("integer->char", PyPrimitive(prim_integer_to_char, (1, 1)))
    env.alloc_local("char-upcase", PyPrimitive(prim_char_upcase, (1, 1)))
    env.alloc_local("char-downcase", PyPrimitive(prim_char_downcase, (1, 1)))
    env.alloc_local("make-vector", PyPrimitive(prim_make_vector, (1, 2)))
    env.alloc_local("vector", PyPrimitive(prim_vector, (-1, -1)))
    env.alloc_local("vector-length", PyPrimitive(prim_vector_length, (1, 1)))
    env.alloc_local("vector-ref", PyPrimitive(prim_vector_ref, (2, 2)))
    env.alloc_local("vector-set!", PyPrimitive(prim_vector_set_x, (3, 3)))
    env.alloc_local("vector->list", PyPrimitive(prim_vector_to_list, (1, 1)))
    env.alloc_local("list->vector", PyPrimitive(prim_list_to_vector, (1, 1)))
    env.alloc_local("vector-fill!", PyPrimitive(prim_vector_fill_x, (2, 2)))


def type_error_decorator(meth):
    "Decorate method to catch Python TypeError and raise skime WrongArgType"

    @wraps(meth)
    def new_meth(*args):
        try:
            return meth(*args)
        except TypeError as e:
            raise WrongArgType(*e.args)

    return new_meth


@type_error_decorator
def plus(vm, *args):
    type_check_all(args, (int, float, complex))
    return sum(args)


@type_error_decorator
def mul(vm, *args):
    type_check_all(args, (int, float, complex))
    res = 1
    for x in args:
        res *= x
    return res


@type_error_decorator
def minus(vm, num, *args):
    type_check_all((num,) + args, (int, float, complex))
    if len(args) == 0:
        return -num
    for x in args:
        num -= x
    return num


@type_error_decorator
def div(vm, num, *args):
    type_check_all((num,) + args, (int, float, complex))
    if len(args) == 0:
        return 1.0 / num
    if isinstance(num, int):
        num = float(num)
    for x in args:
        num /= x
    return num


def equal(vm, *args):
    if len(args) < 2:
        return True
    a = args[0]
    b = args[1]
    type_check(a, (int, int, float, complex))
    type_check(b, (int, int, float, complex))
    if a != b:
        return False
    for x in args[2:]:
        type_check(x, (int, int, float, complex))
        if x != a:
            return False
    return True


def less(vm, a, b, *args):
    type_check_all((a, b) + args, (int, float))
    if a >= b:
        return False
    for x in args:
        if b >= x:
            return False
        b = x
    return True


def more(vm, a, b, *args):
    type_check_all((a, b) + args, (int, float))
    if a <= b:
        return False
    for x in args:
        if b <= x:
            return False
        b = x
    return True


def less_equal(vm, a, b, *args):
    type_check_all((a, b) + args, (int, float))
    if a > b:
        return False
    for x in args:
        if b > x:
            return False
        b = x
    return True


def more_equal(vm, a, b, *args):
    type_check_all((a, b) + args, (int, float))
    if a < b:
        return False
    for x in args:
        if b < x:
            return False
        b = x
    return True


def prim_positive_p(vm, arg):
    type_check(arg, (int, int, float))
    return arg > 0


def prim_negative_p(vm, arg):
    type_check(arg, (int, int, float))
    return arg < 0


def prim_odd_p(vm, arg):
    type_check(arg, (int, int))
    return arg % 2 != 0


def prim_even_p(vm, arg):
    type_check(arg, (int, int))
    return arg % 2 == 0


def prim_max(vm, *args):
    type_check_all(args, (int, float))
    return max(args)


def prim_min(vm, *args):
    type_check_all(args, (int, float))
    return min(args)


def prim_quotient(vm, a, b):
    type_check(a, (int, int))
    type_check(b, (int, int))
    quotient = abs(a) // abs(b)
    if (a < 0) != (b < 0):
        quotient = -quotient
    return quotient


# remainder has the same sign as a
def prim_remainder(vm, a, b):
    type_check(a, (int, int))
    type_check(b, (int, int))
    return a - prim_quotient(vm, a, b) * b


# modulo has the same sign as b
def prim_modulo(vm, a, b):
    type_check(a, (int, int))
    type_check(b, (int, int))
    return a % b


def gcd(a, b):
    while b != 0:
        b, a = a % b, b
    return a


def lcm(a, b):
    if a == 0 or b == 0:
        return 0
    return abs(a // gcd(a, b) * b)


def prim_gcd(vm, *args):
    if len(args) == 0:
        return 0
    if len(args) == 1:
        type_check(args[0], (int, int))
        return abs(args[0])
    a, b, args = args[0], args[1], args[2:]
    type_check(a, (int, int))
    type_check(b, (int, int))
    g = gcd(a, b)
    for x in args:
        type_check(x, (int, int))
        g = gcd(g, x)
    return abs(g)


def prim_lcm(vm, *args):
    if len(args) == 0:
        return 1
    if len(args) == 1:
        type_check(args[0], (int, int))
        return abs(args[0])
    a, b, args = args[0], args[1], args[2:]
    type_check(a, (int, int))
    type_check(b, (int, int))
    l = lcm(a, b)
    for x in args:
        type_check(x, (int, int))
        l = lcm(l, x)
    return abs(l)


@type_error_decorator
def prim_floor(vm, a):
    type_check(a, (int, float))
    return math.floor(a)


@type_error_decorator
def prim_ceiling(vm, a):
    type_check(a, (int, float))
    return math.ceil(a)


@type_error_decorator
def prim_truncate(vm, a):
    type_check(a, (int, float))
    if a > 0:
        return math.floor(a)
    return math.ceil(a)


@type_error_decorator
def prim_round(vm, a):
    type_check(a, (int, float))
    return round(a)


@type_error_decorator
def prim_exp(vm, arg):
    type_check(arg, (int, float, complex))
    return cmath.exp(arg) if isinstance(arg, complex) else math.exp(arg)


@type_error_decorator
def prim_log(vm, arg):
    type_check(arg, (int, float, complex))
    return cmath.log(arg) if isinstance(arg, complex) or arg < 0 else math.log(arg)


@type_error_decorator
def prim_sin(vm, arg):
    type_check(arg, (int, float, complex))
    return cmath.sin(arg) if isinstance(arg, complex) else math.sin(arg)


@type_error_decorator
def prim_cos(vm, arg):
    type_check(arg, (int, float, complex))
    return cmath.cos(arg) if isinstance(arg, complex) else math.cos(arg)


@type_error_decorator
def prim_tan(vm, arg):
    type_check(arg, (int, float, complex))
    return cmath.tan(arg) if isinstance(arg, complex) else math.tan(arg)


@type_error_decorator
def prim_asin(vm, arg):
    type_check(arg, (int, float, complex))
    if isinstance(arg, complex) or not -1 <= arg <= 1:
        return cmath.asin(arg)
    return math.asin(arg)


@type_error_decorator
def prim_acos(vm, arg):
    type_check(arg, (int, float, complex))
    if isinstance(arg, complex) or not -1 <= arg <= 1:
        return cmath.acos(arg)
    return math.acos(arg)


@type_error_decorator
def prim_atan(vm, arg, *arg2):
    type_check(arg, (int, float, complex))
    if len(arg2) == 0:
        return cmath.atan(arg) if isinstance(arg, complex) else math.atan(arg)
    type_check_all((arg, arg2[0]), (int, float))
    return math.atan2(arg, arg2[0])


@type_error_decorator
def prim_sqrt(vm, arg):
    type_check(arg, (int, float, complex))
    if isinstance(arg, complex) or arg < 0:
        return cmath.sqrt(arg)
    return math.sqrt(arg)


@type_error_decorator
def prim_expt(vm, a, b):
    type_check_all((a, b), (int, float, complex))
    return a**b


def prim_make_rectangular(vm, real, imag):
    type_check_all((real, imag), (int, float))
    return complex(real, imag)


def prim_make_polar(vm, magnitude, angle):
    type_check_all((magnitude, angle), (int, float))
    return cmath.rect(magnitude, angle)


def prim_real_part(vm, number):
    type_check(number, (int, float, complex))
    return number.real if isinstance(number, complex) else number


def prim_imag_part(vm, number):
    type_check(number, (int, float, complex))
    return number.imag if isinstance(number, complex) else 0


def prim_magnitude(vm, number):
    type_check(number, (int, float, complex))
    return abs(number)


def prim_angle(vm, number):
    type_check(number, (int, float, complex))
    return cmath.phase(number)


@type_error_decorator
def prim_abs(vm, arg):
    type_check(arg, (int, float, complex))
    return abs(arg)


def prim_not(vm, arg):
    if arg is False:
        return True
    return False


def prim_first(vm, arg):
    type_check(arg, pair)
    return arg.first


def prim_rest(vm, arg):
    type_check(arg, pair)
    return arg.rest


def prim_pair(vm, a, b):
    return pair(a, b)


def prim_set_first_x(vm, arg, val):
    type_check(arg, pair)
    arg.first = val


def prim_set_rest_x(vm, arg, val):
    type_check(arg, pair)
    arg.rest = val


def prim_exact_p(vm, arg):
    if matches_type(arg, int):
        return True
    # python complex are always inexact
    if isinstance(arg, (float, complex)):
        return False
    raise WrongArgType("Expecting a number, but got %s" % arg)


def prim_inexact_p(vm, arg):
    return not prim_exact_p(vm, arg)


def prim_zero_p(vm, arg):
    type_check(arg, (int, int, complex, float))
    return arg == 0


def prim_null_p(vm, arg):
    return arg is None


# list?, detect circular list
def prim_list_p(vm, val):
    obj1 = val
    obj2 = val
    while True:
        if obj1 is None:
            return True
        if not isinstance(obj1, pair):
            return False

        obj1 = obj1.rest
        if obj1 is None:
            return True
        if not isinstance(obj1, pair):
            return False

        obj1 = obj1.rest
        obj2 = obj2.rest

        # circular
        if obj1 is obj2:
            break

    return False


def prim_list(vm, *args):
    lst = None
    for x in reversed(args):
        lst = pair(x, lst)
    return lst


def prim_length(vm, lst):
    return sum(1 for _ in iter_list(lst))


def prim_append(vm, *lists):
    if not lists:
        return None
    result = lists[-1]
    for lst in reversed(lists[:-1]):
        values = list(iter_list(lst))
        for value in reversed(values):
            result = pair(value, result)
    return result


def prim_reverse(vm, lst):
    result = None
    for value in iter_list(lst):
        result = pair(value, result)
    return result


def prim_list_tail(vm, lst, index):
    type_check(index, int)
    if index < 0:
        raise WrongArgType("List index cannot be negative")
    for _ in range(index):
        type_check(lst, pair)
        lst = lst.rest
    return lst


def prim_list_ref(vm, lst, index):
    tail = prim_list_tail(vm, lst, index)
    type_check(tail, pair)
    return tail.first


def find_member(obj, lst, predicate):
    while isinstance(lst, pair):
        if predicate(obj, lst.first):
            return lst
        lst = lst.rest
    if lst is not None:
        raise WrongArgType("Expected a proper list")
    return False


def prim_memq(vm, obj, lst):
    return find_member(obj, lst, lambda a, b: prim_eq(vm, a, b))


def prim_memv(vm, obj, lst):
    return find_member(obj, lst, lambda a, b: prim_eqv(vm, a, b))


def prim_member(vm, obj, lst):
    return find_member(obj, lst, lambda a, b: prim_equal(vm, a, b))


def find_assoc(obj, alist, predicate):
    while isinstance(alist, pair):
        entry = alist.first
        type_check(entry, pair)
        if predicate(obj, entry.first):
            return entry
        alist = alist.rest
    if alist is not None:
        raise WrongArgType("Expected a proper association list")
    return False


def prim_assq(vm, obj, alist):
    return find_assoc(obj, alist, lambda a, b: prim_eq(vm, a, b))


def prim_assv(vm, obj, alist):
    return find_assoc(obj, alist, lambda a, b: prim_eqv(vm, a, b))


def prim_assoc(vm, obj, alist):
    return find_assoc(obj, alist, lambda a, b: prim_equal(vm, a, b))


def prim_apply(vm, proc, *args):
    if len(args) == 0:
        return vm.apply(proc, args)
    argv = list(args[:-1])
    arglst = args[-1]
    while isinstance(arglst, pair):
        argv.append(arglst.first)
        arglst = arglst.rest
    if arglst is not None:
        raise WrongArgType(
            "The last argument of apply should be a valid list, but got %s" % args[-1]
        )
    return vm.apply(proc, argv)


def prim_map(vm, proc, *lists):
    res = []
    lists = list(lists)
    while True:
        if any(lst is not None and not isinstance(lst, pair) for lst in lists):
            raise WrongArgType("Arguments of map should be valid lists.")
        ended = [lst is None for lst in lists]
        if any(ended):
            if not all(ended):
                raise MiscError(
                    "Lists supplied to map should be all of the same length."
                )
            break
        args = [lst.first for lst in lists]
        lists = [lst.rest for lst in lists]
        res.append(vm.apply(proc, args))
    rest = None
    for x in reversed(res):
        rest = pair(x, rest)
    return rest


def prim_for_each(vm, proc, *lists):
    lists = list(lists)
    while True:
        if any(lst is not None and not isinstance(lst, pair) for lst in lists):
            raise WrongArgType("Arguments of for-each should be valid lists.")
        ended = [lst is None for lst in lists]
        if any(ended):
            if not all(ended):
                raise MiscError(
                    "Lists supplied to for-each should be all of the same length."
                )
            return None
        vm.apply(proc, [lst.first for lst in lists])
        lists = [lst.rest for lst in lists]


def prim_load(vm, filename):
    type_check(filename, str)
    return vm.load(filename)


def prim_string_to_symbol(vm, name):
    type_check(name, str)
    return sym(name)


def prim_symbol_to_string(vm, s):
    type_check(s, sym)
    return s.name


def prim_number_to_string(vm, num, radix=10):
    if radix == 10:
        return str(num)
    type_check(num, (int, int))
    minus = False
    if num < 0:
        minus = True
        num = -num

    if radix == 2:
        fmt = "%s" % format(num, "b")
    elif radix == 8:
        fmt = "%o" % num
    elif radix == 16:
        fmt = "%X" % num
    else:
        raise MiscError("Radix should be one of 2, 8, 10, or 16")

    if minus:
        return "-" + fmt
    return fmt


def prim_string_to_number(vm, s, radix=10):
    type_check(s, str)
    if not s:
        return False
    try:
        return int(s, radix)
    except ValueError:
        if radix != 10:
            raise MiscError("Only radix 10 is permitted for decimal number")
        try:
            if s.endswith("i"):
                # complex number
                return complex(s[:-1] + "j")
            else:
                return float(s)
        except ValueError:
            return False


@type_error_decorator
def prim_string_append(vm, *strings):
    return "".join(strings)


def prim_make_string(vm, size, *fill):
    check_size(size)
    character = fill[0] if fill else Character("\x00")
    type_check(character, Character)
    return character.value * size


def prim_string(vm, *characters):
    for character in characters:
        type_check(character, Character)
    return "".join(character.value for character in characters)


def prim_string_length(vm, string):
    type_check(string, str)
    return len(string)


def prim_string_ref(vm, string, index):
    type_check(string, str)
    check_index(index, len(string))
    return Character(string[index])


def prim_substring(vm, string, start, end):
    type_check(string, str)
    check_slice(start, end, len(string))
    return string[start:end]


def prim_string_copy(vm, string):
    type_check(string, str)
    return string[:]


def prim_string_to_list(vm, string):
    type_check(string, str)
    return prim_list(vm, *(Character(value) for value in string))


def prim_list_to_string(vm, characters):
    values = list(iter_list(characters))
    for character in values:
        type_check(character, Character)
    return "".join(character.value for character in values)


def make_string_comparison(name, relation, case_insensitive):
    def comparison(vm, *strings):
        for string in strings:
            type_check(string, str)
        key = str.casefold if case_insensitive else lambda value: value
        return compare_chain([key(string) for string in strings], relation)

    comparison.__name__ = name
    return comparison


def make_char_comparison(name, relation, case_insensitive):
    def comparison(vm, *characters):
        for character in characters:
            type_check(character, Character)
        values = [character.value for character in characters]
        if case_insensitive:
            values = [value.casefold() for value in values]
        return compare_chain(values, relation)

    comparison.__name__ = name
    return comparison


def compare_chain(values, relation):
    operators = {
        "eq": lambda a, b: a == b,
        "lt": lambda a, b: a < b,
        "gt": lambda a, b: a > b,
        "le": lambda a, b: a <= b,
        "ge": lambda a, b: a >= b,
    }
    predicate = operators[relation]
    return all(predicate(a, b) for a, b in zip(values, values[1:]))


def character_value(character):
    type_check(character, Character)
    return character.value


def prim_char_alphabetic_p(vm, character):
    return character_value(character).isalpha()


def prim_char_numeric_p(vm, character):
    return character_value(character).isdigit()


def prim_char_whitespace_p(vm, character):
    return character_value(character).isspace()


def prim_char_upper_case_p(vm, character):
    return character_value(character).isupper()


def prim_char_lower_case_p(vm, character):
    return character_value(character).islower()


def prim_char_to_integer(vm, character):
    return ord(character_value(character))


def prim_integer_to_char(vm, value):
    type_check(value, int)
    if isinstance(value, bool):
        raise WrongArgType("Expected an exact integer")
    try:
        return Character(chr(value))
    except ValueError as error:
        raise WrongArgType(str(error))


def prim_char_upcase(vm, character):
    value = character_value(character).upper()
    return Character(value if len(value) == 1 else character.value)


def prim_char_downcase(vm, character):
    value = character_value(character).lower()
    return Character(value if len(value) == 1 else character.value)


def prim_make_vector(vm, size, *fill):
    check_size(size)
    value = fill[0] if fill else None
    return Vector([value] * size)


def prim_vector(vm, *elements):
    return Vector(elements)


def prim_vector_length(vm, vector):
    type_check(vector, Vector)
    return len(vector)


def prim_vector_ref(vm, vector, index):
    type_check(vector, Vector)
    check_index(index, len(vector))
    return vector.elements[index]


def prim_vector_set_x(vm, vector, index, value):
    type_check(vector, Vector)
    check_index(index, len(vector))
    vector.elements[index] = value


def prim_vector_to_list(vm, vector):
    type_check(vector, Vector)
    return prim_list(vm, *vector.elements)


def prim_list_to_vector(vm, lst):
    return Vector(iter_list(lst))


def prim_vector_fill_x(vm, vector, fill):
    type_check(vector, Vector)
    vector.elements[:] = [fill] * len(vector)


def prim_equal(vm, a, b):
    return a == b


def prim_eq(vm, a, b):
    return a is b


def prim_eqv(vm, a, b):
    if is_number(a) and is_number(b):
        return type(a) is type(b) and a == b
    return prim_eq(vm, a, b)


########################################
# Helper for primitives
########################################
def make_type_predict(tt):
    def predict(vm, obj):
        return matches_type(obj, tt)

    return predict


def make_cxr(operations):
    def cxr(vm, obj):
        for operation in reversed(operations):
            type_check(obj, pair)
            obj = obj.first if operation == "a" else obj.rest
        return obj

    cxr.__name__ = "c%sr" % "".join(operations)
    return cxr


def is_number(obj):
    return not isinstance(obj, bool) and isinstance(obj, (int, float, complex))


def check_size(size):
    type_check(size, int)
    if isinstance(size, bool) or size < 0:
        raise WrongArgType("Expected a non-negative exact integer")


def check_index(index, length):
    check_size(index)
    if index >= length:
        raise WrongArgType("Index %d is out of bounds" % index)


def check_slice(start, end, length):
    check_size(start)
    check_size(end)
    if start > end or end > length:
        raise WrongArgType("Invalid string slice %d:%d" % (start, end))


def type_check(obj, t):
    if not matches_type(obj, t):
        raise WrongArgType(
            "Expecting type %s, but got %s (type %s)" % (t, obj, type(obj))
        )


def type_check_all(objects, expected_type):
    for obj in objects:
        type_check(obj, expected_type)


def matches_type(obj, expected_type):
    if isinstance(obj, bool):
        if expected_type is int:
            return False
        if isinstance(expected_type, tuple):
            if int in expected_type and bool not in expected_type:
                return False
    return isinstance(obj, expected_type)


def iter_list(lst, excp_t=WrongArgType):
    while isinstance(lst, pair):
        yield lst.first
        lst = lst.rest
    if lst is not None:
        raise excp_t("Not a proper list")
