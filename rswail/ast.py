from rswail.bytecode import Instruction
from rswail.cons_list import cons_list, from_list, to_list
from rswail.struct import Struct, StructInstance, construct
from rswail.value import Integer, String, Value

statement = Struct(u"statement", {
	u"declaration": [u"header", u"name", u"args", u"body"],
	u"expression": [u"expr"],
})

expression = Struct(u"expression", {
	u"name_access": [u"name"],
	u"apply": [u"func", u"args"],
	u"base_value": [u"value"],
})

def expr_name_access(name):
	return construct(expression, u"name_access", name)
def expr_base_value(value):
	assert isinstance(value, Value)
	return construct(expression, u"base_value", value)
def expr_apply(function, args):
	assert args.member.parent == cons_list
	return construct(expression, u"apply", function, args)
def expr_from_int(value):
	assert isinstance(value, int)
	return expr_base_value(Integer.from_int(value))
def stmt_declaration(header, name, args, body):
	return construct(statement, u"declaration", header, name, args, body)
def stmt_expression(expr):
	return construct(statement, u"expression", expr)

class Closure:
	"""Represents a set of variables during compilation.
	
	Not to be confused with a stack frame,
	which represents a set of variables during execution.
	A closure can cause many stack frames,
	e.g. when a function is called many times.
	"""
	def __init__(self):
		"""Make a new closure."""
		
		"""The variables bound in this closure.
		
		We need to track these variables so we can load them from the
		appropriate stack frame whenever they're used.
		
		Since RPython doesn't support sets, we make this a dict {key: None}
		"""
		self.bound_variables = {}
		"""The free variables in this closure which will need to be bound.
		
		We need to track these variables so we can load them from the
		appropriate stack frame.
		
		Note that bound_variables and used_variables can have any kind of overlap.
		"""
		self.used_variables = {}
	def make_bound(self, name):
		"""Remember that a declaration introduces a new name."""
		assert isinstance(name, unicode)
		self.bound_variables[name] = None
	def make_used(self, name):
		"""Remember that an expression wants to load a variable."""
		assert isinstance(name, unicode)
		self.used_variables[name] = None
	def get_free_variables(self):
		"""Calculate which variables need to be closed over in the outer frame.
		
		Returns a dict {variable: None} since RPython has no sets.
		"""
		result = {}
		for key in self.used_variables:
			if key not in self.bound_variables:
				result[key] = None
		return result

def compile_statement(program, block_id, stmt, closure):
	"""Add code to implement the statement to the given block.
	
	After a statement is executed, the stack should not have changed, except
	exactly one new value is now on top.
	
	Returns the block id that any code after this statement should append to.
	"""
	assert isinstance(stmt, StructInstance)
	if stmt.member.name == u"declaration":
		(header, name, args, body) = stmt.values
		header_expr = expr_name_access(header)
		# convert all the arguments to base values so we can call with them
		name_expr = expr_base_value(name)
		args_expr = expr_base_value(args)
		body_expr = expr_base_value(body)
		call_expr = expr_apply(header_expr, from_list([name_expr, args_expr, body_expr]))
		# run the header against the AST
		block_id = compile_expression(program, block_id, call_expr, closure)
		
		# store it as a name
		program.add_instruction(block_id, Instruction.DUP, 1)
		name_id = program.add_name(block_id, name)
		program.add_instruction(block_id, Instruction.STORE_LOCAL, name_id)
		closure.make_bound(name)
		
		# return value of the statement is whatever we just stored
		return block_id
	elif stmt.member.name == u"expression":
		(expr,) = stmt.values
		# return value is the value of the expression
		return compile_expression(program, block_id, expr, closure)

def compile_expression(program, block_id, expr, closure):
	"""Add code to implement the expression to the given block.
	
	After an expression is executed, the stack should not have changed, except
	exactly one new value is now on top.
	
	Returns the block id that any code after this expression should append to.
	"""
	if expr.member.name == u"name_access":
		# get the root and all its attributes
		(name,) = expr.values
		assert name.member == cons_list.members[u"cons"]
		root, tail = name.values
		assert isinstance(root, String)
		
		# load the root
		closure.make_used(root.value)
		root_id = program.add_name(block_id, root.value)
		program.add_instruction(block_id, Instruction.LOAD_LOCAL, root_id)
		
		# load its attributes
		while tail.member == cons_list.members[u"cons"]:
			attr, tail = tail.values
			assert isinstance(attr, String)
			attr_id = program.add_name(block_id, attr.value)
			program.add_instruction(block_id, Instruction.LOAD_ATTR, attr_id)
		assert tail.member == cons_list.members[u"empty"]
		return block_id
	elif expr.member.name == u"apply":
		(function_expr, arg_exprs) = expr.values
		block_id = compile_expression(program, block_id, function_expr, closure)
		arg_expr_list = to_list(arg_exprs)
		for arg_expr in arg_expr_list:
			block_id = compile_expression(program, block_id, arg_expr, closure)
		program.add_instruction(block_id, Instruction.CALL, len(arg_expr_list))
		return block_id
	elif expr.member.name == u"base_value":
		(value,) = expr.values
		value_id = program.add_constant(block_id, value)
		program.add_instruction(block_id, Instruction.PUSH_CONST, value_id)
		return block_id
