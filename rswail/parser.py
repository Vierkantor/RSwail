from rpython.rlib.parsing.ebnfparse import parse_ebnf, make_parse_function
from rpython.rlib.parsing.parsing import ParseError
from rpython.rlib.parsing.tree import RPythonVisitor

from rswail.ast import statement, expression, expr_name_access, expr_base_value, expr_apply, stmt_declaration, stmt_expression
from rswail.value import Integer

"""Define Swail's grammar.

When you want to modify this grammar, be sure to also update the NodesToASTVisitor
which assembles the generated nodes into an AST that Swail can understand.
"""
# TODO: add unicode classes to the grammar
# note that rpython parsing is bytes-based :(
regexes, rules, ToAST = parse_ebnf("""
IGNORE: "[ ]|#[^\n]*";
NEWLINE: "\n";
INDENT: "<indent>\t";
DEDENT: "<dedent>\t";

LITERAL_INT: "[0-9]+";
NAME: "[A-Za-z_][A-Za-z0-9_]*";

file: [NEWLINE]* (statement [NEWLINE]+)* [EOF];
block: INDENT (statement [NEWLINE]+)+ DEDENT;
statement: <declaration> | <expression_stmt>;
declaration: general_name NAME arg_list (":" NEWLINE block)?;
expression_stmt: expression;

expression: <apply> | <callable>;
callable: <name_access> | <base_value> | "(" <expression> ")";
name_access: general_name;
apply: callable arg_list;
base_value: LITERAL_INT;

arg_list: "(" (expression [","])* expression? ")";
general_name: (NAME ["."])* NAME;
""")

"""Convert a lexed bytestring into parser nodes.

This step is done using an automatically generated parser which takes care of
all the boring details.
"""
lexed_to_nodes = make_parse_function(regexes, rules, eof=True)

def swail_lexer(program_code):
	"""To make parsing a bit easier, we first convert indentation to explicit tokens."""
	indent_level = 0
	char = '\n'
	source = iter(program_code)
	eof = False
	# we break from the loop when there are no more characters in the file
	while not eof:
		if char == '\n':
			line_indent = 0
			# count the indentation on this line
			while True:
				try:
					char = next(source)
				except StopIteration:
					eof = True
					break
				if char != '\t':
					break
				line_indent += 1
			# and print that amount of indent/dedent tokens
			for i in range(indent_level, line_indent):
				for c in "<indent>\t":
					yield c
			for i in range(line_indent, indent_level):
				# TODO: remove the \n at the end
				# workaround for ending each statement with newlines
				for c in "<dedent>\t\n":
					yield c
			indent_level = line_indent
		else:
			try:
				char = next(source)
			except StopIteration:
				break
		yield char

	yield "\n"
	for i in range(0, indent_level):
		for c in "<dedent>\t\n":
			yield c

