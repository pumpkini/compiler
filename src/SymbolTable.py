
class Type():
    types = {}
    types_index = {}
    def __init__(self, name, size):
        self.name = name
        self.size = size
        self.index = len(Type.types)
        Type.types[name] = self
        Type.types_index[self.index] = name

    @classmethod
    def get_type_by_name(name):
        if name in Type.types:
            return Type.types[name]

        return None # Type not found

    @classmethod
    def get_type_by_index(index):
        if index not in Type.types_index:
            return None # Type not found
        
        name = Type.types_index[index]
        
        return Type.get_type_by_name(name)



class Variable():
    def __init__(self, name, type_ = None, address = None, size = 0):
        self.name = name
        self.type_ = type_
        self.address = address
        self.size = size

    def __str__(self) -> str:
        return f"V-{self.name}-{self.type_}-{self.address}-{self.size}"
    

class Function():
    def __init__(self, name, type_ = None, **kwargs):
            self.name = name
            self.type_ = type_
            self.arguments = {}
            for key, value in kwargs.items():
                self.arguments[key] = value     #dict {name : Type}

    def __str__(self) -> str:
        return f"F-{self.name}-{self.type_}-{self.arguments}"
    

class SymbolTable():
    symbol_tables = []

    def __init__(self, parent=None):
        self.variables = {}     # dict {name: Variable}
        self.functions = {}     # dict {name: Function}
        self.parent = parent
        SymbolTable.symbol_tables.append(self)


    def find_var(self, variable_name):
        if variable_name in self.variables:
            return self.variables[variable_name]
        if self.parent:
            return self.parent.find_var(variable_name)

        return None # Varriable not found

    def find_func(self, func_name):
        if func_name in self.variables:
            return self.functions[func_name]
        if self.parent:
            return self.parent.find_func(func_name)

        return None # Varriable not found


    def get_index(self):
        return SymbolTable.symbol_tables.index(self)

    def __str__(self) -> str:
        return f"SYMBOLYABLE: {self.get_index()} PARENT: {self.parent.get_index() if self.parent else -1}\n\tVARIABLES: {[v.__str__() for v in self.variables.values()]}\n\tFUNCTIONS: {[f.__str__() for f in self.functions]}"


