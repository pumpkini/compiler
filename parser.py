import logging
from lark import Lark, logger

logger.setLevel(logging.DEBUG)

grammar = '''
    start: breakstmt start
        | continuestmt start
        |
    breakstmt: "break;"
    continuestmt: "continue;"

    %import common.WS
    %ignore WS
'''
parser = Lark(grammar, parser='lalr', debug=True)

print(parser.parse('break;continue;continue;break;'))