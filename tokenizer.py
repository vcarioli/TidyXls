# ========================================================================
# Description: Tokenise an Excel formula using an implementation of
# ========================================================================
import collections
import re


# ========================================================================
#       Class: XlsTokens
# Description: Inheritable container for token definitions
#
#  Attributes: Self explanatory
#
#     Methods: None
# ========================================================================
class XlsTokens:
	# Types
	TT_NOOP = 'noop'
	TT_OPERAND = 'operand'
	TT_FUNCTION = 'function'
	TT_SUBEXPR = 'subexpression'
	TT_ARGUMENT = 'argument'
	TT_OP_PRE = 'operator-prefix'
	TT_OP_IN = 'operator-infix'
	TT_OP_POST = 'operator-postfix'
	TT_WSPACE = 'white-space'
	TT_UNKNOWN = 'unknown'

	# SubTypes
	TS_START = 'start'
	TS_STOP = 'stop'
	TS_TEXT = 'text'
	TS_NUMBER = 'number'
	TS_LOGICAL = 'logical'
	TS_ERROR = 'error'
	TS_RANGE = 'range'
	TS_MATH = 'math'
	TS_CONCAT = 'concatenate'
	TS_INTERSECT = 'intersect'
	TS_UNION = 'union'


# ========================================================================
#       Class: Token
# Description: Encapsulate a formula token
#
#  Attributes:   tvalue -
#                 ttype - See token definitions, above, for values
#              tsubtype - See token definitions, above, for values
#
#     Methods:    Token - __init__()
# ========================================================================
class Token:
	def __init__(self, value, ttype, tsubtype):
		self.tvalue = value
		self.ttype = ttype
		self.tsubtype = tsubtype

	def __str__(self):
		return self.tvalue

	def get(self):
		return self.tvalue, self.ttype, self.tsubtype


# ========================================================================
#       Class: Tokens
# Description: An ordered list of tokens
#
#  Attributes:      items  - Ordered list
#                   index  - Current position in the list
#
#     Methods: Tokens      - __init__()
#              Token       - add()      - Add a token to the end of the list
#              None        - addRef()   - Add a token to the end of the list
#              None        - reset()    - reset the index to -1
#              Boolean     - BOF()      - End of list?
#              Boolean     - EOF()      - Beginning of list?
#              Boolean     - moveNext() - Move the index along one
#              Token/None  - current()  - Return the current token
#              Token/None  - next()     - Return the next token (leave the index unchanged)
#              Token/None  - previous() - Return the previous token (leave the index unchanged)
# ========================================================================
class Tokens:
	def __init__(self):
		self.items = []
		self.index = -1

	def add(self, value, ttype, tsubtype=""):
		if not tsubtype:
			tsubtype = ""
		token = Token(value, ttype, tsubtype)
		self.add_ref(token)
		return token

	def add_ref(self, token):
		self.items.append(token)

	def reset(self):
		self.index = -1

	def bof(self):
		return self.index <= 0

	def eof(self):
		return self.index >= (len(self.items) - 1)

	def move_next(self):
		if self.eof():
			return False
		self.index += 1
		return True

	def current(self):
		if self.index == -1:
			return None
		return self.items[self.index]

	def next(self):
		if self.eof():
			return None
		return self.items[self.index + 1]

	def previous(self):
		if self.index < 1:
			return None
		return self.items[self.index - 1]


