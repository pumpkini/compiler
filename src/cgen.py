import logging
from lark import Lark, logger, __file__ as lark_file, ParseError, Tree
from lark.visitors import Interpreter

from SymbolTable import SymbolTable


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
		code = ''
		code += ''
		return code


	    

def generate_tac(code):
	try:
		tree = parser.parse(code)
		print(tree.pretty())
		root_symbol_table = SymbolTable()
		Cgen().visit(tree,  symbol_table= root_symbol_table)
		
	except ParseError as e:
		# TODO
		print(e)
		pass
	

if __name__ == "__main__":
	inputfile = 'example.d'
	code = ""
	with open(inputfile, "r") as input_file:
		code = input_file.read()
	generate_tac(code)