class NodesToASTVisitor(RPythonVisitor):
	"""Converts the nodes from the parser generator into a Swail AST.
	
	The nodes_to_ast function wraps this conversion for a Swail program.
	"""

	def __init__(self):
		pass

	def general_symbol_visit(self, node):
		return node

	def general_nonterminal_visit(self, node):
		node.children = list(map(self.dispatch, node.children))
		# skip any intermediate symbols generated by expanding + and * and ?
		if node.symbol[0] == '_' and len(node.children) == 1:
			return node.children[0]
		raise NotImplementedError

	# TODO: get rid of these fragile cases
	def visit___file_rest_0_0(self, node):
		assert len(node.children) in [1, 2]
		if len(node.children) == 1:
			return []
		else:
			return self.dispatch(node.children[0])
	def visit__maybe_symbol2(self, node):
		assert len(node.children) == 3
		return self.dispatch(node.children[2])
	def visit__plus_symbol0(self, node):
		return None
	def visit__plus_symbol2(self, node):
		assert len(node.children) in [2, 3]
		result = [self.dispatch(node.children[0])]
		if len(node.children) == 3:
			assert node.children[2].symbol == "_plus_symbol2"
			result.extend(self.dispatch(node.children[2]))
		return result
	def visit__star_symbol1(self, node):
		assert len(node.children) in [2, 3]
		result = [self.dispatch(node.children[0])]
		if len(node.children) == 3:
			assert node.children[2].symbol == "_star_symbol1"
			result.extend(self.dispatch(node.children[2]))
		return result
	def visit__star_symbol3(self, node):
		assert len(node.children) in [2, 3]
		result = [self.dispatch(node.children[0])]
		if len(node.children) == 3:
			assert node.children[2].symbol == "_star_symbol3"
			result.extend(self.dispatch(node.children[2]))
		return result
	def visit__star_symbol5(self, node):
		assert len(node.children) in [2, 3]
		# TODO: support other encodings?
		result = [self.dispatch(node.children[0]).token.source.decode("utf-8")]
		if len(node.children) == 3:
			assert node.children[2].symbol == "_star_symbol5"
			result.extend(self.dispatch(node.children[2]))
		return result

	def visit_file(self, node):
		assert len(node.children) in [1, 2]
		return self.dispatch(node.children[-1])
	def visit_block(self, node):
		assert len(node.children) == 3
		return self.dispatch(node.children[1])

	def visit_statement(self, node):
		assert len(node.children) == 1
		return self.dispatch(node.children[0])
	def visit_declaration(self, node):
		if len(node.children) == 3:
			block = []
		else:
			assert len(node.children) == 4
			block = self.dispatch(node.children[3])
		header = self.dispatch(node.children[0])
		name = self.dispatch(node.children[1])
		args = self.dispatch(node.children[2])
		return stmt_declaration(header, name, args, block)
	def visit_expression_stmt(self, node):
		assert len(node.children) == 1
		return stmt_expression(self.dispatch(node.children[0]))

	def visit_expression(self, node):
		assert len(node.children) == 1
		return self.dispatch(node.children[0])
	def visit_callable(self, node):
		assert len(node.children) == 1
		return self.dispatch(node.children[0])
	def visit_name_access(self, node):
		assert len(node.children) == 1
		return expr_name_access(self.dispatch(node.children[0]))
	def visit_apply(self, node):
		assert len(node.children) == 2
		return expr_apply(self.dispatch(node.children[0]), self.dispatch(node.children[1]))
	def visit_base_value(self, node):
		assert len(node.children) == 1
		value_symbol = node.children[0]
		if value_symbol.symbol == "LITERAL_INT":
			return Integer.from_decimal(value_symbol.token.source)
		else:
			raise NotImplementedError

	def visit_arg_list(self, node):
		assert len(node.children) >= 2
		# strip out the parentheses
		args = node.children[1:len(node.children)-1]
		return list(map(self.dispatch, args))
	def visit_general_name(self, node):
		assert len(node.children) in [1, 2]
		if len(node.children) == 2:
			result = self.dispatch(node.children[0])
		else:
			result = []
		assert node.children[-1].symbol == "NAME"
		# TODO: support other encodings?
		result.append(node.children[-1].token.source.decode("utf-8"))
		return result

def nodes_to_ast(program_nodes):
	"""Convert the nodes we received from the generated parser into Swail AST.
	
	The nodes we get should make up a full file.
	
	This step is especially useful for implementing declaration statements,
	since they will operate on the AST we produce here.
	"""
	visitor = NodesToASTVisitor()
	return visitor.dispatch(program_nodes)

def swail_parser(program_code):
	"""Parse a string representing a single Swail file into an AST.
	
	This is probably the function you want to use during execution.
	"""
	# TODO directly produce rlib.parsing tokens
	lexed = "".join(swail_lexer(program_code))
	nodes = lexed_to_nodes(lexed)
	return nodes_to_ast(nodes)