# ========================================================================
#       Class: TokenStack
#    Inherits: XlsTokens - a list of token values
# Description: A LIFO stack of tokens
#
#  Attributes:       items  - Ordered list
#
#     Methods: TokenStack   - __init__()
#              None         - push(token) - Push a token onto the stack
#              Token/None   - pop()       - Pop a token off the stack
#              Token/None   - token()     - Non-destructively return the top item on the stack
#              String       - type()      - Return the top token's type
#              String       - subtype()   - Return the top token's subtype
#              String       - value()     - Return the top token's value
# ========================================================================
class TokenStack(XlsTokens):
	def __init__(self):
		self.items = []

	def push(self, token):
		self.items.append(token)

	def pop(self):
		# token = self.items.pop()
		token = self.items.pop() if self.items else Token("unknown", self.TT_UNKNOWN, self.TS_STOP)
		return Token("", token.ttype, self.TS_STOP)

	def token(self):
		# Note: this uses Pythons and/or "hack" to emulate C's ternary operator (i.e. cond ? exp1 : exp2)
		return ((len(self.items) > 0) and [self.items[len(self.items) - 1]] or [None])[0]

	def value(self):
		return ((self.token()) and [(self.token()).tvalue] or [""])[0]

	def type(self):
		#		t = self.token()
		return ((self.token()) and [(self.token()).ttype] or [""])[0]

	def subtype(self):
		return ((self.token()) and [(self.token()).tsubtype] or [""])[0]


