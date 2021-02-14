from utils import SemanticError
from lark.visitors import  Interpreter, Visitor_Recursive, Visitor
from lark import Tree


class Type():
	def __init__(self, name, size=None, arr_type=None, class_ref=None):
		self.name = name
		self.size = size
		self.arr_type = arr_type
		self.class_ref = class_ref

	def __str__(self) -> str:
		return f"<T-{self.name}-{self.size}>"


class Variable():
	def __init__(self, name= None, type_:Type = None, address = None, size = 0):
		self.name = name
		self.type_ = type_
		self.address = address
		self.size = size



	def __str__(self) -> str:
		return f"<V-{self.name}-{self.type_}-{self.address}-{self.size}>"
	

class Function():
	def __init__(self, name, formals=[], return_type:Type = None, prefix_label = ''):
		self.name = name
		self.return_type = return_type
		self.formals = formals	# array: variable (order is important)
		self.label = name
		self.change_name(name, prefix_label)
		
	def change_name(self, name, prefix_label=''):
		if name != "main":
			self.label = prefix_label + "func_" + name
		else:
			self.label = prefix_label + name


	def __str__(self) -> str:
		return f"<F-{self.name}-{self.return_type}-{[a.__str__() for a in self.formals]}>"
	

class Class():
	def __init__(self, name, address, member_data= {}, member_functions={}):
		self.name = name
		self.address = address
		self.member_data = {}
		self.member_functions = {}
		self.fields = {}
		self.set_fields(member_data, member_functions)
	
	def set_fields(self, member_data, member_functions):
		self.member_data = member_data
		self.member_functions = member_functions
		
		if member_data.keys() & member_functions.keys():
			raise SemanticError(f"class '{self.name}' members must have distinct names")
		
		self.fields = {**member_data, **member_functions}


	def __str__(self) -> str:
		return f"<C: {self.name} \
			\n\tdata: {[v for v in self.member_data]}\
			\n\tmethods: {[v for v in self.member_functions]}>"
			# \n\tdata: {[v.__str__() for v in self.member_data.values()]}\
			# \n\tmethods: {[v.__str__() for v in self.member_functions.values()]}>"


class_stack = []

class SymbolTable():
	symbol_tables = []

	def __init__(self, parent=None):
		# self.classes = {}		# dict {name: Class}
		self.variables = {}     # dict {name: Variable}
		self.functions = {}     # dict {name: Function}
		self.types = {}			# dict {name: Type}
		self.parent = parent
		SymbolTable.symbol_tables.append(self)


	# def find_class(self, name, tree=None, error=True):
	# 	if name in self.classes:
	# 		return self.classes[name]
	# 	if self.parent:
	# 		return self.parent.find_classes(name, tree, error)
	# 	if error:
	# 		raise SemanticError(f'Class {name} not found in this scope', tree=tree)
	# 	return None


	def find_var(self, name, tree=None, error=True):
		if name in self.variables:
			return self.variables[name]
		if self.parent:
			return self.parent.find_var(name, tree, error)

		if error:
			raise SemanticError(f'Variable {name} not found in this scope', tree=tree)
		return None

	def find_func(self, name, tree=None, error=True):
		if name in self.functions:
			return self.functions[name]
		if self.parent:
			return self.parent.find_func(name, tree, error)

		if error:
			raise SemanticError(f'Function {name} not found in this scope', tree=tree)
		return None

	def find_type(self, name, tree=None, error=True):
		if name in self.types:
			return self.types[name]
		if self.parent:
			return self.parent.find_type(name, tree, error)

		if error:
			raise SemanticError(f'Type {name} not found in this scope', tree=tree)
		return None


	def add_var(self, var:Variable, tree=None):
		if self.find_var(var.name, error=False):
			raise SemanticError('Variable already exist in scope', tree=tree)
		
		self.variables[var.name] = var

	def add_func(self, func:Function, tree=None):
		if self.find_func(func.name, error=False):
			raise SemanticError('Function already exist in scope', tree=tree)

		self.functions[func.name] = func

	def add_type(self, type_:Type, tree=None):
		if self.find_type(type_.name, error=False):
			raise SemanticError('Type already  exist in scope', tree=tree)

		self.types[type_.name] = type_

	
	# # TODO do we need this?
	# def add_class(self, class_:Class, tree=None):
	# 	if self.find_var(class_.name, error=False):
	# 		raise SemanticError('Class already exist in scope', tree=tree)
		
	# 	self.classes[class_.name] = class_


	def get_index(self):
		return SymbolTable.symbol_tables.index(self)

	def __str__(self) -> str:
		return f"SYMBOLYABLE: {self.get_index()} \
			 PARENT: {self.parent.get_index() if self.parent else -1}\
				 \n\tVARIABLES: {[v.__str__() for v in self.variables.values()]}\
				 \n\tFUNCTIONS: {[f.__str__() for f in self.functions.values()]}"



class ParentVisitor(Visitor):
	def __default__(self, tree):
		for subtree in tree.children:
			if isinstance(subtree, Tree):
				assert not hasattr(subtree, 'parent')
				subtree.parent = tree




### stack contains last type:Type visited, remember to pop from stack
# also remember to push into stack :)
stack = [] 

def IncDataPointer(size):
	cur = SymbolTableVisitor.data_pointer
	SymbolTableVisitor.data_pointer += size
	return cur

