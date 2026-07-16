import pytest
from helper import HelperVM

from skime.errors import WrongArgType
from skime.types.character import Character


class TestR5RSCharacters(HelperVM):
    def test_character_predicates(self):
        assert self.eval("(char? #\\a)") is True
        assert self.eval('(char? "a")') is False
        assert self.eval("(char<? #\\a #\\b #\\c)") is True
        assert self.eval("(char-ci=? #\\a #\\A)") is True
        assert self.eval("(char-alphabetic? #\\a)") is True
        assert self.eval("(char-numeric? #\\7)") is True
        assert self.eval("(char-whitespace? #\\space)") is True
        assert self.eval("(char-upper-case? #\\A)") is True
        assert self.eval("(char-lower-case? #\\a)") is True

    def test_character_conversion(self):
        assert self.eval("(char->integer #\\A)") == ord("A")
        assert self.eval("(integer->char 65)") == Character("A")
        assert self.eval("(char-upcase #\\a)") == Character("A")
        assert self.eval("(char-downcase #\\A)") == Character("a")


class TestR5RSStrings(HelperVM):
    def test_string_construction_and_access(self):
        assert self.eval("(make-string 3 #\\a)") == "aaa"
        assert self.eval("(string #\\a #\\b #\\c)") == "abc"
        assert self.eval('(string-length "abc")') == 3
        assert self.eval('(string-ref "abc" 1)') == Character("b")
        assert self.eval('(substring "abcdef" 1 4)') == "bcd"
        assert self.eval('(string-copy "abc")') == "abc"

    def test_string_comparisons(self):
        assert self.eval('(string=? "abc" "abc")') is True
        assert self.eval('(string<? "abc" "abd" "b")') is True
        assert self.eval('(string-ci=? "Scheme" "scheme")') is True
        assert self.eval('(string-ci>=? "b" "A")') is True

    def test_string_list_conversion(self):
        assert self.eval('(string->list "abc")') == self.eval("'(#\\a #\\b #\\c)")
        assert self.eval("(list->string '(#\\a #\\b #\\c))") == "abc"

    def test_invalid_string_operations(self):
        pytest.raises(WrongArgType, self.eval, '(string-ref "a" 1)')
        pytest.raises(WrongArgType, self.eval, '(substring "abc" 2 1)')
        pytest.raises(WrongArgType, self.eval, "(list->string '(#\\a 1))")
