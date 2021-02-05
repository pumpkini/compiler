import logging
from lark import Lark, logger, __file__ as lark_file, ParseError, Tree
from lark.visitors import Interpreter, v_args

logger.setLevel(logging.DEBUG)

from pathlib import Path

grammer_path = Path(__file__).parent
grammer_file = grammer_path / 'grammer.lark'

parser = Lark.open(grammer_file, rel_to=__file__, parser="lalr")


def generate_tac(code):
	try:
		tree = parser.parse(code)
		root_symbol_table = SymbolTable()
		Cgen().visit(tree,  symbol_table= root_symbol_table)
		
	except ParseError as e:
		# TODO
		pass
	

if __name__ == "__main__":
	inputfile = '../tmp/in1.d'
	code = ""
	with open(inputfile, "r") as input_file:
		code = input_file.read()

	generate_tac(code)
