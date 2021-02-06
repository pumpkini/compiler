class Variable():
    def __init__(self, name, type_ = None, address = None, size = 0):
        self.name = name
        self.type_ = type_
        self.address = address
        self.size = size
    

class Function():
        def __init__(self, name, type_ = None, **kwargs):
            self.name = name
            self.type_ = type_
            self.arguments = {}
            for key, value in kwargs.items():
                self.arguments[key] = value     #dict {name : Type}



class SymbolTable():
    symbol_tables = []

    def __init__(self, parent=None):
        self.variables = {}     # dict {name: Variable}
        self.functions = {}     # dict {name: Function}
        self.parent = parent
        SymbolTable.symbol_tables.append(self)


    def find(self, variable_name):
        if variable_name in self.variables:
            return self.variables[variable_name]
        if self.parent:
            return self.parent.find(variable_name)

        return None # Varriable not found

