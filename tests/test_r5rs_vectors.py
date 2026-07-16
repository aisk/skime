import pytest
from helper import HelperVM

from skime.errors import WrongArgType
from skime.types.vector import Vector


class TestR5RSVectors(HelperVM):
    def test_vector_literals_and_construction(self):
        assert self.eval("'#(a b c)") == Vector(
            [self.eval("'a"), self.eval("'b"), self.eval("'c")]
        )
        assert self.eval("(vector 1 2 3)") == Vector([1, 2, 3])
        assert self.eval("(make-vector 3 'empty)") == Vector([self.eval("'empty")] * 3)
        assert self.eval("(vector? '#(1 2))") is True
        assert self.eval("(vector? '(1 2))") is False

    def test_vector_access_and_mutation(self):
        assert self.eval("(vector-length '#(1 2 3))") == 3
        assert self.eval("(vector-ref '#(1 2 3) 1)") == 2
        assert self.eval("(let ((v (vector 1 2 3))) (vector-set! v 1 9) v)") == Vector(
            [1, 9, 3]
        )
        assert self.eval("(let ((v (vector 1 2 3))) (vector-fill! v 0) v)") == Vector(
            [0, 0, 0]
        )

    def test_vector_list_conversion(self):
        assert self.eval("(vector->list '#(1 2 3))") == self.eval("'(1 2 3)")
        assert self.eval("(list->vector '(1 2 3))") == Vector([1, 2, 3])

    def test_quasiquoted_vector(self):
        assert self.eval("`#(1 ,(+ 1 1) ,@(list 3 4))") == Vector([1, 2, 3, 4])

    def test_invalid_vector_indexes(self):
        pytest.raises(WrongArgType, self.eval, "(vector-ref '#(1) -1)")
        pytest.raises(WrongArgType, self.eval, "(vector-ref '#(1) 1)")
