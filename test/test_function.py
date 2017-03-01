from rswail.ast import Closure, compile_expression, expr_apply, expr_base_value
from rswail.bytecode import Instruction, Program
from rswail.function import CodeFunction
from rswail.cons_list import empty
from rswail.value import Integer
from target import start_execution

def test_defined_function_call():
	"""Define a function manually and call it."""
	program = Program()

	# Construct the function
	return_expr = expr_base_value(Integer.from_int(37))
	func_closure = Closure()
	func_block = program.new_block()
	block_id = compile_expression(program, func_block, return_expr, func_closure)
	# get the return label and jump to it
	program.add_instruction(block_id, Instruction.JUMP_LABEL, 2)

	# FIXME debug code
	print(program.blocks[func_block].pretty_print())

	# And call it
	func_expr = expr_base_value(CodeFunction(u"func", func_block))
	call_expr = expr_apply(func_expr, empty())
	main_closure = Closure()
	compile_expression(program, program.start_block, call_expr, main_closure)

	stack = start_execution(program)
	tos = stack[-1]

	assert tos.eq(37)
