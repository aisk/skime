import pytest
from helper import HelperVM

from skime.errors import WrongArgType
from skime.types.character import Character


class TestCharacters(HelperVM):
    def test_character_predicates(self):
        assert self.eval("(char? #\\a)") is True
        assert self.eval('(char? "a")') is False
        assert self.eval("(char-alphabetic? #\\a)") is True
        assert self.eval("(char-numeric? #\\7)") is True
        assert self.eval("(char-whitespace? #\\space)") is True
        assert self.eval("(char-upper-case? #\\A)") is True
        assert self.eval("(char-lower-case? #\\a)") is True

    def test_character_comparisons(self):
        cases = [
            ("char=?", "#\\a", "#\\a", True),
            ("char<?", "#\\a", "#\\b", True),
            ("char>?", "#\\b", "#\\a", True),
            ("char<=?", "#\\a", "#\\a", True),
            ("char>=?", "#\\a", "#\\b", False),
            ("char-ci=?", "#\\a", "#\\A", True),
            ("char-ci<?", "#\\a", "#\\B", True),
            ("char-ci>?", "#\\B", "#\\a", True),
            ("char-ci<=?", "#\\a", "#\\A", True),
            ("char-ci>=?", "#\\a", "#\\B", False),
        ]
        for procedure, left, right, expected in cases:
            assert self.eval("(%s %s %s)" % (procedure, left, right)) is expected

    def test_character_conversion(self):
        assert self.eval("(char->integer #\\A)") == ord("A")
        assert self.eval("(integer->char 65)") == Character("A")
        assert self.eval("(char-upcase #\\a)") == Character("A")
        assert self.eval("(char-downcase #\\A)") == Character("a")


class TestStrings(HelperVM):
    def test_string_construction_and_access(self):
        assert self.eval('(string? "abc")') is True
        assert self.eval("(string? 1)") is False
        assert self.eval("(make-string 3 #\\a)") == "aaa"
        assert self.eval("(string #\\a #\\b #\\c)") == "abc"
        assert self.eval('(string-length "abc")') == 3
        assert self.eval('(string-ref "abc" 1)') == Character("b")
        assert self.eval('(substring "abcdef" 1 4)') == "bcd"
        assert self.eval('(string-copy "abc")') == "abc"

    def test_string_comparisons(self):
        cases = [
            ("string=?", "a", "a", True),
            ("string<?", "a", "b", True),
            ("string>?", "b", "a", True),
            ("string<=?", "a", "a", True),
            ("string>=?", "a", "b", False),
            ("string-ci=?", "Scheme", "scheme", True),
            ("string-ci<?", "a", "B", True),
            ("string-ci>?", "B", "a", True),
            ("string-ci<=?", "a", "A", True),
            ("string-ci>=?", "a", "B", False),
        ]
        for procedure, left, right, expected in cases:
            assert self.eval('(%s "%s" "%s")' % (procedure, left, right)) is expected

    def test_string_list_conversion(self):
        assert self.eval('(string->list "abc")') == self.eval("'(#\\a #\\b #\\c)")
        assert self.eval("(list->string '(#\\a #\\b #\\c))") == "abc"

    def test_string_append(self):
        assert self.eval('(string-append "Scheme" " " "works")') == "Scheme works"
        assert self.eval("(string-append)") == ""

    def test_invalid_string_operations(self):
        pytest.raises(WrongArgType, self.eval, '(string-ref "a" 1)')
        pytest.raises(WrongArgType, self.eval, '(substring "abc" 2 1)')
        pytest.raises(WrongArgType, self.eval, "(list->string '(#\\a 1))")


class TestSymbols(HelperVM):
    def test_symbol_predicate_and_conversion(self):
        assert self.eval("(symbol? 'scheme)") is True
        assert self.eval('(symbol? "scheme")') is False
        assert self.eval('(string->symbol "scheme")') == self.eval("'scheme")
        assert self.eval("(symbol->string 'scheme)") == "scheme"
