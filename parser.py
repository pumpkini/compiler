import logging
from lark import Lark, logger, __file__ as lark_file, ParseError

logger.setLevel(logging.DEBUG)

from pathlib import Path

grammer_path = Path(__file__).parent
grammar_file = grammer_path / 'tokens.lark'

parser = Lark.open(grammar_file, rel_to=__file__, parser="lalr")

def parse(code):
    try:
        parser.parse(code)
        return True
    except ParseError:
        return False

if __name__ == "__main__":
    # text = input()
    text = """ "boba" """
    print(parser.parse(text).pretty())