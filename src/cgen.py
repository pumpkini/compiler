import logging
from lark import Lark, logger, __file__ as lark_file, ParseError, Tree
from lark.visitors import Interpreter

from SymbolTable import Function, SymbolTable, Variable, Type


logger.setLevel(logging.DEBUG)

from pathlib import Path

grammer_path = Path(__file__).parent
grammer_file = grammer_path / 'grammer.lark'

parser = Lark.open(grammer_file, rel_to=__file__, parser="lalr")



DATA_POINTER = 0
stack = []

class Cgen(Interpreter):
	def visit(self, tree, *args, **kwargs):
		f = getattr(self, tree.data)
		wrapper = getattr(f, 'visit_wrapper', None)
		if wrapper is not None:
			return f.visit_wrapper(f, tree.data, tree.children, tree.meta, *args, **kwargs)
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

		type_ = self.visit(tree.children[0],**kwargs)
		func_name = tree.children[1].value
		formals = self.visit(tree.children[2],**kwargs)

		symbol_table.functions[func_name] = Function(
				name = func_name,
				type_ = type_,
				arguments = formals
		)

		statement_block = self.visit(tree.children[3],**kwargs)

		# TODO check return type
		# TODO do something with arguments
		# TODO save registers, do sth with fp ra
		

		code = f"""
{func_name}:
	{statement_block}
		"""

		return code

	def statement_block(self, tree, *args, **kwargs):
		symbol_table = kwargs.get('symbol_table')

		new_symbol_table = SymbolTable(parent=symbol_table)

		childrens_code = self.visit_children(tree, symbol_table = new_symbol_table)
		
		childrens_code = [c if c else '' for c in childrens_code]

		code = '\n'.join(childrens_code)

		return code

	def variable(self, tree, *args, **kwargs):
		symbol_table = kwargs.get('symbol_table')

		type_ = self.visit(tree.children[0],**kwargs)
		var_name = tree.children[1].value

		size = 4
		if type_ in TYPE_SIZE:
			size = TYPE_SIZE[type_]
		else:
			raise Exception(f"NOOOOO {type_} is not in TYPE_SIZE")

		
		global DATA_POINTER

		if var_name in symbol_table.variables:
			### TODO var_name already exist in this scope. error?
			pass


		symbol_table.variables[var_name] = Variable(
				name=var_name,
				type_=type_,
				address=DATA_POINTER,
				size=size
				)
			
		DATA_POINTER += size
		
		return ""	

	def expr_assign(self, tree, *args, **kwargs):
		# l_value = expr
		symbol_table = kwargs.get('symbol_table')

		code = ''
		variable = self.visit(tree.children[0],**kwargs, return_var=True)
		code += self.visit(tree.children[1],**kwargs)

		if not variable:
			# TODO variable not found noooo
			return ''

		# TODO check type of var and expr

		code += f"""
				### store
				li $t0, 0($sp)
				sw $t0, {variable.address}($gp) 	
				""".replace("\t\t\t\t","\t")
		return code


	def add(self, tree, *args, **kwargs):
		code = ''
		code += self.visit(tree.children[0],**kwargs)
		code += self.visit(tree.children[1],**kwargs)
		code += f"""
				### add
				li $t0, 0($sp)
				li $t1, 4($sp)
				add $t2, $t1, $t0
				sw $t2, 4($sp) 
				addi $sp, $sp, 4
				""".replace("\t\t\t\t", "\t")
		return code

	def ident(self, tree, return_var=False, *args, **kwargs):
		symbol_table = kwargs.get('symbol_table')

		var_name = tree.children[0].value
		variable = symbol_table.find_var(var_name)

		if return_var:
			return variable
		
		code = f"""
				### ident
				lw $t0, {variable.address}($gp)
				subi $sp, $sp, 4
				sw $t0, 0($sp)
				""".replace("\t\t\t\t", "\t")
		return code
		
	def constant(self, tree, *args, **kwargs):
		# TODO for other types
		# TODO store type somewhere

		constant_type = tree.children[0].type
		value = "????"
		if constant_type == 'INTCONSTANT':
			value = int(tree.children[0].value)

		code = f"""
				### constant
				li $t0, {value}
				subi $sp, $sp, 4
				sw $t0, 0($sp)
				""".replace("\t\t\t\t","\t")
		
		# stack.append(int(tree.children[0].value)) 
		return code
		
	def print_stmt(self, tree, *args, **kwargs):
		symbol_table = kwargs.get('symbol_table')

		code = f"""
			### print stmt start
			add $s0, $sp, $zero
		""".replace("\t\t\t\t","\t")

		actuals = self.visit(tree.children[1],**kwargs)

		## TODO print (or maybe another place)

		code += actuals

		code += f"""
			### print stmt continue
			li $t0, 0($sp)
			addi $sp, $sp, 4
			lw {var_reg}, {variable.address}($gp)
			syscall	
			lw {var_reg}, {variable.address}($gp)
			syscall	
		"""
		code = ""
		for actual in actuals:
			# TODO this only work if actual is a single symbol :(
			
			variable = symbol_table.find_var(actual)
		
			if not variable:
				# TODO variable not found noooo
				continue
				
			var_reg = "$a0"
			sys_call_code = 1
			if variable.type_ == 'int':
				sys_call_code = 1
			elif variable.type == 'double':
				sys_call_code = 3
				var_reg = "$f12"
			elif variable.type == 'string': # TODO not sure
				sys_call_code = 4
				
			code += f"""
				### print_stmt
				li $v0, {sys_call_code} 	
				lw {var_reg}, {variable.address}($gp)
				syscall
				""".replace("\t\t\t\t","\t")

		return code

	def actuals(self, tree, *args, **kwargs):
		actuals = self.visit_children(tree, args,**kwargs)
		return actuals

	def type(self, tree, *args, **kwargs):
		return tree.children[0].value




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
