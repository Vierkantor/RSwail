from rswail.bytecode import Instruction
from rswail.struct import Struct, construct
from rswail.value import Integer, Value

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
def expr_apply(function, *args):
	return construct(expression, u"apply", function, args)
def expr_from_int(value):
	assert isinstance(value, int)
	return expr_base_value(Integer.from_int(value))
def stmt_expression(expr):
	return construct(statement, u"expression", expr)

def compile_statement(program, block_id, stmt):
	"""Add code to implement the statement, to the given block.
	
	After a statement is executed, the stack should not have changed, except
	exactly one new value is now on top.
	
	Returns the block id that any code after this statement should append to.
	"""
	if stmt.member.name == u"declaration":
		(header, name, args, body) = stmt.values
		header_expr = expr_name_access(header)
		# convert all the arguments to base values so we can call with them
		name_expr = expr_base_value(name)
		args_expr = expr_base_value(args)
		body_expr = expr_base_value(body)
		call_expr = expr_apply(header_expr, name_expr, args_expr, body_expr)
		# run the header against the AST
		block_id = compile_expression(program, block_id, call_expr)
		
		# store it as a name...
		program.add_instruction(block_id, Instruction.DUP, 1)
		# TODO: what if the name isn't local?
		name_id = program.add_name(block_id, name)
		program.add_instruction(block_id, Instruction.STORE_LOCAL, name_id)
		# return value of the statement is whatever we just stored
		return block_id
	elif stmt.member.name == u"expression":
		(expr,) = stmt.values
		# return value is the value of the expression
		return compile_expression(program, block_id, expr)

def compile_expression(program, block_id, expr):
	"""Add code to implement the expression, to the given block.
	
	After an expression is executed, the stack should not have changed, except
	exactly one new value is now on top.
	
	Returns the block id that any code after this expression should append to.
	"""
	if expr.member.name == u"name_access":
		(name,) = expr.values
		# TODO: what if the name isn't local?
		name_id = program.add_name(block_id, name)
		program.add_instruction(block_id, Instruction.LOAD_LOCAL, name_id)
		return block_id
	elif expr.member.name == u"apply":
		(function_expr, arg_exprs) = expr.values
		block_id = compile_expression(program, block_id, function_expr)
		for arg_expr in arg_exprs:
			block_id = compile_expression(program, block_id, arg_expr)
		program.add_instruction(block_id, Instruction.CALL, len(arg_exprs))
		return block_id
	elif expr.member.name == u"base_value":
		(value,) = expr.values
		value_id = program.add_constant(block_id, value)
		program.add_instruction(block_id, Instruction.PUSH_CONST, value_id)
		return block_id
