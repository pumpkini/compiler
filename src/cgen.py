import logging
from lark import Lark, logger, __file__ as lark_file, ParseError, Tree
from lark.visitors import Interpreter

from SymbolTable import Function, SymbolTable, Variable, Type

from pathlib import Path

DATA_POINTER = 0
stack = []


class SemanticError(Exception):
	def __init__(self, message="", line=None, col=None):
		self.message = message
		self.line = line
		self.col = col

	def __str__(self) -> str:
		return f"l{self.line}-c{self.col}:: {self.message}"


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

		try:
			code = '\n'.join(self.visit_children(tree, symbol_table = symbol_table))
		
			code += """
			
			### function: Print_bool(a0: boolean_value)
			print_bool: 
				beq $a0, $zero, print_bool_false
				b print_bool_true

			print_bool_false:
				la $a0, falseStr
				li $v0, 4	# sys call for print string 
				syscall
				b print_bool_end

			print_bool_true:
				la $a0, trueStr
				li $v0, 4	# sys call for print string
				syscall
				b print_bool_end

			print_bool_end:
				jr $ra

			""".replace("\t\t\t","")

			code += """
			.data
			falseStr: .asciiz "false"
			trueStr: .asciiz "true"
			""".replace("\t\t\t","")

		except SemanticError as err:
			print(err)
			# TODO check
			code = """
			.text
			.globl main

			main:
			la $a0 , errorMsg
			addi $v0 , $zero, 4
			syscall
			jr $ra

			.data
			errorMsg: .asciiz "Semantic Error"
			""".replace("\t\t\t","\t")

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
	jr $ra
		"""

		return code

	def statement_block(self, tree, *args, **kwargs):
		symbol_table = kwargs.get('symbol_table')

		new_symbol_table = SymbolTable(parent=symbol_table)

		children_code = self.visit_children(tree, symbol_table = new_symbol_table)
		children_code = [c if c else '' for c in children_code]

		code = '\n'.join(children_code)

		return code

	def variable(self, tree, *args, **kwargs):
		symbol_table = kwargs.get('symbol_table')

		type_name = self.visit(tree.children[0],**kwargs)
		var_name = tree.children[1].value

		type_ = Type.get_type_by_name(type_name)

		if not type_:
			raise Exception(f"NOOOOO {type_name} is not in types")

		
		global DATA_POINTER

		if var_name in symbol_table.variables:
			### TODO var_name already exist in this scope. error?
			pass

		size = 1
		total_size = size * type_.size

		symbol_table.variables[var_name] = Variable(
				name=var_name,
				type_=type_,
				address=DATA_POINTER,
				size=size
				)
			
		DATA_POINTER += total_size
		
		return ""	

	def expr_assign(self, tree, *args, **kwargs):
		global stack

		code = ''
		
		self.visit(tree.children[0],**kwargs)
		variable = stack.pop()

		code += self.visit(tree.children[1],**kwargs)

		if not variable:
			# TODO variable not found noooo
			return ''

		# TODO check type of var and expr

		code += f"""
				### store
				lw $t0, 0($sp)
				sw $t0, {variable.address}($gp) 	
				""".replace("\t\t\t\t","\t")
		
		stack.pop()
		return code


	def add(self, tree, *args, **kwargs):
		code = ''
		code += self.visit(tree.children[0],**kwargs)
		var1 = stack.pop()
		code += self.visit(tree.children[1],**kwargs)
		var2 = stack.pop()

		if var1.type_.name != var2.type_.name:
			print(var1.type_.name, var2.type_.name)
			raise SemanticError('var1 type != var2 type in \'add\'', line=tree.meta.line, col=tree.meta.column)
		
		elif var1.type_.name == "int":
			code += f"""
				### add
				lw $t0, 0($sp)
				lw $t1, 4($sp)
				add $t2, $t1, $t0
				sw $t2, 4($sp) 
				addi $sp, $sp, 4
				""".replace("\t\t\t\t", "\t")

		elif var1.type_.name == "double":
			code += f"""
				### add
				l.d $f1, 0($sp)
				l.d $f2, 4($sp)
				add.d $f3, $f2, $f1
				s.d $f3, 4($sp) 
				addi $sp, $sp, 4
				""".replace("\t\t\t\t", "\t")
		
		elif var1.type_.name == "string":
			# TODO
			pass
		elif  var1.type_.name == "array":
			# TODO
			pass
		else:
			raise SemanticError



		stack.append(Variable(type_=var1.type_))
		return code

	def sub(self, tree, *args, **kwargs):
		code = ''
		code += self.visit(tree.children[0],**kwargs)
		var1 = stack.pop()
		code += self.visit(tree.children[1],**kwargs)
		var2 = stack.pop()

		if var1.type_.name != var2.type_.name:
			# TODO nooo what to do now
			raise SemanticError
		
		elif var1.type_.name == "int":
			code += f"""
				### sub
				lw $t0, 0($sp)
				lw $t1, 4($sp)
				sub $t2, $t1, $t0
				sw $t2, 4($sp) 
				addi $sp, $sp, 4
				""".replace("\t\t\t\t", "\t")

		elif var1.type_.name == "double":
			code += f"""
				### sub
				l.d $f1, 0($sp)
				l.d $f2, 4($sp)
				sub.d $f3, $f2, $f1
				s.d $f3, 4($sp) 
				addi $sp, $sp, 4
				""".replace("\t\t\t\t", "\t")

		elif var1.type_.name == "string":
			# TODO
			pass
		elif  var1.type_.name == "array":
			# TODO
			pass
		else:
			raise SemanticError


		stack.append(Variable(type_=var1.type_))
		return code

	def ident(self, tree, *args, **kwargs):
		symbol_table = kwargs.get('symbol_table')

		var_name = tree.children[0].value
		variable = symbol_table.find_var(var_name)

		stack.append(variable)
		code = f"""
				### ident
				lw $t0, {variable.address}($gp)
				addi $sp, $sp, -4
				sw $t0, 0($sp)
				""".replace("\t\t\t\t", "\t")
		return code
		

	def constant(self, tree, *args, **kwargs):
		# TODO for other types

		constant_type = tree.children[0].type
		value = "????"
		type_ = "????"
		if constant_type == 'INTCONSTANT':
			value = int(tree.children[0].value)
			type_ = Type.get_type_by_name('int')

		stack.append(Variable(type_=type_))

		code = f"""
				### constant
				li $t0, {value}
				addi $sp, $sp, -4
				sw $t0, 0($sp)
				""".replace("\t\t\t\t","\t")
		
		return code
		
	def print_stmt(self, tree, *args, **kwargs):
		symbol_table = kwargs.get('symbol_table')

		code = f"""\t### print stmt begin"""

		stack_size_initial = len(stack)

		actuals = self.visit(tree.children[1],**kwargs)
		print(actuals)
		code += actuals
		
		if len(stack) == stack_size_initial:
			return code


		sp_offset = (len(stack) - stack_size_initial - 1) * 4
		for var in stack[stack_size_initial:]:
			if var.type_.name  == 'int':
				code += f"""
					### print int	
					li $v0, 1		# sys call for print integer 
					lw $a0, {sp_offset}($sp)
					syscall
					""".replace("\t\t\t\t\t","\t")	
			
			if var.type_.name  == 'bool':
				# TODO  refactor this
				code += f"""
					### print bool	
					lw $a0, {sp_offset}($sp)
					move $s0, $ra 	#save ra
					jal print_bool
					move $ra, $s0 	#restore ra
					""".replace("\t\t\t\t","")	
			sp_offset -= 4

			# TODO other type


		code += f"""
				addi $sp, $sp, {(len(stack) - stack_size_initial ) * 4}
				### print stmt end
				""".replace("\t\t\t\t","\t")

		return code

	def actuals(self, tree, *args, **kwargs):
		actuals = self.visit_children(tree, args,**kwargs)
		code = '\n'.join(actuals)
		return code

	def type(self, tree, *args, **kwargs):
		return tree.children[0].value


	def boolean_expr(self, tree, *args, **kwargs):
		code = ''
		code += self.visit(tree.children[0],**kwargs)
		var1 = stack.pop()
		code += self.visit(tree.children[2],**kwargs)
		var2 = stack.pop()


		if var1.type_.name != var2.type_.name:
			raise SemanticError('var1 type != var2 type in \'less\'', line=tree.meta.line, col=tree.meta.column)

		if var1.type_.name != 'int' and var1.type_.name != 'double':
			raise SemanticError('variables type are not double or int in \'less\'', line=tree.meta.line, col=tree.meta.column)


		if var1.type_.name == 'int':
			# t0 operand 1
			# t1 operand 2

			operand = tree.children[1].value
			print("OPERAND", operand)
			compare_line = ""
			if operand == '<':
				compare_line ="slt $t2, $t0, $t1"
			elif operand == '>':
				compare_line = "sgt $t2, $t0, $t1"
			elif operand == '<=':
				compare_line = "sge $t2, $t1, $t0"
			elif operand == '>=':
				compare_line = "sge $t2, $t0, $t1"
			elif operand == '==':
				compare_line = "seq $t2, $t0, $t1"
			elif operand == '!=':
				compare_line = "sne $t2, $t0, $t1"

			code += f"""
					### boolean_expr
					lw $t1, 0($sp)
					lw $t0, 4($sp)
					{compare_line}
					sw $t2, 4($sp) 
					#greater_equal
					addi $sp, $sp, 4
					""".replace("\t\t\t\t\t", "\t")
		else:
			# TODO for double
			pass

		stack.append(Variable(type_=Type.get_type_by_name('bool')))
		return code
		



def generate_tac(code):
	logger.setLevel(logging.DEBUG)
	grammer_path = Path(__file__).parent
	grammer_file = grammer_path / 'grammer.lark'
	parser = Lark.open(grammer_file, rel_to=__file__, parser="lalr", propagate_positions=True)
	init()
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
	

def init():
	Type("int",4)
	Type("double",4)
	Type("bool",4)
	Type("string",1)
	Type("void",0)



if __name__ == "__main__":
	# inputfile = 'example.d'
	inputfile = '../tmp/in1.d'
	code = ""
	with open(inputfile, "r") as input_file:
		code = input_file.read()
	code = generate_tac(code)
	print("#### code ")
	print(code)

		
	output_file = open("../tmp/res.mips", "w")
	output_file.write(code)
