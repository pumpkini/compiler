import logging
from lark import Lark, logger, __file__ as lark_file, ParseError, Tree
from lark.visitors import Interpreter

from SymbolTable import SymbolTable, Variable


logger.setLevel(logging.DEBUG)

from pathlib import Path

grammer_path = Path(__file__).parent
grammer_file = grammer_path / 'grammer.lark'

parser = Lark.open(grammer_file, rel_to=__file__, parser="lalr")

class Cgen(Interpreter):
	def visit(self, tree, *args, **kwargs):
		f = getattr(self, tree.data)
		wrapper = getattr(f, 'visit_wrapper', None)
		if wrapper is not None:
			return f.visit_wrapper(f, tree.data, tree.children, tree.meta)
		else:
			return f(tree, *args, **kwargs)
	
	def visit_children(self, tree, *args, **kwargs):
		return [self.visit(child, *args, **kwargs) if isinstance(child, Tree) else child
                for child in tree.children]
	
	def __default__(self, tree, *args, **kwargs):
		return self.visit_children(tree, *args, **kwargs)


    ### Cgen methods
	def program(self, tree, *args, **kwargs):
		symbol_table = kwargs.get('symbol_table')
		code = '\n'.join(self.visit_children(tree, symbol_table = symbol_table))
		return code
		
	def	decl(self, tree, *args, **kwargs):
		symbol_table = kwargs.get('symbol_table')
		code = ''
		for decl in tree.children:
			if decl.data == 'function_decl':
				code += self.visit(decl,tree, symbol_table = symbol_table)
		return code
	
	def function_decl(self, tree, *args, **kwargs):
		symbol_table = kwargs.get('symbol_table')

		type_ = self.visit(tree.children[0])
		func_name = tree.children[1].value
		formals = self.visit(tree.children[2])
		statement_block = self.visit(tree.children[3])

		# TODO check return type
		# TODO do something with arguments

		code = f"""
		{func_name}:
			{statement_block}
		""".replace("\n\t\t", "\n")

		return code

	def statement_block(self, tree, *args, **kwargs):
		symbol_table = kwargs.get('symbol_table')

		new_symbol_table = SymbolTable(parent=symbol_table)

		childrens_code = self.visit_children(tree, symbol_table = new_symbol_table)
		code = '\n\t'.join(childrens_code)
		return code

	def variable(self, tree, *args, **kwargs):
		type_ = self.visit(tree.children[0])
		var_name = tree.children[1].value

		# TODO do something (but what?)
		return ""	

	def expr_assign(self, tree, *args, **kwargs):
		l_value = self.visit(tree.children[0], kwargs)
		expr = self.visit(tree.children[1], kwargs)
		
		# TODO store new value for l_value
		code = "expr assign"
		return code

	def ident(self, tree, *args, **kwargs):
		return tree.children[0].value
		
	def constant(self, tree, *args, **kwargs):
		return tree.children[0].value
		
	def print_stmt(self, tree, *args, **kwargs):
		actuals = self.visit(tree.children[1])

		## TODO print (or maybe another place)

		code = "print"

		return code

	def actuals(self, tree, *args, **kwargs):
		actuals = self.visit_children(tree, args, kwargs)
		return actuals





def generate_tac(code):
	try:
		tree = parser.parse(code)
		print(tree.pretty())
		root_symbol_table = SymbolTable()
		mips_code = Cgen().visit(tree,  symbol_table= root_symbol_table)
		return mips_code
	except ParseError as e:
		# TODO
		print(e)
		pass
	

if __name__ == "__main__":
	inputfile = 'example.d'
	code = ""
	with open(inputfile, "r") as input_file:
		code = input_file.read()
	code = generate_tac(code)
	print("#### code ")
	print(code)
