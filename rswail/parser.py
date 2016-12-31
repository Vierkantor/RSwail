from rpython.rlib.parsing.ebnfparse import parse_ebnf, make_parse_function
from rpython.rlib.parsing.parsing import ParseError

from rswail.ast import statement, expression

# TODO: add unicode classes to the grammar
# note that rpython parsing is bytes-based :(
regexes, rules, ToAST = parse_ebnf("""
IGNORE: "[ ]|#[^\n]*";
NEWLINE: "\n";
INDENT: "<indent>\t";
DEDENT: "<dedent>\t";

LITERAL_INT: "[0-9]+";
NAME: "[A-Za-z_][A-Za-z0-9_]*";

file: statements | [NEWLINE+];
statements: [NEWLINE*] (statement [NEWLINE+])* statement [NEWLINE*];
statement: <headered> | <expression_stmt>;
headered: general_name NAME arg_list (":" INDENT statements DEDENT)?;
expression_stmt: expression;

expression: <apply> | <callable>;
callable: <name_access> | <base_value> | "(" <expression> ")";
name_access: general_name;
apply: callable arg_list;
base_value: LITERAL_INT;

arg_list: ["("] (expression [","])* expression? [")"];
general_name: (NAME ["."])* NAME;
""")

"""Convert a lexed bytestring into parser nodes.

This step is done using an automatically generated parser which takes care of
all the boring details.
"""
lexed_to_nodes = make_parse_function(regexes, rules, eof=True)

# TODO: automatic lexing
def swail_lexer(program_code):
	raise NotImplementedError
def nodes_to_ast(program_nodes):
	raise NotImplementedError
def swail_parser(program_code):
	"""Parse a string representing a single Swail file into an AST.
	
	This is probably the function you want to use during execution.
	"""
	lexed = swail_lexer(program_code)
	nodes = lexed_to_nodes(lexed)
	return nodes_to_ast(nodes)
