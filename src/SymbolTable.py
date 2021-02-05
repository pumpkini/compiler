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
