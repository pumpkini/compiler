from utils import SemanticError
from lark.visitors import  Interpreter, Visitor_Recursive, Visitor
from lark import Tree


class Type():
	# types = {}
	# types_index = {}
	def __init__(self, name, size=None):
		self.name = name
		self.size = size
		# self.index = len(Type.types)
		# Type.types[name] = self
		# Type.types_index[self.index] = name

	def __str__(self) -> str:
		return f"<T-{self.name}-{self.size}>"
	# @classmethod
	# def get_type_by_name(cls, name):
	# 	if name in cls.types:
	# 		return cls.types[name]

	# 	return None # Type not found

	# @classmethod
	# def get_type_by_index(cls, index):
	# 	if index not in cls.types_index:
	# 		return None # Type not found
		
	# 	name = cls.types_index[index]
		
	# 	return cls.get_type_by_name(name)



class Variable():
	def __init__(self, name= None, type_:Type = None, address = None, size = 0):
		self.name = name
		self.type_ = type_
		self.address = address
		self.size = size

	def __str__(self) -> str:
		return f"<V-{self.name}-{self.type_}-{self.address}-{self.size}>"
	

class Function():
	def __init__(self, name, arguments=[], return_type:Type = None):
			self.name = name
			self.return_type = return_type
			self.arguments = arguments	# array: variable (order is important)

	def __str__(self) -> str:
		return f"<F-{self.name}-{self.return_type}-{[a.__str__() for a in self.arguments]}>"
	

class SymbolTable():
	symbol_tables = []

	def __init__(self, parent=None):
		self.variables = {}     # dict {name: Variable}
		self.functions = {}     # dict {name: Function}
		self.types = {}			# dict {name: Type}
		self.parent = parent
		SymbolTable.symbol_tables.append(self)


	def find_var(self, name):
		if name in self.variables:
			return self.variables[name]
		if self.parent:
			return self.parent.find_var(name)

		return None # Varriable not found

	def find_func(self, name):
		if name in self.functions:
			return self.functions[name]
		if self.parent:
			return self.parent.find_func(name)

		return None # Varriable not found

	def find_type(self, name):
		if name in self.types:
			return self.types[name]
		if self.parent:
			return self.parent.find_type(name)

		return None # Varriable not found		

	def get_index(self):
		return SymbolTable.symbol_tables.index(self)

	def __str__(self) -> str:
		return f"SYMBOLYABLE: {self.get_index()} PARENT: {self.parent.get_index() if self.parent else -1}\n\tVARIABLES: {[v.__str__() for v in self.variables.values()]}\n\tFUNCTIONS: {[f.__str__() for f in self.functions]}"

	def add_var(self, var:Variable, tree=None):
		if self.find_var(var.name):
			raise SemanticError('Variable already exist in scope', tree=tree)
		
		self.variables[var.name] = var

	def add_func(self, func:Function, tree=None):
		if self.find_var(func.name):
			raise SemanticError('Function already exist in scope', tree=tree)

		self.functions[func.name] = func

	def add_type(self, type_:Type, tree=None):
		if self.find_var(type_.name):
			raise SemanticError('Type already  exist in scope', tree=tree)

		self.types[type_.name] = type_



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
		stack.append("?")


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

		# TODO void

		# type 
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
		
		# set body scope
		body_symbol_table = SymbolTable(parent=formals_symbol_table)
		tree.children[3].symbol_table = body_symbol_table
		self.visit(tree.children[3])

		tree.symbol_table.add_func(Function(
				name = func_name,
				return_type = type_,
				arguments = formals
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