# ========================================================================
#       Class: XlsParser(formula)
# Description: Parse an Excel formula into a stream of tokens
#
#  Attributes:
#
#     Methods: Tokens - parse(formula) - return a token stream (list)
# ========================================================================
class XlsParser(XlsTokens):
	def __init__(self, formula='', arg_sep=','):
		self._formula = formula
		self._arg_sep = arg_sep
		self.items = []
		self._parse()

	def _get_tokens(self):
		def current_char():
			return self._formula[offset]

		def double_char():
			return self._formula[offset:offset + 2]

		def next_char():
			# JavaScript returns an empty string if the index is out of bounds,
			# Python throws an IndexError.  We mimic this behaviour here.
			try:
				self._formula[offset + 1]
			except IndexError:
				return ""
			else:
				return self._formula[offset + 1]

		def eof():
			return offset >= len(self._formula)

		tokens = Tokens()
		token_stack = TokenStack()
		offset = 0
		token = ""
		in_string = False
		in_path = False
		in_range = False
		in_error = False

		while len(self._formula) > 0:
			if self._formula[0] == ' ':
				self._formula = self._formula[1:]
			else:
				if self._formula[0] == '=':
					self._formula = self._formula[1:]
				break

			# state-dependent character evaluation (order is important)
		while not eof():

			# double-quoted strings
			# embeds are doubled
			# end marks token
			if in_string:
				if current_char() == '"':
					if next_char() == '"':
						token += '"'
						offset += 1
					else:
						in_string = False
						tokens.add(token, self.TT_OPERAND, self.TS_TEXT)
						token = ""
				else:
					token += current_char()
				offset += 1
				continue

			# single-quoted strings (links)
			# embeds are double
			# end does not mark a token
			if in_path:
				if current_char() == "'":
					if next_char() == "'":
						token += "'"
						offset += 1
					else:
						token = "'" + token + "'"
						in_path = False
				else:
					token += current_char()
				offset += 1
				continue

			# bracketed strings (range offset or linked workbook name)
			# no embeds (changed to "()" by Excel)
			# end does not mark a token
			if in_range:
				if current_char() == ']':
					in_range = False
				token += current_char()
				offset += 1
				continue

			# error values
			# end marks a token, determined from absolute list of values
			if in_error:
				token += current_char()
				offset += 1
				if ',#NULL!,#DIV/0!,#VALUE!,#REF!,#NAME?,#NUM!,#N/A,'.find(',' + token + ',') != -1:
					in_error = False
					tokens.add(token, self.TT_OPERAND, self.TS_ERROR)
					token = ""
				continue

			# scientific notation check
			regexsn = '^[1-9]{1}(\.[0-9]+)?[eE]{1}$'
			if '+-'.find(current_char()) != -1:
				if len(token) > 1:
					if re.match(regexsn, token):
						token += current_char()
						offset += 1
						continue

			# independent character evaulation (order not important)
			#
			# establish state-dependent character evaluations
			if current_char() == '"':
				if len(token) > 0:
					# not expected
					tokens.add(token, self.TT_UNKNOWN)
					token = ""
				in_string = True
				offset += 1
				continue

			if current_char() == "'":
				if len(token) > 0:
					# not expected
					tokens.add(token, self.TT_UNKNOWN)
					token = ""
				in_path = True
				offset += 1
				continue

			if current_char() == '[':
				in_range = True
				token += current_char()
				offset += 1
				continue

			if current_char() == '#':
				if len(token) > 0:
					# not expected
					tokens.add(token, self.TT_UNKNOWN)
					token = ""
				in_error = True
				token += current_char()
				offset += 1
				continue

			# mark start and end of arrays and array rows
			if current_char() == '{':
				if len(token) > 0:
					# not expected
					tokens.add(token, self.TT_UNKNOWN)
					token = ""
				token_stack.push(tokens.add('ARRAY', self.TT_FUNCTION, self.TS_START))
				token_stack.push(tokens.add('ARRAYROW', self.TT_FUNCTION, self.TS_START))
				offset += 1
				continue

			if current_char() == ';':
				if len(token) > 0:
					tokens.add(token, self.TT_OPERAND)
					token = ""
				tokens.add_ref(token_stack.pop())
				tokens.add(',', self.TT_ARGUMENT)
				token_stack.push(tokens.add('ARRAYROW', self.TT_FUNCTION, self.TS_START))
				offset += 1
				continue

			if current_char() == '}':
				if len(token) > 0:
					tokens.add(token, self.TT_OPERAND)
					token = ""
				tokens.add_ref(token_stack.pop())
				tokens.add_ref(token_stack.pop())
				offset += 1
				continue

			# trim white-space
			if current_char() == ' ':
				if len(token) > 0:
					tokens.add(token, self.TT_OPERAND)
					token = ""
				tokens.add("", self.TT_WSPACE)
				offset += 1
				while (current_char() == ' ') and (not eof()):
					offset += 1
				continue

			# multi-character comparators
			if ',>=,<=,<>,'.find(',' + double_char() + ',') != -1:
				if len(token) > 0:
					tokens.add(token, self.TT_OPERAND)
					token = ""
				tokens.add(double_char(), self.TT_OP_IN, self.TS_LOGICAL)
				offset += 2
				continue

			# standard infix operators
			if '+-*/^&=><'.find(current_char()) != -1:
				if len(token) > 0:
					tokens.add(token, self.TT_OPERAND)
					token = ""
				tokens.add(current_char(), self.TT_OP_IN)
				offset += 1
				continue

			# standard postfix operators
			if '%'.find(current_char()) != -1:
				if len(token) > 0:
					tokens.add(token, self.TT_OPERAND)
					token = ""
				tokens.add(current_char(), self.TT_OP_POST)
				offset += 1
				continue

			# start subexpression or function
			if current_char() == '(':
				if len(token) > 0:
					token_stack.push(tokens.add(token, self.TT_FUNCTION, self.TS_START))
					token = ""
				else:
					token_stack.push(tokens.add("", self.TT_SUBEXPR, self.TS_START))
				offset += 1
				continue

			# function, subexpression, array parameters
			if current_char() == ',':
				if len(token) > 0:
					tokens.add(token, self.TT_OPERAND)
					token = ""
				if not (token_stack.type() == self.TT_FUNCTION):
					tokens.add(current_char(), self.TT_OP_IN, self.TS_UNION)
				else:
					tokens.add(current_char(), self.TT_ARGUMENT)
				offset += 1
				continue

			# stop subexpression
			if current_char() == ')':
				if len(token) > 0:
					tokens.add(token, self.TT_OPERAND)
					token = ""
				tokens.add_ref(token_stack.pop())
				offset += 1
				continue

			# token accumulation
			token += current_char()
			offset += 1

		# dump remaining accumulation
		if len(token) > 0:
			tokens.add(token, self.TT_OPERAND)

		# move all tokens to a new collection, excluding all unnecessary white-space tokens
		tokens2 = Tokens()

		while tokens.move_next():
			token = tokens.current()

			if token.ttype == self.TT_WSPACE:
				if tokens.bof() or tokens.eof():
					pass
				elif not (  tokens.previous().ttype == self.TT_FUNCTION and tokens.previous().tsubtype == self.TS_STOP
							or tokens.previous().ttype == self.TT_SUBEXPR and tokens.previous().tsubtype == self.TS_STOP
							or tokens.previous().ttype == self.TT_OPERAND):
					pass
				elif not (  tokens.next().ttype == self.TT_FUNCTION and tokens.next().tsubtype == self.TS_START
							or tokens.next().ttype == self.TT_SUBEXPR and tokens.next().tsubtype == self.TS_START
							or tokens.next().ttype == self.TT_OPERAND):
					pass
				else:
					tokens2.add(token.tvalue, self.TT_OP_IN, self.TS_INTERSECT)
				continue

			tokens2.add_ref(token)

		# switch infix '-' operator to prefix when appropriate, switch infix '+' operator to noop when appropriate,
		# identify operand and infix-operator subtypes, pull '@' from in front of function names
		while tokens2.move_next():
			token = tokens2.current()
			if token.ttype == self.TT_OP_IN and token.tvalue == '-':
				if tokens2.bof():
					token.ttype = self.TT_OP_PRE
				elif (  tokens2.previous().ttype == self.TT_FUNCTION and tokens2.previous().tsubtype == self.TS_STOP
						or tokens2.previous().ttype == self.TT_SUBEXPR and tokens2.previous().tsubtype == self.TS_STOP
						or tokens2.previous().ttype == self.TT_OP_POST
						or tokens2.previous().ttype == self.TT_OPERAND):
					token.tsubtype = self.TS_MATH
				else:
					token.ttype = self.TT_OP_PRE
				continue

			if token.ttype == self.TT_OP_IN and token.tvalue == '+':
				if tokens2.bof():
					token.ttype = self.TT_NOOP
				elif (  tokens2.previous().ttype == self.TT_FUNCTION and tokens2.previous().tsubtype == self.TS_STOP
						or tokens2.previous().ttype == self.TT_SUBEXPR and tokens2.previous().tsubtype == self.TS_STOP
						or tokens2.previous().ttype == self.TT_OP_POST
						or tokens2.previous().ttype == self.TT_OPERAND):
					token.tsubtype = self.TS_MATH
				else:
					token.ttype = self.TT_NOOP
				continue

			if token.ttype == self.TT_OP_IN and len(token.tsubtype) == 0:
				if '<>='.find(token.tvalue[0:1]) != -1:
					token.tsubtype = self.TS_LOGICAL
				elif token.tvalue == '&':
					token.tsubtype = self.TS_CONCAT
				else:
					token.tsubtype = self.TS_MATH
				continue

			if token.ttype == self.TT_OPERAND and len(token.tsubtype) == 0:
				try:
					float(token.tvalue)
				except ValueError:  # as e:
					if token.tvalue == 'TRUE' or token.tvalue == 'FALSE':
						token.tsubtype = self.TS_LOGICAL
					else:
						token.tsubtype = self.TS_RANGE
				else:
					token.tsubtype = self.TS_NUMBER
				continue

			if token.ttype == self.TT_FUNCTION:
				if token.tvalue[0:1] == '@':
					token.tvalue = token.tvalue[1:]
				continue

		tokens2.reset()

		# move all tokens to a new collection, excluding all noops
		tokens = Tokens()
		while tokens2.move_next():
			if tokens2.current().ttype != self.TT_NOOP:
				tokens.add_ref(tokens2.current())

		tokens.reset()
		return tokens

	def _parse(self, formula=None):
		if formula:
			self._formula = formula
		if not self._formula:
			return

		self.tokens = self._get_tokens()

		stack = []
		for tok in self.tokens.items:
			t = None

			tv, tt, ts = tok.get()

			if tt == XlsTokens.TT_FUNCTION:

				if ts == XlsTokens.TS_START:
					t = Token('', XlsTokens.TT_ARGUMENT, XlsTokens.TS_START)
					stack.append(tv)
				elif ts == XlsTokens.TS_STOP:
					tv = stack.pop()
			# elif tt == XlsTokens.TT_OPERAND:
			#    if ts == XlsTokens.TS_TEXT:
			#        pass
			#    elif ts == XlsTokens.TS_NUMBER:
			#        pass
			#    elif ts == XlsTokens.TS_RANGE:
			#        pass
			#    pass
			elif tt == XlsTokens.TT_ARGUMENT:
				tv = self._arg_sep
			elif tt == XlsTokens.TT_SUBEXPR:
				if ts == XlsTokens.TS_START:
					tv = '('
				elif ts == XlsTokens.TS_STOP:
					tv = ')'
			# elif tt == XlsTokens.TT_OP_PRE:
			#    pass
			# elif tt == XlsTokens.TT_OP_POST:
			#    pass
			# elif tt == XlsTokens.TT_OP_IN:
			#    pass

			self.items.append(Token(tv, tt, ts))
			if t:
				self.items.append(t)

	def render(self):
		output = ""
		if self.tokens:
			for t in self.tokens.items:
				if t.ttype == self.TT_FUNCTION and t.tsubtype == self.TS_START:
					output += t.tvalue + '('
				elif t.ttype == self.TT_FUNCTION and t.tsubtype == self.TS_STOP:
					output += ')'
				elif t.ttype == self.TT_SUBEXPR and t.tsubtype == self.TS_START:
					output += '('
				elif t.ttype == self.TT_SUBEXPR and t.tsubtype == self.TS_STOP:
					output += ')'
				# TODO: add in RE substitution of " with "" for strings
				elif t.ttype == self.TT_OPERAND and t.tsubtype == self.TS_TEXT:
					output += '"' + t.tvalue + '"'
				elif t.ttype == self.TT_OP_IN and t.tsubtype == self.TS_INTERSECT:
					output += ' '

				else:
					output += t.tvalue
		return output

	def prettyprint(self):
		indent = 0
		output = ""
		if self.tokens:
			for t in self.tokens.items:
				# print("'",t.ttype,t.tsubtype,t.tvalue,"'")
				if t.tsubtype == self.TS_STOP:
					indent -= 1

				output += '    ' * indent + t.tvalue + ' <' + t.ttype + '> <' + t.tsubtype + '>' + '\n'

				if t.tsubtype == self.TS_START:
					indent += 1
		return output

	def xlstidy(self):
		func_stack = []

		def sp(n=1):
			return '\t' * n if n > 0 else ''

		def push(fn):
			func_stack.append(fn)

		def pop():
			return func_stack.pop()

		def top(i=0):
			x = len(func_stack) - 1 - i
			return func_stack[x] if x >= 0 else None

		def _do_nl():
			fn = ('IF', 'IFERROR', 'AND', 'OR', 'NOT')
			return '\n' if top() in fn else ''

		def tidy(tokens, i=0, indent=''):
			if not tokens:
				return ''

			nextindent = ''
			o = ''
			tv, tt, ts = tokens[0].get()

			if tt == XlsTokens.TT_FUNCTION:
				if ts == XlsTokens.TS_START:
					push(tv)
					o += indent + tv + '(' + _do_nl()
					i += 1
					nextindent = sp(i)
				elif ts == XlsTokens.TS_STOP:
					i -= 1
					nextindent = sp(i) if _do_nl() else ''
					o += _do_nl() + (sp(i) if _do_nl() else '') + ')'
					pop()
			elif tt == XlsTokens.TT_OPERAND:
				if ts == XlsTokens.TS_TEXT:
					o += '"' + tv + '"'
				else:
					o += tv
			elif tt == XlsTokens.TT_ARGUMENT:
				if ts == XlsTokens.TS_START:
					o += sp(i) if _do_nl() else ''
				else:
					o += _do_nl() + (sp(i) if _do_nl() else '') + tv
			elif tt == XlsTokens.TT_SUBEXPR:
				if ts == XlsTokens.TS_START:
					o += '('
				elif ts == XlsTokens.TS_STOP:
					o += ')'
			elif tt == XlsTokens.TT_OP_PRE:
				o += tv
			elif tt == XlsTokens.TT_OP_POST:
				o += tv
			elif tt == XlsTokens.TT_OP_IN:
				o += tv

			return o + tidy(tokens[1:], i, nextindent)

		#
		return tidy(self.items)


	def dependencies(self):
		o = []
		for i in self.items:
			tv, tt, ts = i.get()

			if ts == XlsTokens.TS_RANGE:
				if tv not in o:
					o.append(tv)

		return o


