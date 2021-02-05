import logging
from lark import Lark, logger, __file__ as lark_file, ParseError, Tree
from lark.visitors import Interpreter, v_args

logger.setLevel(logging.DEBUG)

from pathlib import Path

grammer_path = Path(__file__).parent
grammer_file = grammer_path / 'grammer.lark'

parser = Lark.open(grammer_file, rel_to=__file__, parser="lalr")


class SymbolTable():
    symbol_tables = []

    def __init__(self, parent=None):
        self.variables = {}
        self.parent = None
        SymbolTable.symbol_tables.append(self)


class Cgen(Interpreter):
    def visit(self, tree, *args, **kwargs):
        f = getattr(self, tree.data)
        wrapper = getattr(f, 'visit_wrapper', None)
        if wrapper is not None:
            return f.visit_wrapper(f, tree.data, tree.children, tree.meta)
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
        print(symbol_table)
        print(symbol_table.variables)
        print("hehehe")

    def decl(self, tree, *args, **kwargs):
        code = ''
        symbol_table = kwargs.get('symbol_table')
        for decl in tree.children:
            if decl.data == 'variable_decl' or decl.data == 'function_decl' or decl.data == 'class_decl':
                code += self.visit(decl)
        return code