class SymbolTableVisitor(Interpreter):
	data_pointer = 0
	"""
	Each Node set it's children SymbolTables. 
	If defining a method make sure to set all children symbol tables
	and visit children. default gives every child (non token) parent
	symbol table
	"""


	def __default__(self, tree):
		for subtree in tree.children:
			if isinstance(subtree, Tree):
				subtree.symbol_table = tree.symbol_table
		
		self.visit_children(tree)
	

	def type(self, tree):
		type_ = tree.children[0].value
		stack.append(Type(type_))

	def array_type(self, tree):
		# TODO
		mem_type = tree.children[0].value
		stack.append(Type("array",arr_type = mem_type))


	def function_decl(self, tree):
		# stack frame
		#			------------------- 		
		# 			| 	argument n    |			\
		# 			| 		...		  |				=> caller
		# 			| 	argument 1    |			/
		#			------------------- 
		#  $fp -> 	| saved registers |			\
		#  $fp - 4	| 		...		  |			 \
		#			-------------------				=> callee
		# 			| 	local vars	  |			 /
		# 			| 		...		  |			/
		#  $sp ->	| 		...		  |			
		#  $sp - 4	-------------------

		# access arguments with $fp + 4, $fp + 8, ...


		# check if function is a member function
		function_class = None
		if len(class_stack) > 0:
			function_class = class_stack[-1]


		# type 
		type_ = Type("void") # void

		if isinstance(tree.children[0], Tree):
			tree.children[0].symbol_table = tree.symbol_table
			self.visit(tree.children[0])
			type_ = stack.pop()

		func_name = tree.children[1].value

		# set formal scope and visit formals
		formals_symbol_table = SymbolTable(parent=tree.symbol_table)
		tree.children[2].symbol_table = formals_symbol_table

		# TODO 
		# not sure what to do here and what types do formals need to be 
		# now they are list of types:Type (but without size)
		sp_initial = len(stack)
		self.visit(tree.children[2])
		formals = []
		
		while len(stack) > sp_initial:
			f = stack.pop()
			formals.append(f)
		
		formals = formals[::-1]

		# Add this to formals and symbol table
		if function_class:
			this = Variable(
				name="this",
				type_=Type(
					name=function_class.name,
					class_ref=function_class
				),
				address= IncDataPointer(4)
				)
			formals = [this, *formals]
			formals_symbol_table.add_var(this)
		

		# set body scope
		body_symbol_table = SymbolTable(parent=formals_symbol_table)
		tree.children[3].symbol_table = body_symbol_table
		self.visit(tree.children[3])

		# change function label in mips code to not get confused with other functions with same name
		prefix_label = ''
		if function_class:
			prefix_label = "class_" + function_class.name + "_"

		tree.symbol_table.add_func(Function(
				name = func_name,
				return_type = type_,
				formals = formals,
				prefix_label=prefix_label
		),tree)

	

	def variable(self, tree):
		tree.children[0].symbol_table = tree.symbol_table
		self.visit(tree.children[0])
		type_ = stack.pop()

		var_name = tree.children[1].value

		var = Variable(
				name=var_name,
				type_=type_,
				address= IncDataPointer(4),
				)

		tree.symbol_table.add_var(var, tree)
		
		# We need var later (e.g. in formals of funtions)
		stack.append(var)


	def if_stmt(self, tree):
		
		# expr
		tree.children[1].symbol_table = tree.symbol_table
		self.visit(tree.children[1])

		# body
		body_symbol_table = SymbolTable(parent=tree.symbol_table)
		tree.children[2].symbol_table = body_symbol_table
		self.visit(tree.children[2])

		# else
		if len(tree.children) > 3:
			else_symbol_table = SymbolTable(parent=tree.symbol_table)
			tree.children[4].symbol_table = else_symbol_table
			self.visit(tree.children[4])


	def while_stmt(self, tree):
		# expr
		tree.children[1].symbol_table = tree.symbol_table
		self.visit(tree.children[1])

		# body
		body_symbol_table = SymbolTable(parent=tree.symbol_table)
		tree.children[2].symbol_table = body_symbol_table
		self.visit(tree.children[2])


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

		
		# expr
		expr_symbol_table = SymbolTable(parent=tree.symbol_table)
		
		if expr1_num:
			tree.children[expr1_num].symbol_table = expr_symbol_table
			self.visit(tree.children[expr1_num])
		
		tree.children[expr2_num].symbol_table = expr_symbol_table
		self.visit(tree.children[expr2_num])
			
		if expr3_num:
			tree.children[expr3_num].symbol_table = expr_symbol_table
			self.visit(tree.children[expr3_num])
			
		# body

		body_symbol_table = SymbolTable(parent=expr_symbol_table)
		tree.children[body_num].symbol_table = body_symbol_table
		self.visit(tree.children[body_num])


	def class_decl(self, tree):
		# CLASS IDENT (EXTENDS IDENT)? (IMPLEMENTS IDENT ("," IDENT)*)?  "{" field* "}"
		

		# TODO extends
		# TODO implements
		# TODO access modes

		# name
		class_name = tree.children[1].value

		class_ = Class(
			name= class_name,
			address= IncDataPointer(4)	# this memory will be used for vtable
		)

		type_ = Type(
			name=class_name,
			class_ref=class_,
			size=4
		)

		tree.symbol_table.add_type(type_)
		
		# fields
		class_symbol_table = SymbolTable(parent=tree.symbol_table)

		class_stack.append(class_)
		
		for subtree in tree.children[::-1]:
			if isinstance(subtree, Tree) and subtree.data == 'field':
				subtree.symbol_table = class_symbol_table
				initial_stack_len = len(stack)
				self.visit(subtree)
				while initial_stack_len < len(stack):
					stack.pop()
			else:
				break

		class_stack.pop()

		class_.set_fields(
			member_data=class_symbol_table.variables,
			member_functions=class_symbol_table.functions
		)

		