class Operator:
	def __init__(self, value, precedence, associativity):
		self.value = value
		self.precedence = precedence
		self.associativity = associativity


class ASTNode(object):
	def __init__(self, token):
		super(ASTNode, self).__init__()
		self.token = token

	def emit(self):
		return self.token.tvalue

	def __str__(self):
		return self.token.tvalue


class OperatorNode(ASTNode):
	def __init__(self, *args):
		super(OperatorNode, self).__init__(*args)

	def emit(self):
		pass


class RangeNode(ASTNode):
	def __init__(self, *args):
		super(RangeNode, self).__init__(*args)

	def emit(self):
		pass


class FunctionNode(ASTNode):
	def __init__(self, *args):
		super(FunctionNode, self).__init__(*args)
		self.num_args = 0

	def emit(self):
		pass


def create_node(t):
	if t.ttype == 'operand' and t.tsubtype == 'range':
		return RangeNode(t)
	elif t.ttype == 'function':
		return FunctionNode(t)
	elif t.ttype == 'operator':
		return OperatorNode(t)
	else:
		return ASTNode(t)


def get_rpn(expression):
	# remove leading =
	if expression.startswith('='):
		expression = expression[1:]

	p = XlsParser()
	p._parse(expression)

	# insert tokens for '(' and ')', to make things cleaner below
	tokens = []
	for t in p.tokens.items:
		if t.ttype == 'function' and t.tsubtype == 'start':
			t.tsubtype = ""
			tokens.append(t)
			tokens.append(Token('(', 'arglist', 'start'))
		elif t.ttype == 'function' and t.tsubtype == 'stop':
			# t.tsubtype = ""
			# tokens.append(t)
			tokens.append(Token(')', 'arglist', 'stop'))
		elif t.ttype == 'subexpression' and t.tsubtype == 'start':
			t.tvalue = '('
			tokens.append(t)
		elif t.ttype == 'subexpression' and t.tsubtype == 'stop':
			t.tvalue = ')'
			tokens.append(t)
		else:
			tokens.append(t)

		# print('tokens: ', '|'.join([x.tvalue for x in tokens]))

	# http://office.microsoft.com/en-us/excel-help/calculation-operators-and-precedence-HP010078886.aspx
	operators = {
		':': Operator(':', 8, 'left'),
		'': Operator(' ', 8, 'left'),
		',': Operator(',', 8, 'left'),
		'u-': Operator('u-', 7, 'left'),
		'%': Operator('%', 6, 'left'),
		'^': Operator('^', 5, 'left'),
		'*': Operator('*', 4, 'left'),
		'/': Operator('/', 4, 'left'),
		'+': Operator('+', 3, 'left'),
		'-': Operator('-', 3, 'left'),
		'&': Operator('&', 2, 'left'),
		'=': Operator('=', 1, 'left'),
		'<': Operator('<', 1, 'left'),
		'>': Operator('>', 1, 'left'),
		'<=': Operator('<=', 1, 'left'),
		'>=': Operator('>=', 1, 'left'),
		'<>': Operator('<>', 1, 'left')
	}

	output = collections.deque()
	stack = []
	were_values = []
	arg_count = []

	for t in tokens:
		if t.ttype == 'operand':
			output.append(create_node(t))

			if were_values:
				were_values.pop()
				were_values.append(True)

		elif t.ttype == 'function':
			stack.append(t)
			arg_count.append(0)
			if were_values:
				were_values.pop()
				were_values.append(True)
			were_values.append(False)

		elif t.ttype == 'argument':
			while stack and (stack[-1].tsubtype != 'start'):
				output.append(create_node(stack.pop()))

			if were_values.pop():
				arg_count[-1] += 1
			were_values.append(False)

			if not len(stack):
				raise Exception('Mismatched or misplaced parentheses')

		elif t.ttype.startswith('operator'):
			if t.ttype.endswith('-prefix') and t.tvalue == '-':
				o1 = operators['u-']
			else:
				o1 = operators[t.tvalue]

			while stack and stack[-1].ttype.startswith('operator'):

				if stack[-1].ttype.endswith('-prefix') and stack[-1].tvalue == '-':
					o2 = operators['u-']
				else:
					o2 = operators[stack[-1].tvalue]

				if o1.associativity == 'left' and o1.precedence <= o2.precedence or o1.associativity == 'right' and o1.precedence < o2.precedence:
					output.append(create_node(stack.pop()))
				else:
					break

			stack.append(t)

		elif t.tsubtype == 'start':
			stack.append(t)

		elif t.tsubtype == 'stop':
			while stack and stack[-1].tsubtype != 'start':
				output.append(create_node(stack.pop()))

			if not stack:
				raise Exception('Mismatched or misplaced parentheses')

			stack.pop()

			if stack and stack[-1].ttype == 'function':
				f = create_node(stack.pop())
				a = arg_count.pop()
				w = were_values.pop()
				if w:
					a += 1
				f.num_args = a
				# print(f, 'has ', a, ' args')
				output.append(f)

	while stack:
		if stack[-1].tsubtype == 'start' or stack[-1].tsubtype == 'stop':
			raise Exception('Mismatched or misplaced parentheses')

		output.append(create_node(stack.pop()))

	# print('Stack is: ', '|'.join(stack))
	# print('Ouput is: ', '|'.join([x.node.tvalue for x in output]))

	return output


