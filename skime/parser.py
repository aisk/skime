from symbol import Symbol as sym
from cons import Cons as cons

from errors import ParseError

def parse(text, name="__unknown__"):
    "Parse a piece of text."
    return Parser(text, name).parse()

class Parser(object):
    "A simple recursive descent parser for Scheme."
    sym_quote = sym("quote")
    
    def __init__(self, text, name="__unknown__"):
        self.text = text
        self.name = name
        self.pos = 0
        self.line = 1

    def parse(self):
        "Parse the text and return a sexp."
        try:
            return self.parse_expr()
        except IndexError:
            self.report_error("Unexpected end of code")

    def parse_expr(self):
        self.skip_all()
        
        ch = self.peak()

        if self.isdigit(ch):
            return self.parse_number()
        if ch == '#':
            if self.peak(idx=1) == 't':
                return True
            if self.peak(idx=1) == 'f':
                return False
            if self.peak(idx=1) == '(':
                return self.parse_vector()
        if ch == '(':
            return self.parse_list()
        if ch == '\'':
            return self.parse_quote()
        if ch in ['+', '-'] and \
           self.isdigit(self.peak(idx=1)):
            return self.parse_number()
        return self.parse_symbol()


    def parse_number(self):
        sign1 = 1
        if self.eat('-'):
            sign1 = -1
        self.eat('+')

        num1 = self.parse_unum()
        if self.eat('/'):
            num2 = self.parse_unum()
            if num2 is None:
                self.report_error("Invalid number format, expecting denominator")
            num1 = float(num1)/num2
        if self.peak() in ['+', '-']:
            sign2 = 1
            if self.eat('-'):
                sign2 = -1
            self.eat('+')
            num2 = self.parse_unum()
            if num2 is None:
                num2 = 1
            if not self.eat('i'):
                self.report_error("Invalid number format, expecting 'i' for complex")
            num1 = num1 + sign2*num2*1j

        return sign1*num1

    def parse_unum(self):
        "Parse an unsigned number."
        isfloat = False
        pos1 = self.pos
        while self.isdigit(self.peak()):
            self.pop()
        if self.eat('.'):
            isfloat = True
        while self.isdigit(self.peak()):
            self.pop()
        pos2 = self.pos
        if pos2 == pos1:
            return None
        if isfloat:
            return float(self.text[pos1:pos2])
        else:
            return int(self.text[pos1:pos2])


    def parse_list(self):
        self.eat('(')
        elems = []
        while self.more():
            self.skip_all()
            if self.eat(')'):
                elems.append(None)
                break
            if self.eat('.'):
                elems.append(self.parse_expr())
                self.skip_all()
                if not self.eat(')'):
                    self.report_error("Expecting %s, but got %s" %
                                      (')', self.text[self.pos]))
                break
            elems.append(self.parse_expr())
        car = elems.pop()
        for x in reversed(elems):
            car = cons(x, car)
        return car

    def parse_quote(self):
        self.eat('\'')
        return cons(Parser.sym_quote,
                    cons(self.parse_expr(), None))

    def parse_symbol(self):
        pos1 = self.pos
        self.pop()
        while self.more() and \
              not self.isspace(self.peak()) and \
              not self.peak() in ['\'', ')', '(', ',', '@', '.']:
            self.pop()
        pos2 = self.pos
        return sym(self.text[pos1:pos2])

    def parse_vector(self):
        pass

    def skip_all(self):
        "Skip all non-relevant characters."
        self.skip_ws()
        self.skip_comment()
        self.skip_ws()

    def skip_ws(self):
        "Skip whitespace."
        while self.more():
            if self.eat('\n'):
                self.line += 1
            elif self.isspace(self.peak()):
                self.pop()
            else:
                break

    def skip_comment(self):
        "Skip comment."
        while self.eat(';'):
            while self.more() and not self.eat('\n'):
                self.pop()
            self.line += 1

    def pop(self, n=1):
        "Increase self.pos by n."
        self.pos += n

    def more(self):
        "Whether we have more content to parse."
        return self.pos < len(self.text)
            
    def eat(self, char):
        "Try to eat a character."
        if self.peak() != char:
            return False
        self.pos += 1
        return True

    def peak(self, idx=0):
        "Get the character under self.pos + idx."
        if self.pos + idx < len(self.text):
            return self.text[self.pos + idx]
        return None

    def isdigit(self, ch):
        "Test whether ch is a digit."
        return ch is not None and ch.isdigit()

    def isspace(self, ch):
        "Test whether ch is whitespace."
        return ch is not None and ch.isspace()
        
    def report_error(self, msg):
        "Raise a ParserError with msg."
        raise ParseError("%s:%d %s" % (self.name, self.line, msg))