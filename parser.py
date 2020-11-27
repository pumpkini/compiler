import logging
from lark import Lark, logger, __file__ as lark_file

logger.setLevel(logging.DEBUG)

from pathlib import Path

grammer_path = Path(__file__).parent
grammar_file = grammer_path / 'grammer.lark'

parser = Lark.open(grammar_file, rel_to=__file__, parser="lalr")

if __name__ == "__main__":
    # text = input()
    text = """
string T_ID() {
   return 1;
}

T_ID T_ID() {
   T_ID T_ID;
   return T_ID;
 }
    """
    print(parser.parse(text).pretty())