def get_ast(expression):
	rpn = get_rpn(expression)
	stack = []
	for n in rpn:
		num_args = (
			2 if n.token.ttype == 'operator-infix'
			else 1 if n.token.ttype.startswith('operator')
			else n.num_args if n.token.ttype == 'function'
			else 0
		)
		n.args = [stack.pop() for _ in range(num_args)][::-1]
		stack.append(n)
	return stack[0]


def walk_ast(ast):
	yield ast
	for arg in getattr(ast, 'args', []):
		for n in walk_ast(arg):
			yield n

# ----------------------------------------------------------------------------------------------------------------------

def	print_dependencies(formulas):
	for f in formulas:
		print("'{0}':\t{{".format(f[0]))
		x = XlsParser(f[1]).dependencies()
		if x:
			for i in x:
				if i: print('\t' + i)
		print('}')

	return

########################################################################################################################

"""
# Formato del file RAW:
>>>\tnome_formula
testo_formula
<<<
>>>\tnome_formula
testo_formula
<<<
... ecc.
"""

if __name__ == '__main__':

	from os.path import join, sep

	# ------------------------------------------------------------------------------------------------------------------

	files_path = join('C:', sep, 'Users', 'vcarioli', 'PycharmProjects', 'TidyXls')

	filename		= 'lanes_0929'	# 'lanes_0913'

	raw_filename	= join(files_path, filename + '_raw.txt')
	tidy_filename	= join(files_path, filename + '_tidy.txt')

	# ------------------------------------------------------------------------------------------------------------------

	formulas = []

	with open(raw_filename, 'r') as ff:
		formula_name = ''
		formula_body = ''
		for line in ff:
			line = line.strip(' \t\n\r')

			if line.startswith('>>>\t'):
				formula_name = line.split('\t')[1]
			elif line.startswith('<<<'):
				if formula_name:
					formulas.append((formula_name, formula_body))
				formula_name = ''
				formula_body = ''
			else:
				formula_body += line

##	print_dependencies(formulas);	exit()

	with open(tidy_filename, 'w') as tidy_file:
		for f in formulas:
			for line in (
						'-' * 100
					,   '----- ' + f[0]
					,   '-' * 100
					,   XlsParser(f[1]).xlstidy()
					,   '-' * 100
					,   ''
					):
				tidy_file.write(line + '\n')

	# for node in get_rpn(e):
	#    print('{0:15}\t{1:25}\t\t{2}'.format('Token type', 'Token value', 'Token sub-type'))
	#    print('{0:15}\t{1:25}\t\t{2}'.format(node.token.ttype, node.token.tvalue, node.token.tsubtype))
