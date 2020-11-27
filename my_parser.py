import logging
from lark import Lark, logger, __file__ as lark_file, ParseError

logger.setLevel(logging.DEBUG)

from pathlib import Path

grammer_path = Path(__file__).parent
grammar_file = grammer_path / 'grammer.lark'

parser = Lark.open(grammar_file, rel_to=__file__, parser="lalr")


def parse(code):
    try:
        parser.parse(code)
        return True
    except ParseError:
        return False


def debug_main(code):
    print("~~~~~input:")
    print(code)
    print(parser.parse(code).pretty())

if __name__ == "__main__":
    # text = input()
    text = """ 
    a = b
    """
    print(parser.parse(text).pretty())