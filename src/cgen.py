import logging
from lark import Lark, logger, __file__ as lark_file, ParseError, Tree
from lark.visitors import Interpreter
from decimal import Decimal
from pathlib import Path

from symbol_table import Function, SymbolTable, Variable, Type, SymbolTableVisitor, ParentVisitor
from utils import SemanticError


stack = []
constant_strings = []
arrays = []

# usage in break and continue
stack_of_for_and_while_labels = [] # (label_for_continue, label_for_break) 

# usage in return
stack_of_functions = [] 

def IncLabels():
	Cgen.labels+=1
	return Cgen.labels



class Cgen(Interpreter):
	labels = 0


	def program(self, tree):
		
		code = "\n.text"

		code += '\n'.join(self.visit_children(tree))
	
		code += """

		### Function: Print_bool(a0: boolean_value)

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


		### Function: String_length(a0: string_addr) $v0: length without zero terminated char

		string_length: 
			li $v0, 0
			move $t1, $a0
		
		string_length_begin:
			lb $t2, 0($t1)
			beq $t2, $zero, string_length_end
			addi $v0, $v0, 1
			addi $t1, $t1, 1
			b string_length_begin

		string_length_end:
			jr $ra

		""".replace("\t\t","")

		code_data_seg = """
		.data

		falseStr: .asciiz "false"
		trueStr: .asciiz "true"
		newLineStr: .asciiz "\\n"
		""".replace("\t\t","")

		for i, s in enumerate(constant_strings):
			code_data_seg += f"constantStr_{i}: .asciiz \"{s}\"\n"
		
		code_data_seg += "\n"

		for i, a in enumerate(arrays):
			code_data_seg += f"array_{i}: .word \"{a}\"\n"

		code_data_seg += "\n"

		return code_data_seg + code
	
	def statement_block(self, tree):
		children_code = self.visit_children(tree)
		children_code = [c if c else '' for c in children_code]
		code = '\n'.join(children_code)

		return code
	

	def	decl(self, tree):

		code = ''
		for decl in tree.children:
			if decl.data == 'function_decl':
				code += self.visit(decl)
		
		return code
	
	def function_decl(self, tree):

		# stack frame
		#			------------------- 		
		# 			| 	argument 1    |			\
		# 			| 		...		  |				=> caller
		# 			| 	argument n    |			/
		#			------------------- 
		#  $fp -> 	| 	  old fp	  |			\
		#  $fp - 4 	| 	  old ra	  |			\
		#  		 	| saved registers |			\
		#  			| 		...		  |			 \
		#			-------------------				=> callee
		# 			| 	local vars	  |			 /
		# 			| 		...		  |			/
		#  $sp ->	| 		...		  |			
		#  $sp - 4	-------------------

		# access arguments with $fp + 4, $fp + 8, ...

		# return value in v0
		

		# type
		
		type_ = Type("void")
		if isinstance(tree.children[0], Tree):
			type_ = self.visit(tree.children[0])

		# name
		func_name = tree.children[1].value
		function = tree.symbol_table.find_func(func_name, tree=tree)

		# formals
		self.visit(tree.children[2])

		formals_code = ""
		
		index = 4
		for arg in function.formals[::-1]:
			formals_code += f"""
			lw $t0, {index}($fp)
			sw $t0, {arg.address}($gp)
			""".replace("\t\t\t", "\t")
			index += 4

		# body
		stack_of_functions.append(function)

		statement_block = self.visit(tree.children[3])		
		
		stack_of_functions.pop()

		code = f"""
		### Function

		{function.label}:
			# func store registers

			sw $fp, -4($sp)
			addi $fp, $sp, -4	# new frame pointer

			sw $ra, -4($fp)
			sw $s0, -8($fp)
			sw $s1, -12($fp)
			sw $s2, -16($fp)
			sw $s3, -20($fp)
			sw $s4, -24($fp)
			sw $s5, -28($fp)
			sw $s6, -32($fp)
			sw $s7, -36($fp)

			addi $sp, $sp, -36	# update stack pointer

			# func formals
			{formals_code}

			# func statement
			{statement_block}
			
		{function.label}_end:
			# func load registers

			lw $ra, -4($fp)
			lw $s0, -8($fp)
			lw $s1, -12($fp)
			lw $s2, -16($fp)
			lw $s3, -20($fp)
			lw $s4, -24($fp)
			lw $s5, -28($fp)
			lw $s6, -32($fp)
			lw $s7, -36($fp)

			addi $sp, $fp, 4  # update stack pointer to old value

			lw $fp, 0($fp)	 # old frame pointer

			jr $ra
		""".replace("\t\t", "")

		return code
	
	def call(self, tree):
		# TODO add member function calls

		function_name = tree.children[0].value
		function = tree.symbol_table.find_func(function_name, tree=tree)


		stack_size_initial = len(stack)
		actuals_code = self.visit(tree.children[1])
		arguments_number = len(stack) - stack_size_initial
		
		if arguments_number != len(function.formals):
			raise SemanticError(f"function {function_name} arguments number are not matched", tree=tree)
		

		i = arguments_number - 1
		while len(stack) > stack_size_initial:
			formal = function.formals[i]
			arg = stack.pop()
			if arg.type_.name != formal.type_.name:
				raise SemanticError(f"function {function_name} arguments not matched with formals", tree=tree)
			i -= 1
		
		code = f"""
			{actuals_code}
			jal	{function.label}
		
			addi $sp, $sp, {arguments_number * 4}
		""".replace("\t\t\t", "\t")

		# return type != void
		# return value in v0

		if function.return_type:
			code += f"""
			sw $v0, -4($sp)
			addi $sp, $sp, -4
			"""	
		
		stack.append(Variable(type_=function.return_type))
		
		return code


	def return_stmt(self, tree):
		if len(stack_of_functions) == 0:
			raise SemanticError("return can only be used in function", tree=tree)

		function = stack_of_functions[-1]

		code = '\t# return\n'
		variable = Variable(type_=Type("void"))

		if len(tree.children) > 1:
			code += self.visit(tree.children[1])
			variable = stack.pop()

			# store return value in v0
			code += f"""
			lw $v0, 0($sp)
			addi $sp, $sp, 4

			""".replace("\t\t\t", "\t")
		
		# TODO maybe array need extra care 
		
		print(variable.type_, "@$@#$@#$", function.return_type)
		if variable.type_.name != function.return_type.name:
			raise SemanticError("return type does not match function declaration", tree=tree)			

		code += f"""
		j {function.label}_end
		""".replace("\t\t", "")
		
		return code



	def variable(self, tree):
		type_ = self.visit(tree.children[0])
		var_name = tree.children[1].value		
		variable = tree.symbol_table.find_var(var_name, tree=tree)

		# old type doesnt have size so change it to Type (TODO maybe this should change)
		variable.type_ = type_
	
		return ""	

	def expr_assign(self, tree):
		global stack

		code = ''
		
		self.visit(tree.children[0])
		lvalue_var = stack.pop()

		code += self.visit(tree.children[1])
		expr_var = stack.pop()
		
		if lvalue_var.type_.name != expr_var.type_.name:
			raise SemanticError(f"lvalue type '{lvalue_var.type_.name}' != expr type '{expr_var.type_.name}' in 'expr_assign'", tree=tree)
		
		if lvalue_var.type_.name == 'int' or\
			 lvalue_var.type_.name == 'bool':
			code += f"""
				### store
				lw $t0, 0($sp)
				addi $sp, $sp, 4
				sw $t0, {lvalue_var.address}($gp) 	
				""".replace("\t\t\t\t","\t")

		elif lvalue_var.type_.name == 'double':
			code += f"""
				### store
				l.s $f2, 0($sp)
				addi $sp, $sp, 4
				s.s $f2, {lvalue_var.address}($gp) 	
				""".replace("\t\t\t\t","\t")

		elif lvalue_var.type_.name == 'string':
			code += f"""
				### store
				lw $t0, 0($sp)
				addi $sp, $sp, 4
				sw $t0, {lvalue_var.address}($gp) 	
				""".replace("\t\t\t\t","\t")
			
			lvalue_var.size = expr_var.size

		# assume assignment expression push a true in stack
		code += f"""
			li $t0, 1
			sw $t0, -4($sp) 
			addi $sp, $sp, -4
		"""
		stack.append(Variable(type_=tree.symbol_table.find_type('bool', tree=tree)))

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
				l.s $f2, 0($sp)
				l.s $f4, 4($sp)
				add.s $f6, $f4, $f2
				s.s $f6, 4($sp) 
				addi $sp, $sp, 4
				""".replace("\t\t\t\t", "\t")
		
		elif var1.type_.name == "string":
			label_number = IncLabels()
			code += f"""
				### add string
				lw $s2, 0($sp)
				
				move $a0, $s2
				move $s0, $ra 	#save ra
				jal string_length
				move $ra, $s0 	#restore ra

				move $s4, $v0	# s4: length of operand 2

				lw $s1, 4($sp)

				move $a0, $s1
				move $s0, $ra 	#save ra
				jal string_length
				move $ra, $s0 	#restore ra

				move $s3, $v0	# s3: length of operand 1

				add $t0, $s3, $s4
				addi $t0, $t0, 1	# t0: length(op1) + length(op2) + 1(for null termination)

				li $v0, 9		# syscall for allocate byte
				move $a0, $t0
				syscall

				move $s0, $v0		# s0: address of new string

			 	sw $s0, 4($sp) 
				addi $sp, $sp, 4 

			add_str_op1_{label_number}:
				lb $t1, 0($s1)
				beq $t1, $zero, add_str_op2_{label_number} 
				sb $t1, 0($s0)
				addi $s1, $s1, 1
				addi $s0, $s0, 1
				b add_str_op1_{label_number}

			add_str_op2_{label_number}:
				lb $t1, 0($s2)
				sb $t1, 0($s0)
				beq $t1, $zero, add_str_end_{label_number} 
				addi $s2, $s2, 1
				addi $s0, $s0, 1
				b add_str_op2_{label_number}
			
			add_str_end_{label_number}:

				""".replace("\t\t\t","")

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
				l.s $f2, 0($sp)
				l.s $f4, 4($sp)
				sub.s $f6, $f4, $f2
				s.s $f6, 4($sp) 
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
				l.s $f2, 0($sp)
				l.s $f4, 4($sp)
				mul.s $f6, $f4, $f2
				s.s $f6, 4($sp) 
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
				l.s $f2, 0($sp)
				l.s $f4, 4($sp)
				div.s $f6, $f4, $f2
				s.s $f6, 4($sp) 
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
				l.s $f2, 0($sp)
				neg.s $f2, $f2
				s.s $f2, 0($sp)
				""".replace("\t\t\t\t", "\t")
		else:
			raise SemanticError('types are not suitable for \'neg\'', tree=tree)

		stack.append(Variable(type_=var.type_))
		return code


	def ident(self, tree):
		var_name = tree.children[0].value
		variable = tree.symbol_table.find_var(var_name, tree=tree)
		
		stack.append(variable)

		if variable.type_.name == "double": # TODO do we need this aslan?
			code = f"""
					### ident
					l.s $f2, {variable.address}($gp)
					addi $sp, $sp, -4
					s.s $f2, 0($sp)
					""".replace("\t\t\t\t", "")
		else:
			code = f"""
					### ident
					lw $t0, {variable.address}($gp)
					addi $sp, $sp, -4
					sw $t0, 0($sp)
					""".replace("\t\t\t\t", "")
		
		return code



	# TODO do we need null?

	def constant(self, tree):
		constant_type = tree.children[0].type
		value = "????"
		type_ = "????"

		code = ''
		if constant_type == 'INTCONSTANT':
			value = tree.children[0].value.lower()
			type_ = tree.symbol_table.find_type('int', tree=tree)
			
			value = value.lstrip('0')

			if value == '':
				value = '0'
			
			code = f"""
				### constant int
				li $t0, {value}
				addi $sp, $sp, -4
				sw $t0, 0($sp)
				""".replace("\t\t\t","")
			

		if constant_type == 'DOUBLECONSTANT':
			value = tree.children[0].value.lower()
			type_ = tree.symbol_table.find_type('double', tree=tree)

			value = value.lstrip('0')

			if value[0] == '.':
				value = '0' + value

			# handle 3.
			if value[-1] == '.':
				value = value + '0'

			# handle 3.E2
			if '.e' in value:
				value = value.replace('.e', '.0e')

			code = f"""
				### constant double
				li.s $f2, {value}
				addi $sp, $sp, -4
				s.s $f2, 0($sp)
				""".replace("\t\t\t","")


		if constant_type == 'BOOLCONSTANT':
			value = 1 if tree.children[0].value == 'true' else 0
			type_ = tree.symbol_table.find_type('bool', tree=tree)
			code = f"""
				### constant bool
				li $t0, {value}
				addi $sp, $sp, -4
				sw $t0, 0($sp)
				""".replace("\t\t\t","")


		if constant_type == 'STRINGCONSTANT':
			value = tree.children[0].value[1:-1]
			type_ = tree.symbol_table.find_type('string', tree=tree)

			constant_string_label = len(constant_strings)
			constant_strings.append(value)

			size = len(value) + 1
			label_number = IncLabels()

			code = f"""
				### constant string
				li $v0, 9		# syscall for allocate byte
				li $a0, {size}
				syscall

				move $s0, $v0		# s0: address of string

				addi $sp, $sp, -4
				sw $s0, 0($sp)

				la $s1, constantStr_{constant_string_label}
				li $t1, 0

			constant_str_{label_number}:
				lb $t1, 0($s1)
				sb $t1, 0($s0)
				beq $t1, $zero, constant_str_end_{label_number} 
				addi $s1, $s1, 1
				addi $s0, $s0, 1
				b constant_str_{label_number}

			constant_str_end_{label_number}:

				""".replace("\t\t\t","")
		
		if constant_type == 'NULL':
			# TODO ??
			type_ = Type('null')

		stack.append(Variable(type_=type_))
		return code
		
		
	def print_stmt(self, tree):
		code = f"""\t\t\t### print stmt begin\n"""

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
					""".replace("\t\t\t\t","")	
			
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
					li $v0, 2		# syscall for print double 
					l.s $f12, {sp_offset}($sp)
					syscall
					""".replace("\t\t\t\t","")

			if var.type_.name == 'string':
				code += f"""
					### print string	
					li $v0, 4		# syscall for print string 
					lw $a0, {sp_offset}($sp)
					syscall
					""".replace("\t\t\t\t","")

			sp_offset -= 4

		code += f"""
				la $a0, newLineStr
				li $v0, 4	# syscall for print string
				syscall
				addi $sp, $sp, {(len(stack) - stack_size_initial ) * 4}
				### print stmt end
				""".replace("\t\t\t\t","\t")

		while len(stack) > stack_size_initial:
			stack.pop()

		return code

	def actuals(self, tree):
		actuals = self.visit_children(tree)
		code = '\n'.join(actuals)
		return code

	# type return Type
	def type(self, tree):
		type_name = tree.children[0].value
		type_ = tree.symbol_table.find_type(type_name, tree=tree)

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

		stack.append(Variable(type_=tree.symbol_table.find_type('bool', tree=tree)))
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

		stack.append(Variable(type_=tree.symbol_table.find_type('bool', tree=tree)))
		return code



	def equal(self,tree):
		code = ''
		code += self.visit(tree.children[0])
		var1 = stack.pop()
		code += self.visit(tree.children[1])
		var2 = stack.pop()

		if var1.type_.name != var2.type_.name:
			raise SemanticError('var1 type != var2 type in \'equal\'', tree=tree)

		#TODO check for null and objects
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
					""".replace("\t\t\t\t", "")
		elif var1.type_.name == 'double':
			# f4 operand 1
			# f2 operand 2
			l1 = IncLabels()
			code += f"""
					### equal double
					l.s $f2, 0($sp)
					l.s $f4, 4($sp)
					li $t0 , 0
					c.eq.s $f4, $f2
					bc1f d_eq_{l1}
					li $t0 , 1
				d_eq_{l1}:
					sw $t0, 4($sp)
					addi $sp, $sp, 4
					""".replace("\t\t\t\t", "")

		elif var1.type_.name == 'string':
			# s0 str1 address
			# s1 str2 address
			labelcnt = IncLabels()
			code += f"""
					### equal string
					lw $s1, 0($sp)
					lw $s0, 4($sp)
					
				cmploop_{labelcnt}:
					lb $t2,0($s0)
					lb $t3,0($s1)
					bne $t2,$t3,cmpne_{labelcnt}
					
					beq $t2,$zero,cmpeq_{labelcnt}
					beq $t3,$zero,cmpeq_{labelcnt}
					
					addi $s0,$s0,1
					addi $s1,$s1,1
					
					j cmploop_{labelcnt}
					
				cmpne_{labelcnt}:
					li $t0,0
					sw $t0, 4($sp)
					addi $sp, $sp, 4
					j end_{labelcnt}
					
				cmpeq_{labelcnt}:
					li $t0,1
					sw $t0, 4($sp)
					addi $sp, $sp, 4
					j end_{labelcnt}
					
				end_{labelcnt}:

				""".replace("\t\t\t\t","")
				
		else:
			raise SemanticError('types are not suitable for \'eq\'', tree=tree)

		stack.append(Variable(type_=tree.symbol_table.find_type('bool', tree=tree)))
		return code



	def not_equal(self,tree):
		code = ''
		code += self.visit(tree.children[0])
		var1 = stack.pop()
		code += self.visit(tree.children[1])
		var2 = stack.pop()

		if var1.type_.name != var2.type_.name:
			raise SemanticError('var1 type != var2 type in \'nequal\'', tree=tree)
		
		#TODO check for null and other objects
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
					""".replace("\t\t\t\t", "")
		elif var1.type_.name == 'double':
			# f4 operand 1
			# f2 operand 2
			l1 = IncLabels()
			code += f"""
					### neq
					l.s $f2, 0($sp)
					l.s $f4, 4($sp)
					li $t0 , 1
					c.eq.s $f4, $f2
					bc1f d_neq_{l1}
					li $t0 , 0
				d_neq_{l1}:
					sw $t0, 4($sp)
					addi $sp, $sp, 4
					""".replace("\t\t\t\t", "")
		elif var1.type_.name == 'string':
			# s0 str1 address
			# s1 str2 address
			labelcnt = IncLabels()
			code += f"""
					### not_equal string
					lw $s1, 0($sp)
					lw $s0, 4($sp)
					
				cmploop_{labelcnt}:
					lb $t2,0($s0)
					lb $t3,0($s1)
					bne $t2,$t3,cmpne_{labelcnt}
					
					beq $t2,$zero,cmpeq_{labelcnt}
					beq $t3,$zero,cmpeq_{labelcnt}
					
					addi $s0,$s0,1
					addi $s1,$s1,1
					
					j cmploop_{labelcnt}
					
				cmpne_{labelcnt}:
					li $t0,1
					sw $t0, 4($sp)
					addi $sp, $sp, 4
					j end_{labelcnt}
					
				cmpeq_{labelcnt}:
					li $t0,0
					sw $t0, 4($sp)
					addi $sp, $sp, 4
					j end_{labelcnt}
					
				end_{labelcnt}:

				""".replace("\t\t\t\t","")
		else:
			raise SemanticError('types are not suitable for \'neq\'', tree=tree)

		stack.append(Variable(type_=tree.symbol_table.find_type('bool', tree=tree)))
		return code

	
	def less_than(self,tree):
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
					""".replace("\t\t\t\t", "")
		elif var1.type_.name == 'double':
			# f4 operand 1
			# f2 operand 2
			l1 = IncLabels()
			code += f"""
					### lt
					l.s $f2, 0($sp)
					l.s $f4, 4($sp)
					li $t0 , 0
					c.lt.s $f4, $f2
					bc1f d_lt_{l1}
					li $t0 , 1
				d_lt_{l1}:
					sw $t0, 4($sp)
					addi $sp, $sp, 4
					""".replace("\t\t\t\t", "")
		
		else:
			raise SemanticError('types are not suitable for \'lt\'', tree=tree)

		stack.append(Variable(type_=tree.symbol_table.find_type('bool', tree=tree)))
		return code


	def less_equal(self,tree):
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
					""".replace("\t\t\t\t", "")
		elif var1.type_.name == 'double':
			# f4 operand 1
			# f2 operand 2
			l1 = IncLabels()
			code += f"""
					### le
					l.s $f2, 0($sp)
					l.s $f4, 4($sp)
					li $t0 , 0
					c.le.s $f4, $f2
					bc1f d_le_{l1}
					li $t0 , 1
				d_le_{l1}:
					sw $t0, 4($sp)
					addi $sp, $sp, 4
					""".replace("\t\t\t\t", "")
		
		else:
			raise SemanticError('types are not suitable for \'le\'', tree=tree)

		stack.append(Variable(type_=tree.symbol_table.find_type('bool', tree=tree)))
		return code




	def greater_than(self,tree):
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
					""".replace("\t\t\t\t", "")
		elif var1.type_.name == 'double':
			l1 = IncLabels()
			code += f"""
					### gt
					l.s $f2, 0($sp)
					l.s $f4, 4($sp)
					li $t0 , 0
					c.lt.s $f2, $f4
					bc1f d_gt_{l1}
					li $t0 , 1
				d_gt_{l1}:
					sw $t0, 4($sp)
					addi $sp, $sp, 4
					""".replace("\t\t\t\t", "")
		
		else:
			raise SemanticError('types are not suitable for \'gt\'', tree=tree)

		stack.append(Variable(type_=tree.symbol_table.find_type('bool', tree=tree)))
		return code


	def greater_equal(self,tree):
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
					""".replace("\t\t\t\t", "")
		elif var1.type_.name == 'double':
			l1 = IncLabels()
			code += f"""
					### ge
					l.s $f2, 0($sp)
					l.s $f4, 4($sp)
					li $t0 , 0
					c.le.s $f2, $f4
					bc1f d_ge_{l1}
					li $t0 , 1
				d_ge_{l1}:
					sw $t0, 4($sp)
					addi $sp, $sp, 4
					""".replace("\t\t\t\t", "")
		
		else:
			raise SemanticError('types are not suitable for \'ge\'', tree=tree)


		stack.append(Variable(type_=tree.symbol_table.find_type('bool', tree=tree)))
		return code


	def not_expr(self, tree):
		code = ''
		code += self.visit(tree.children[0])
		var1 = stack.pop()

		if var1.type_.name != 'bool':
			raise SemanticError('variable type is not bool in \'not_expr\'', tree=tree)

		code += f"""
				### not_expr
				lw $t0, 0($sp)
				xori $t1, $t0, 1
				sw $t1, 0($sp) 
				""".replace("\t\t\t", "")

		stack.append(Variable(type_=tree.symbol_table.find_type('bool', tree=tree)))
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
				sub $sp, $sp, 4
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
		stack.append(Variable(type_=tree.symbol_table.find_type('string', tree=tree)))
		return code

	def read_integer(self, tree):
		code = f"""
				li $v0, 5
				syscall
				move $t0, $v0
				addi $sp, $sp, -4
				sw $t0, 0($sp)
				""".replace("\t\t\t", "")
		stack.append(Variable(type_=tree.symbol_table.find_type('int', tree=tree)))
		return code


	def itod(self, tree):
		code = self.visit(tree.children[1])
		var1 = stack.pop()

		if var1.type_.name != 'int':
			raise SemanticError('variable type is not integer in \'itod\'', tree=tree)

		code += f"""
					l.s $f0, 0($sp)
					cvt.s.w $f2, $f0
					s.s $f2, 0($sp)
				""".replace("\t\t\t", "")
		stack.append(Variable(type_=tree.symbol_table.find_type('double', tree=tree)))
		return code
	

	def dtoi(self, tree):
		code = self.visit(tree.children[1])
		var1 = stack.pop()

		if var1.type_.name != 'double':
			raise SemanticError('variable type is not double in \'dtoi\'', tree=tree)
		l1 = IncLabels()
		code+= f"""
				li.s $f4, -0.5
				li.s $f6, 0.0
				l.s $f0, 0($sp)
				c.lt.s $f0, $f6
				bc1t dtoi_{l1}
				li.s $f4, 0.5
			dtoi_{l1}:
				add.s $f0, $f0, $f4
				cvt.w.s $f2, $f0
				s.s $f2, 0($sp)
				""".replace("\t\t\t", "")
		stack.append(Variable(type_=tree.symbol_table.find_type('int', tree=tree)))
		return code


	def itob(self,tree):
		code = self.visit(tree.children[1])
		var1 = stack.pop()

		if var1.type_.name != 'int':
			raise SemanticError('variable type is not integer in \'itob\'', tree=tree)

		code += f"""
				lw $t0, 0($sp)
				sne $t0, $zero, $t0
				sw $t0, 0($sp)
				""".replace("\t\t\t", "")
		stack.append(Variable(type_=tree.symbol_table.find_type('bool', tree=tree)))
		return code


	def btoi(self,tree):
		code = self.visit(tree.children[1])
		var1 = stack.pop()

		if var1.type_.name != 'bool':
			raise SemanticError('variable type is not bool in \'btoi\'', tree=tree)

		# no need to do anything!

		stack.append(Variable(type_=tree.symbol_table.find_type('int', tree=tree)))
		return code

	def expr_expr(self, tree):
		code = self.visit(tree.children[1])
		index = stack.pop()
		var_name = tree.children[0].value
		variable = tree.symbol_table.find_var(var_name, tree=tree)

		if index.type_.name != 'int':
			raise SemanticError('index type is not int', tree = tree)
		#TODO how to know array size
		#TODO how to know array type size
		l1 = IncLabels()
		code += f"""
				li $t0, {variable.contain} 
				li $t1, 0($sp)
				addi $t1, $t1, -1
				la $t2, {variable.address}
			s_iter_array_{l1}:
				beq $t1, $zero, f_iter_array{l1}
				addi $t2, $t2, {-1*variable.size} 
				addi $t1, $t1, -1
			f_iter_array_{l1}:
				lw $t2, 0($t2)
				sw $t2, 0($sp)	
				""".replace("\t\t\t", "")
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

		label_num = IncLabels()

		stack_of_for_and_while_labels.append((f"start_while_{label_num}", f"end_while_{label_num}"))

		statement_code = self.visit(tree.children[2])

		stack_of_for_and_while_labels.pop()
		
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

	def for_stmt(self, tree):
		# for types: (number is child number)
		#	for (2;4;6) 8
		#	for (2;4;) 7
		#	for (;3;5) 7
		# 	for (;3;) 6

		childs = []
		for subtree in tree.children:
			if isinstance(subtree, Tree):
				childs.append(subtree.data)
			else:
				childs.append(subtree.value)
		
		expr1_num = None
		expr2_num = None
		expr3_num = None
		body_num = None

		# type 1
		if len(childs) == 9:
			expr1_num = 2
			expr2_num = 4
			expr3_num = 6
			body_num = 8

		# type 2
		elif len(childs) == 8 and childs[3] == ';':
			expr1_num = 2
			expr2_num = 4
			body_num = 7

		# type 3
		elif len(childs) == 8 and childs[2] == ';':
			expr2_num = 3
			expr3_num = 5
			body_num = 7

		# type 4
		elif len(childs) == 7:
			expr2_num = 3
			body_num = 6

		code_expr1 = ''
		code_expr2 = ''
		code_expr3 = ''
		code_body = ''
		
		label_num = IncLabels()

		stack_of_for_and_while_labels.append((f"continue_for_{label_num}", f"end_for_{label_num}"))

		# expr
		if expr1_num:
			code_expr1 = self.visit(tree.children[expr1_num])
			expr1_var = stack.pop()
		
		code_expr2 = self.visit(tree.children[expr2_num])
		expr2_var = stack.pop()
			
		if expr3_num:
			code_expr3 = self.visit(tree.children[expr3_num])
			expr3_var = stack.pop()
			
		# body
		code_body = self.visit(tree.children[body_num])

		stack_of_for_and_while_labels.pop()

		code = f"""
		### for stmt no. {label_num}
		{code_expr1}
		start_for_{label_num}:
			{code_expr2}
			
			lw $t0, 0($sp)
			beq $t0, $zero, end_for_{label_num}

			{code_body}
		
		continue_for_{label_num}:
			{code_expr3}

			b start_for_{label_num}

		end_for_{label_num}:
		""".replace("\t\t", "")

		return code

	
	def break_stmt(self, tree):
		if len(stack_of_for_and_while_labels) == 0:
			raise SemanticError("break can only be used in for/while", tree=tree)

		labels = stack_of_for_and_while_labels[-1]

		code = f"""
		# break
		j {labels[1]}
		""".replace("\t\t", "")

		return code

	def continue_stmt(self, tree):
		if len(stack_of_for_and_while_labels) == 0:
			raise SemanticError("continue can only be used in for/while", tree=tree)

		labels = stack_of_for_and_while_labels[-1]

		code = f"""
		# continue
		j {labels[0]}
		""".replace("\t\t", "")
		
		return code


	def new_array(self, tree):
		code = self.visit(tree.children[0])
		size = int(stack.pop())

		mem_type_name = tree.children[1].value

		mem_type = tree.symbol_table.find_type(Type(mem_type_name))

		type_ = Type("array",arr_type = mem_type)

		if size < 0 or type(size) != "int":
			raise SemanticError("size of array should be a positive integer", tree=tree) #TODO 

		code += f"""
				### array

				lw $t0, 0($sp)

				la $a0 , $t0
				li $v0 , 51
				syscall

				bneq $a1,  0, array_size_err_

				ble $t0, 0 , array_size_err_

				li $v0, 9		# syscall for allocate byte
				li $a0, {(size + 1) * 4}
				syscall

				move $s0, $v0		# s0: address of array

				sw {size}, 0($s0)

				addi $sp, $sp, -4
				sw $s0, 0($sp)

			array_size_err_: 
				la $a0 , errorMsg
				li $v0 , 4
				syscall
				
				""".replace("\t\t\t","")
		# TODO
		
		stack.append(Variable(type_=type_))
		return code





def add_initial_types(symbol_table):
	symbol_table.add_type(Type("int",4))
	symbol_table.add_type(Type("double",4))
	symbol_table.add_type(Type("bool",4))
	symbol_table.add_type(Type("string",4))
	symbol_table.add_type(Type("void",0))
	symbol_table.add_type(Type("array",4))


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
		print("Parent visitor ended")
		tree.symbol_table = SymbolTable()
		add_initial_types(tree.symbol_table)
		SymbolTableVisitor().visit_topdown(tree)
		print("SymbolTable visitor ended")
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
