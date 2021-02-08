
class Type_():
    types = {}
    types_index = {}
    def __init__(self, name, size):
        self.name = name
        self.size = size
        self.index = len(Type_.types)
        Type_.types[name] = self
        Type_.types_index[self.index] = name

    @classmethod
    def get_type_by_name(cls, name):
        if name in cls.types:
            return cls.types[name]

        return None # Type not found

    @classmethod
    def get_type_by_index(cls, index):
        if index not in cls.types_index:
            return None # Type not found
        
        name = cls.types_index[index]
        
        return cls.get_type_by_name(name)



class Variable():
    def __init__(self, name= None, type_:Type_ = None, address = None, size = 0):
        self.name = name
        self.type_ = type_
        self.address = address
        self.size = size

    def __str__(self) -> str:
        return f"V-{self.name}-{self.type_}-{self.address}-{self.size}"
    

class Function():
    def __init__(self, name, type_:Type_ = None, **kwargs):
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


