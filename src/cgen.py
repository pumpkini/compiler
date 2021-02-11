import logging
from lark import Lark, logger, __file__ as lark_file, ParseError, Tree
from lark.visitors import Interpreter
from decimal import Decimal
from pathlib import Path

from symbol_table import Function, SymbolTable, Variable, Type, SymbolTableVisitor, ParentVisitor
from utils import SemanticError


stack = []


def IncLabels():
	Cgen.labels+=1
	return Cgen.labels


def IncDataPointer(size):
	cur = Cgen.data_pointer
	Cgen.data_pointer += size
	return cur

class Cgen(Interpreter):
	labels = 0
	data_pointer = 0


	def program(self, tree):
	
		code = '\n'.join(self.visit_children(tree))
	
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

		""".replace("\t\t","")

		code += """
		.data
		falseStr: .asciiz "false"
		trueStr: .asciiz "true"
		newLineStr: .asciiz "\\n"
		""".replace("\t\t","")

		return code
		
	def	decl(self, tree):

		code = ''
		for decl in tree.children:
			if decl.data == 'function_decl':
				code += self.visit(decl)
		
		return code
	
	def function_decl(self, tree):
		type_ = self.visit(tree.children[0])
		func_name = tree.children[1].value
		formals = self.visit(tree.children[2])

		statement_block = self.visit(tree.children[3])

		# TODO check return type
		# TODO do something with arguments
		# TODO save registers, do sth with fp ra
		
		code = f"""
{func_name}:
	{statement_block}
	jr $ra
		"""

		return code

	def statement_block(self, tree):
		children_code = self.visit_children(tree)
		children_code = [c if c else '' for c in children_code]
		code = '\n'.join(children_code)

		return code

	def variable(self, tree):
		type_ = self.visit(tree.children[0])
		var_name = tree.children[1].value		

		size = 1
		total_size = size * type_.size

		variable = tree.symbol_table.find_var(var_name)
	
		variable.size = size
		variable.address = IncDataPointer(total_size)
	
		return ""	

	def expr_assign(self, tree):
		global stack

		code = ''
		
		self.visit(tree.children[0])
		lvalue_var = stack.pop()

		code += self.visit(tree.children[1])
		expr_var = stack.pop()

		if lvalue_var.type_.name != expr_var.type_.name:
			raise SemanticError('lvalue type != expr type in \'expr_assign\'', tree=tree)
		
		if lvalue_var.type_.name == 'int' or lvalue_var.type_.name == 'bool':
			code += f"""
				### store
				lw $t0, 0($sp)
				addi $sp, $sp, 4
				sw $t0, {lvalue_var.address}($gp) 	
				""".replace("\t\t\t\t","\t")

		elif lvalue_var.type_.name == 'double':
			code += f"""
				### store
				l.d $f2, 0($sp)
				addi $sp, $sp, 4
				s.d $f2, {lvalue_var.address}($gp) 	
				""".replace("\t\t\t\t","\t")
		
		return code


	def add(self, tree):
		code = ''
		code += self.visit(tree.children[0])
		var1 = stack.pop()
		code += self.visit(tree.children[1])
		var2 = stack.pop()

		if var1.type_.name != var2.type_.name:
			raise SemanticError('var1 type != var2 type in \'add\'', tree=tree)
		
		elif var1.type_.name == "int":
			code += f"""
				### add int
				lw $t0, 0($sp)
				lw $t1, 4($sp)
				add $t2, $t1, $t0
				sw $t2, 4($sp) 
				addi $sp, $sp, 4
				""".replace("\t\t\t\t", "\t")

		elif var1.type_.name == "double":
			code += f"""
				### add double
				l.d $f2, 0($sp)
				l.d $f4, 4($sp)
				add.d $f6, $f4, $f2
				s.d $f6, 4($sp) 
				addi $sp, $sp, 4
				""".replace("\t\t\t\t", "\t")
		
		elif var1.type_.name == "string":
			# TODO
			pass
		elif  var1.type_.name == "array":
			# TODO
			pass
		else:
			raise SemanticError('types are not suitable for \'add\'', tree=tree)

		stack.append(Variable(type_=var1.type_))
		return code




	def sub(self, tree):
		code = ''
		code += self.visit(tree.children[0])
		var1 = stack.pop()
		code += self.visit(tree.children[1])
		var2 = stack.pop()

		if var1.type_.name != var2.type_.name:
			raise SemanticError('var1 type != var2 type in \'sub\'', tree=tree)
		
		elif var1.type_.name == "int":
			code += f"""
				### sub int
				lw $t0, 0($sp)
				lw $t1, 4($sp)
				sub $t2, $t1, $t0
				sw $t2, 4($sp) 
				addi $sp, $sp, 4
				""".replace("\t\t\t\t", "\t")

		elif var1.type_.name == "double":
			code += f"""
				### sub double
				l.d $f2, 0($sp)
				l.d $f4, 4($sp)
				sub.d $f6, $f4, $f2
				s.d $f6, 4($sp) 
				addi $sp, $sp, 4
				""".replace("\t\t\t\t", "\t")

		else:
			raise SemanticError('types are not suitable for \'sub\'', tree=tree)

		stack.append(Variable(type_=var1.type_))
		return code


	def mul(self, tree):
		code = ''
		code += self.visit(tree.children[0])
		var1 = stack.pop()
		code += self.visit(tree.children[1])
		var2 = stack.pop()

		if var1.type_.name != var2.type_.name:
			raise SemanticError('var1 type != var2 type in \'mul\'', tree=tree)
		
		elif var1.type_.name == "int":
			code += f"""
				### mul int
				lw $t0, 0($sp)
				lw $t1, 4($sp)
				mul $t2, $t1, $t0
				sw $t2, 4($sp) 
				addi $sp, $sp, 4
				""".replace("\t\t\t\t", "\t")
		
		elif var1.type_.name == "double":
			code += f"""
				### mul double
				l.d $f2, 0($sp)
				l.d $f4, 4($sp)
				mul.d $f6, $f4, $f2
				s.d $f6, 4($sp) 
				addi $sp, $sp, 4
				""".replace("\t\t\t\t", "\t")
		
		else:
			raise SemanticError('types are not suitable for \'mul\'', tree=tree)

		stack.append(Variable(type_=var1.type_))
		return code



	def div(self, tree):
		code = ''
		code += self.visit(tree.children[0])
		var1 = stack.pop()
		code += self.visit(tree.children[1])
		var2 = stack.pop()

		if var1.type_.name != var2.type_.name:
			raise SemanticError('var1 type != var2 type in \'div\'', tree=tree)
		
		elif var1.type_.name == "int":
			code += f"""
				### div int
				lw $t0, 0($sp)
				lw $t1, 4($sp)
				div $t2, $t1, $t0
				sw $t2, 4($sp) 
				addi $sp, $sp, 4
				""".replace("\t\t\t\t", "\t")
		
		elif var1.type_.name == "double":
			code += f"""
				### div double
				l.d $f2, 0($sp)
				l.d $f4, 4($sp)
				div.d $f6, $f4, $f2
				s.d $f6, 4($sp) 
				addi $sp, $sp, 4
				""".replace("\t\t\t\t", "\t")
		
		else:
			raise SemanticError('types are not suitable for \'div\'', tree=tree)

		stack.append(Variable(type_=var1.type_))
		return code



	def mod(self, tree):
		code = ''
		code += self.visit(tree.children[0])
		var1 = stack.pop()
		code += self.visit(tree.children[1])
		var2 = stack.pop()

		if var1.type_.name != var2.type_.name:
			raise SemanticError('var1 type != var2 type in \'mod\'', tree=tree)
		
		elif var1.type_.name == "int":
			code += f"""
				### mod
				lw $t0, 0($sp)
				lw $t1, 4($sp)
				div $t1, $t0
				mfhi $t2
				sw $t2, 4($sp) 
				addi $sp, $sp, 4
				""".replace("\t\t\t\t", "\t")
		
		else:
			raise SemanticError('types are not suitable for \'mod\'', tree=tree)

		stack.append(Variable(type_=var1.type_))
		return code




	def neg(self, tree):
		code = ''
		code += self.visit(tree.children[0])
		var = stack.pop()
		
		if var.type_.name == "int":
			code += f"""
				### neg int
				lw $t0, 0($sp)
				sub $t0, $zero, $t0
				sw $t0, 0($sp) 
				""".replace("\t\t\t\t", "\t")
		elif var.type_.name == "double":
			code += f"""
				### neg double
				l.d $f2, 0($sp)
				neg.d $f2, $f2
				s.d $f2, 0($sp)
				""".replace("\t\t\t\t", "\t")
		else:
			raise SemanticError('types are not suitable for \'neg\'', tree=tree)

		stack.append(Variable(type_=var.type_))
		return code


	# TODO  other l_value expr_ident expr_expr
	def ident(self, tree):
		var_name = tree.children[0].value
		variable = tree.symbol_table.find_var(var_name)
		
		if not variable:
			raise SemanticError('ident not found', tree=tree)
		
		stack.append(variable)

		code = ''
		if variable.type_.name == "int" or variable.type_.name == "bool":
			code = f"""
					### ident
					lw $t0, {variable.address}($gp)
					addi $sp, $sp, -4
					sw $t0, 0($sp)
					""".replace("\t\t\t\t\t", "\t")
		elif variable.type_.name == "double":
			code = f"""
					### ident
					l.d $f2, {variable.address}($gp)
					addi $sp, $sp, -4
					s.d $f2, 0($sp)
					""".replace("\t\t\t\t\t", "\t")
		return code
		

	def constant(self, tree):
		# TODO for other types

		constant_type = tree.children[0].type
		value = "????"
		type_ = "????"

		code = ''
		if constant_type == 'INTCONSTANT':
			value = tree.children[0].value.lower()
			type_ = tree.symbol_table.find_type('int')
			
			value = value.lstrip('0')
			
			code = f"""
				### constant int
				li $t0, {value}
				addi $sp, $sp, -4
				sw $t0, 0($sp)
				""".replace("\t\t\t","")
			

		if constant_type == 'DOUBLECONSTANT':
			value = tree.children[0].value.lower()
			type_ = tree.symbol_table.find_type('double')

			value = value.lstrip('0')

			# handle 3.
			if value[-1] == '.':
				value = value + '0'

			# handle 3.E2
			if '.e' in value:
				value = value.replace('.e', '.0e')

			code = f"""
				### constant double
				li.d $f2, {value}
				addi $sp, $sp, -4
				s.d $f2, 0($sp)
				""".replace("\t\t\t","")


		if constant_type == 'BOOLCONSTANT':
			value = 1 if tree.children[0].value == 'true' else 0
			type_ = tree.symbol_table.find_type('bool')
			code = f"""
				### constant bool
				li $t0, {value}
				addi $sp, $sp, -4
				sw $t0, 0($sp)
				""".replace("\t\t\t","")


		if constant_type == 'STRINGCONSTANT':
			value = tree.children[0].value[1:-1]
			type_ = tree.symbol_table.find_type('string')

			code = f"""
				### constant string
				li $v0, 9		# syscall for allocate byte
				li $a0, {len(value) + 1}
				syscall

				move $s0, $v0		# s0: address of string
				""".replace("\t\t\t","")

			for i,c in enumerate(value):
				code += f"""
				li $t0, '{c}'
				sb $t0, {i}($s0)
				""".replace("\t\t\t","")

			code += f"""
				li $t0, 0	# add a null terminator
				sb $t0, {len(value)}($s0)

				addi $sp, $sp, -4
				sw $s0, 0($sp)
				""".replace("\t\t\t","")

		stack.append(Variable(type_=type_))
		return code
		
		
	def print_stmt(self, tree):
		code = f"""\t### print stmt begin"""

		stack_size_initial = len(stack)

		actuals = self.visit(tree.children[1])
		code += actuals
		
		if len(stack) == stack_size_initial:
			return code


		sp_offset = (len(stack) - stack_size_initial - 1) * 4
		for var in stack[stack_size_initial:]:
			if var.type_.name  == 'int':
				code += f"""
					### print int	
					li $v0, 1		# syscall for print integer 
					lw $a0, {sp_offset}($sp)
					syscall
					""".replace("\t\t\t\t\t","\t")	
			
			if var.type_.name  == 'bool':
				code += f"""
					### print bool	
					lw $a0, {sp_offset}($sp)
					move $s0, $ra 	#save ra
					jal print_bool
					move $ra, $s0 	#restore ra
					""".replace("\t\t\t\t","")	

			if var.type_.name == 'double':
				code += f"""
					### print double	
					li $v0, 3		# syscall for print double 
					l.d $f12, {sp_offset}($sp)
					syscall
					""".replace("\t\t\t\t\t","\t")

			if var.type_.name == 'string':
				code += f"""
					### print string	
					li $v0, 4		# syscall for print string 
					lw $a0, {sp_offset}($sp)
					syscall
					""".replace("\t\t\t\t\t","\t")

			sp_offset -= 4

		code += f"""
				la $a0, newLineStr
				li $v0, 4	# syscall for print string
				syscall
				addi $sp, $sp, {(len(stack) - stack_size_initial ) * 4}
				### print stmt end
				""".replace("\t\t\t\t","\t")

		return code

	def actuals(self, tree):
		actuals = self.visit_children(tree)
		code = '\n'.join(actuals)
		return code

	def type(self, tree):
		type_name = tree.children[0].value
		type_ = tree.symbol_table.find_type(type_name)

		if not type_:
			raise SemanticError("Type not in scope",tree=tree)
		return type_


	def boolean_or(self, tree):
		code = ''
		code += self.visit(tree.children[0])
		var1 = stack.pop()
		code += self.visit(tree.children[1])
		var2 = stack.pop()

		if var1.type_.name != var2.type_.name:
			raise SemanticError('var1 type != var2 type in \'boolean_or\'', tree=tree)

		if var1.type_.name != 'bool':
			raise SemanticError('variables type are not bool \'boolean_or\'', tree=tree)

		code += f"""
				### boolean_or
				lw $t1, 0($sp)
				lw $t0, 4($sp)
				or $t2, $t0, $t1
				sw $t2, 4($sp) 
				addi $sp, $sp, 4
				""".replace("\t\t\t", "")

		stack.append(Variable(type_=tree.symbol_table.find_type('bool')))
		return code


	def boolean_and(self,tree):
		code = ''
		code += self.visit(tree.children[0])
		var1 = stack.pop()
		code += self.visit(tree.children[1])
		var2 = stack.pop()

		if var1.type_.name != var2.type_.name:
			raise SemanticError('var1 type != var2 type in \'boolean_and\'', tree=tree)

		if var1.type_.name != 'bool':
			raise SemanticError('variables type are not bool \'boolean_and\'', tree=tree)

		code += f"""
				### boolean_and
				lw $t1, 0($sp)
				lw $t0, 4($sp)
				and $t2, $t0, $t1
				sw $t2, 4($sp) 
				addi $sp, $sp, 4
				""".replace("\t\t\t", "")

		stack.append(Variable(type_=tree.symbol_table.find_type('bool')))
		return code



	def eq(self,tree):
		code = ''
		code += self.visit(tree.children[0])
		var1 = stack.pop()
		code += self.visit(tree.children[1])
		var2 = stack.pop()

		if var1.type_.name != var2.type_.name:
			raise SemanticError('var1 type != var2 type in \'equal\'', tree=tree)
		#TODO check for null 
		
		if var1.type_.name == 'int' or var1.type_.name == 'bool':
			# t0 operand 1
			# t1 operand 2
			code += f"""
					### equal
					lw $t1, 0($sp)
					lw $t0, 4($sp)
					seq $t2, $t0, $t1
					sw $t2, 4($sp) 
					addi $sp, $sp, 4
					""".replace("\t\t\t\t\t", "\t")
		else:
			# TODO for double and objects
			pass

		stack.append(Variable(type_=tree.symbol_table.find_type('bool')))
		return code

		
	def neq(self,tree):
		code = ''
		code += self.visit(tree.children[0])
		var1 = stack.pop()
		code += self.visit(tree.children[1])
		var2 = stack.pop()

		if var1.type_.name != var2.type_.name:
			raise SemanticError('var1 type != var2 type in \'nequal\'', tree=tree)
		#TODO check for null 
		
		if var1.type_.name == 'int' or var1.type_.name == 'bool':
			# t0 operand 1
			# t1 operand 2
			code += f"""
					### nequal
					lw $t1, 0($sp)
					lw $t0, 4($sp)
					sne $t2, $t0, $t1
					sw $t2, 4($sp) 
					addi $sp, $sp, 4
					""".replace("\t\t\t\t\t", "\t")
		else:
			# TODO for double and objects
			pass

		stack.append(Variable(type_=tree.symbol_table.find_type('bool')))
		return code

	
	def lt(self,tree):
		code = ''
		code += self.visit(tree.children[0])
		var1 = stack.pop()
		code += self.visit(tree.children[1])
		var2 = stack.pop()

		if var1.type_.name != var2.type_.name:
			raise SemanticError('var1 type != var2 type in \'lt\'', tree=tree)

		if var1.type_.name == 'int':
			# t0 operand 1
			# t1 operand 2
			code += f"""
					### lt
					lw $t1, 0($sp)
					lw $t0, 4($sp)
					slt $t2, $t0, $t1
					sw $t2, 4($sp) 
					addi $sp, $sp, 4
					""".replace("\t\t\t\t\t", "\t")
		elif var1.type_.name == 'double':
			l1 = IncLabels()
			code += f"""
					### lt
					l.d $f2, 0($sp)
					l.d $f4, 4($sp)
					li $t0 , 0
					c.lt.d $f4, $f2
					bc1t d_lt_{l1}
					li $t0 , 1
				d_lt_{l1}:
					sw $t0, 4($sp)
					addi $sp, $sp, 4
					""".replace("\t\t\t\t\t", "\t").replace("\t\t\t\t", "")
		
		else:
			raise SemanticError('types are not suitable for \'lt\'', tree=tree)

		stack.append(Variable(type_=tree.symbol_table.find_type('bool')))
		return code


	def le(self,tree):
		code = ''
		code += self.visit(tree.children[0])
		var1 = stack.pop()
		code += self.visit(tree.children[1])
		var2 = stack.pop()

		if var1.type_.name != var2.type_.name:
			raise SemanticError('var1 type != var2 type in \'le\'', tree=tree)
		
		if var1.type_.name == 'int':
			# t0 operand 1
			# t1 operand 2
			code += f"""
					### le
					lw $t1, 0($sp)
					lw $t0, 4($sp)
					sle $t2, $t0, $t1
					sw $t2, 4($sp) 
					addi $sp, $sp, 4
					""".replace("\t\t\t\t\t", "\t")
		elif var1.type_.name == 'double':
			l1 = IncLabels()
			code += f"""
					### le
					l.d $f2, 0($sp)
					l.d $f4, 4($sp)
					li $t0 , 0
					c.le.d $f4, $f2
					bc1t d_le_{l1}
					li $t0 , 1
				d_le_{l1}:
					sw $t0, 4($sp)
					addi $sp, $sp, 4
					""".replace("\t\t\t\t\t", "\t").replace("\t\t\t\t", "")
		
		else:
			raise SemanticError('types are not suitable for \'le\'', tree=tree)

		stack.append(Variable(type_=tree.symbol_table.find_type('bool')))
		return code




	def gt(self,tree):
		code = ''
		code += self.visit(tree.children[0])
		var1 = stack.pop()
		code += self.visit(tree.children[1])
		var2 = stack.pop()

		if var1.type_.name != var2.type_.name:
			raise SemanticError('var1 type != var2 type in \'gt\'', tree=tree)
		
		if var1.type_.name == 'int':
			# t0 operand 1
			# t1 operand 2
			code += f"""
					### gt
					lw $t1, 0($sp)
					lw $t0, 4($sp)
					sgt $t2, $t0, $t1
					sw $t2, 4($sp) 
					addi $sp, $sp, 4
					""".replace("\t\t\t\t\t", "\t")
		elif var1.type_.name == 'double':
			l1 = IncLabels()
			code += f"""
					### gt
					l.d $f2, 0($sp)
					l.d $f4, 4($sp)
					li $t0 , 1
					c.le.d $f4, $f2
					bc1t d_gt_{l1}
					li $t0 , 0
				d_gt_{l1}:
					sw $t0, 4($sp)
					addi $sp, $sp, 4
					""".replace("\t\t\t\t\t", "\t").replace("\t\t\t\t", "")
		
		else:
			raise SemanticError('types are not suitable for \'gt\'', tree=tree)

		stack.append(Variable(type_=tree.symbol_table.find_type('bool')))
		return code


	def ge(self,tree):
		code = ''
		code += self.visit(tree.children[0])
		var1 = stack.pop()
		code += self.visit(tree.children[1])
		var2 = stack.pop()

		if var1.type_.name != var2.type_.name:
			raise SemanticError('var1 type != var2 type in \'ge\'', tree=tree)
		
		if var1.type_.name == 'int':
			# t0 operand 1
			# t1 operand 2
			code += f"""
					### ge
					lw $t1, 0($sp)
					lw $t0, 4($sp)
					sge $t2, $t0, $t1
					sw $t2, 4($sp) 
					addi $sp, $sp, 4
					""".replace("\t\t\t\t\t", "\t")
		elif var1.type_.name == 'double':
			l1 = IncLabels()
			code += f"""
					### ge
					l.d $f2, 0($sp)
					l.d $f4, 4($sp)
					li $t0 , 1
					c.lt.d $f4, $f2
					bc1t d_ge_{l1}
					li $t0 , 0
				d_ge_{l1}:
					sw $t0, 4($sp)
					addi $sp, $sp, 4
					""".replace("\t\t\t\t\t", "\t").replace("\t\t\t\t", "")
		
		else:
			raise SemanticError('types are not suitable for \'ge\'', tree=tree)


		stack.append(Variable(type_=tree.symbol_table.find_type('bool')))
		return code





	# def boolean_expr(self, tree):
	# 	code = ''
	# 	code += self.visit(tree.children[0])
	# 	var1 = stack.pop()
	# 	code += self.visit(tree.children[2])
	# 	var2 = stack.pop()

		
	# 	operand = tree.children[1].value

	# 	if var1.type_.name != var2.type_.name:
	# 		raise SemanticError('var1 type != var2 type in \'boolean_expr\'', tree=tree)

	# 	if operand != '==' and  operand != '!=' and var1.type_.name != 'int' and var1.type_.name != 'double':
	# 		raise SemanticError('variables type are not double or int in \'boolean_expr\'', tree=tree)

		

	# 	if var1.type_.name == 'int' or var1.type_.name == 'bool':
	# 		# t0 operand 1
	# 		# t1 operand 2
	# 		compare_line = ""
	# 		if operand == '<':
	# 			compare_line ="slt $t2, $t0, $t1"
	# 		elif operand == '>':
	# 			compare_line = "sgt $t2, $t0, $t1"
	# 		elif operand == '<=':
	# 			compare_line = "sge $t2, $t1, $t0"
	# 		elif operand == '>=':
	# 			compare_line = "sge $t2, $t0, $t1"

	# 		# TODO check these for other types if needed
	# 		elif operand == '==':
	# 			compare_line = "seq $t2, $t0, $t1"
	# 		elif operand == '!=':
	# 			compare_line = "sne $t2, $t0, $t1"

	# 		code += f"""
	# 				### boolean_expr
	# 				lw $t1, 0($sp)
	# 				lw $t0, 4($sp)
	# 				{compare_line}
	# 				sw $t2, 4($sp) 
	# 				addi $sp, $sp, 4
	# 				""".replace("\t\t\t\t\t", "\t")
	# 	else:
	# 		# TODO for double
	# 		pass

	# 	stack.append(Variable(type_=tree.symbol_table.find_type('bool')))
	# 	return code
		
	
	# def logical_expr(self, tree):
	# 	code = ''
	# 	code += self.visit(tree.children[0])
	# 	var1 = stack.pop()
	# 	code += self.visit(tree.children[2])
	# 	var2 = stack.pop()


	# 	if var1.type_.name != var2.type_.name:
	# 		raise SemanticError('var1 type != var2 type in \'logical_expr\'', tree=tree)

	# 	if var1.type_.name != 'bool':
	# 		raise SemanticError('variables type are not bool in \'logical_expr\'', tree=tree)

	# 	operand = tree.children[1].value

	# 	compare_line = ""
	# 	if operand == '||':
	# 		compare_line = "or $t2, $t0, $t1"
	# 	elif operand == '&&':
	# 		compare_line = "and $t2, $t0, $t1"

	# 	code += f"""
	# 			### logical_expr
	# 			lw $t1, 0($sp)
	# 			lw $t0, 4($sp)
	# 			{compare_line}
	# 			sw $t2, 4($sp) 
	# 			#greater_equal
	# 			addi $sp, $sp, 4
	# 			""".replace("\t\t\t", "")

	# 	stack.append(Variable(type_=tree.symbol_table.find_type('bool')))
	# 	return code

	def not_expr(self, tree):
		code = ''
		code += self.visit(tree.children[1])
		var1 = stack.pop()

		if var1.type_.name != 'bool':
			raise SemanticError('variable type is not bool in \'not_expr\'', tree=tree)

		code += f"""
				### not_expr
				lw $t0, 0($sp)
				xori $t1, $t0, 1
				sw $t1, 0($sp) 
				""".replace("\t\t\t", "")

		stack.append(Variable(type_=tree.symbol_table.find_type('bool')))
		return code

	def read_line(self, tree):
		l1 = IncLabels()
		l2 = IncLabels()
		l3 = IncLabels()
		code = f"""
				### read Line
				li $v0, 9	# syscall for allocating bytes
				li $a0, 1000
				syscall		
				sub $sp, $sp, 8
				sw $v0, 0($sp)
				move $a0, $v0
				li $a1, 1000
				li $v0, 8	# syscall for read string
				syscall
				lw $a0, 0($sp)
				line_{l1}:
					lb $t0, 0($a0)
					beq $t0, 0, end_line_{l1}
					bne $t0, 10, remover_{l2}
					li $t2, 0
					sb $t2, 0($a0)
				remover_{l2}:
					bne $t0, 13, remover_{l3}
					li $t2, 0
					sb $t2, 0($a0)
				remover_{l3}:
					addi $a0, $a0, 1
					j line_{l1}
				end_line_{l1}:
					
				""".replace("\t\t\t", "")
		stack.append(Variable(type_=tree.symbol_table.find_type('string')))
		return code

	def itod(self, tree):
		code = self.visit(tree.children[1])
		var1 = stack.pop()

		if var1.type_.name != 'int':
			raise SemanticError('variable type is not integer in \'itod\'', tree=tree)

		code += f"""
					la $t0, 0($sp)
					mtc1 $t0, $f0
					cvt.d.w $f0, $f0
					s.d $f0, 0($sp)
				""".replace("\t\t\t", "")
		stack.append(Variable(type_=tree.symbol_table.find_type('double')))
		return code
	def dtoi(self, tree):
		code = self.visit(tree.children[1])
		var1 = stack.pop()

		if var1.type_.name != 'double':
			raise SemanticError('variable type is not double in \'dtoi\'', tree=tree)

		code+= f"""
				la $t0, 0($sp)
				mov $f0, $t0
				cvt.w.d $f0, $f0
				mfc1 $t0, $f0
				sw $a0, 0($sp)
				""".replace("\t\t\t", "")
		stack.append(Variable(type_=tree.symbol_table.find_type('int')))
	def itob(self,tree):
		code = self.visit(tree.children[1])
		var1 = stack.pop()

		if var1.type_.name != 'int':
			raise SemanticError('variable type is not integer in \'itob\'', tree=tree)

		code += f"""
				la $t0, 0($sp)
				li $t1, 0
				sne $t0, $t1, $t0
				sw $t0, 0($sp)
				""".replace("\t\t\t", "")
		stack.append(Variable(type_=tree.symbol_table.find_type('bool')))
		return code

	def btoi(self,tree):
		code = self.visit(tree.children[1])
		var1 = stack.pop()

		if var1.type_.name != 'bool':
			raise SemanticError('variable type is not bool in \'btoi\'', tree=tree)

		l1 = IncLabels()
		code += f"""
				btoi_{l1}:
					la $t0, 0($sp)
					beq $t0, 0, set_zero_{l1}
					addi $t0, $zero, 1
					sw $t0, 0($sp)
				set_zero_{l1}:
					mov $t0, $zero
					sw $t0, 0($sp)
				""".replace("\t\t\t", "")
		stack.append(Variable(type_=tree.symbol_table.find_type('int')))
		return code


	def if_stmt(self, tree):
		
		expr_code = self.visit(tree.children[1])
		expr_variable = stack.pop()

		statement_code = self.visit(tree.children[2])

		else_code = ''
		if len(tree.children) > 3:
			else_code = self.visit(tree.children[4])
		

		label_num = IncLabels()
		code = f"""
		### if stmt no. {label_num}
			{expr_code}
			lw $t0, 0($sp)
			bne $t0, 1, else_{label_num}

			{statement_code}
			b end_if_{label_num}

		else_{label_num}:
			{else_code}
		
		end_if_{label_num}:
		""".replace("\t\t", "")

		return code

	def while_stmt(self, tree):
		expr_code = self.visit(tree.children[1])
		expr_variable = stack.pop()

		statement_code = self.visit(tree.children[2])

		label_num = IncLabels()

		code = f"""
		### while stmt no. {label_num}
		start_while_{label_num}:
			{expr_code}
			lw $t0, 0($sp)
			bne $t0, 1, end_while_{label_num}

			{statement_code}
			b start_while_{label_num}

		end_while_{label_num}:
		""".replace("\t\t", "")

		return code




def add_initial_types(symbol_table):
	symbol_table.add_type(Type("int",4))
	symbol_table.add_type(Type("double",4))
	symbol_table.add_type(Type("bool",4))
	symbol_table.add_type(Type("string",4))
	symbol_table.add_type(Type("void",0))


def generate_tac(code):
	logger.setLevel(logging.DEBUG)
	grammer_path = Path(__file__).parent
	grammer_file = grammer_path / 'grammer.lark'
	parser = Lark.open(grammer_file, rel_to=__file__, parser="lalr", propagate_positions=True)

	try:
		tree = parser.parse(code)
		print(tree.pretty())
	except ParseError as e:
		# TODO
		print(e)
		return e

	try:
		ParentVisitor().visit_topdown(tree)
		tree.symbol_table = SymbolTable()
		add_initial_types(tree.symbol_table)
		SymbolTableVisitor().visit_topdown(tree)
		mips_code = Cgen().visit(tree)

	except SemanticError as err:
		print(err)
		# TODO check
		mips_code = """
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

	return mips_code




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
