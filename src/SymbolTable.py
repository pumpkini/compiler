class Variable():
    def __init__(self, name, type_ = None, address = None):
        self.name = name
        self.type_ = type_
        self.address = address
    
class SymbolTable():
    symbol_tables = []

    def __init__(self, parent=None):
        self.variables = {}     # dict {name: Variable}
        self.parent = parent
        SymbolTable.symbol_tables.append(self)


    def find(self, variable_name):
        if variable_name in self.variables:
            return self.variables[variable_name]
        if self.parent:
            return self.parent.find(variable_name)

        return None # Varriable not found

