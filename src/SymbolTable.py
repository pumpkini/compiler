import lark
from lark import Lark, Tree
from lark.lexer import Token
from lark.visitors import Interpreter

grammar = """
            ?start: program 
            
            program: decl+
            
            decl: variable_decl
                | function_decl
                | class_decl
                | interface_decl
            
            variable_decl: variable ";"
            
            variable: type IDENT
            
            type.2: INT
                | DOUBLE
                | BOOL
                | STRING
                | IDENT
                | type "[" "]"
            
            function_decl: type IDENT "(" formals ")" statement_block
                | VOID IDENT "(" formals ")" statement_block
            
            formals: (variable",")* variable
                |
            
            class_decl: CLASS IDENT (EXTENDS IDENT)? (IMPLEMENTS IDENT+ ",")? "{" field* "}"
            
            field: access_mode variable_decl -> field_var
                | access_mode function_decl -> field_func
            
            access_mode: PRIVATE
                | PROTECTED
                | PUBLIC
                |
            
            interface_decl: INTERFACE IDENT "{" prototype* "}"
            
            prototype: type IDENT "(" formals ")" ";"
                | VOID IDENT "(" formals ")" ";"
            
            statement_block: "{" variable_decl* statement* "}"
            
            statement: expr? ";"
                | if_stmt
                | while_stmt
                | for_stmt
                | return_stmt
                | break_stmt
                | continue_stmt
                | print_stmt
                | statement_block
            
            if_stmt: IF "(" expr ")" statement (ELSE statement)?
            
            while_stmt: WHILE "(" expr ")" statement
            
            for_stmt: FOR "(" expr? ";" expr ";" expr? ")" statement
            
            return_stmt: RETURN expr? ";"
            
            break_stmt: BREAK ";"
            
            continue_stmt: CONTINUE ";"
            
            print_stmt: PRINT (actuals)";"
            
            expr: l_value "=" expr -> expr_assign
                    | constant -> expr_constant
                    | l_value -> expr_l_value
                    | THIS -> expr_this
                    | call -> expr_call
                    | "(" expr ")" -> expr_parantheses
                    | expr "+" expr -> add
                    | expr "-" expr -> sub
                    | expr "*" expr -> mul
                    | expr "/" expr -> div
                    | expr "%" expr -> mod
                    | "-" expr -> neg
                    | expr "<" expr -> less
                    | expr "<=" expr -> less_equal
                    | expr ">" expr -> greater
                    | expr ">=" expr -> greater_equal
                    | expr "==" expr -> equal
                    | expr "!=" expr -> not_equal
                    | expr "&&" expr -> and
                    | expr "||" expr -> or
                    | "!" expr -> not
                    | READINTEGER "(" ")" -> read_integer
                    | READLINE "(" ")" -> read_line
                    | NEW IDENT -> new_ident
                    | NEWARRAY "(" expr "," type ")" -> new_array
                    | ITOD "(" expr ")" -> itod
                    | DTOI "(" expr ")" -> dtoi
                    | ITOB "(" expr ")" -> itob
                    | BTOI "(" expr ")" -> btoi
            
            l_value: IDENT
                    | expr "." IDENT
                    | expr "[" expr "]"
            
            call: IDENT "(" actuals ")"
                    | expr "." IDENT "(" actuals ")"
            
            
            actuals: expr+ ","
                | 
            
            constant: INTCONSTANT
                | DOUBLECONSTANT
                | BOOLCONSTANT
                | STRINGCONSTANT
                | NULL
            
            // keywords: EXTENDS
            //     | IMPLEMENTS
            //     | CLASS
            //     | INT
            //     | BOOL
            //     | DOUBLE
            //     | STRING 
            //     | PRIVATE
            //     | PROTECTED
            //     | PUBLIC
            //     | WHILE
            //     | IF
            //     | ELSE
            //     | FOR
            //     | VOID
            //     | RETURN
            //     | BREAK
            //     | CONTINUE
            //     | INTERFACE
            //     | PRINT
            //     | THIS
            //     | READINTEGER
            //     | READLINE
            //     | NEWARRAY
            //     | ITOD
            //     | DTOI
            //     | ITOB
            //     | BTOI
            //     | NULL
            //     | NEW
            
            EXTENDS: "extends"
            IMPLEMENTS: "implements"
            CLASS: "class"
            INT: "int"
            BOOL: "bool"
            DOUBLE: "double"
            STRING : "string"
            PRIVATE: "private"
            PROTECTED: "protected"
            PUBLIC: "public"
            WHILE: "while"
            IF: "if"
            ELSE: "else"
            FOR: "for"
            VOID: "void"
            RETURN: "return"
            BREAK: "break"
            CONTINUE: "continue"
            INTERFACE: "interface"
            PRINT: "Print"
            THIS: "this"
            READINTEGER: "ReadInteger"
            READLINE : "ReadLine"
            NEWARRAY : "NewArray"
            ITOD : "itod"
            DTOI : "dtoi"
            ITOB : "itob"
            BTOI : "btoi"
            NULL : "null"
            NEW: "new"
            
            
            //T_INTLITERAL
            INTCONSTANT: /(0x|0X)[0-9a-fA-F]+|([0-9]+)/
            
            //T_BOOLEANLITERAL
            DOUBLECONSTANT: /[-+]?\d+\.\d*(?:[eE][-+]?\d+)?/
            
            //T_BOOLEANLITERAL
            BOOLCONSTANT:  /\b(false|true)\b/
            
            //T_STRINGLITERAL
            STRINGCONSTANT:  /\"[^\n\"]*\"/
            
            //T_ID
            IDENT: /(?!(extends|implements|class|int|bool|double|string|private|protected|public|while|if|else|for|void|return|break|continue|interface|Print|this|ReadInteger|ReadLine|NewArray|itod|dtoi|itob|btoi|null|new|true|false)\b)[a-zA-Z]\w*/
            
            COMMENT: /\/\/[^\n]*/
                | "/*" /.*?/s "*/"
            
            // MISMATCH: /./
            
            //OP_PUNCTUATION: ==|>=|<=|<|>|\+|\-|\*|\/|\%|\=|!=|\|\||\&\&|!|;|,|\.|\[|\]|\(|\)|\{|\}
            
            %import common.NEWLINE
            %import common.WS_INLINE
            
            %ignore WS_INLINE
            %ignore NEWLINE
            %ignore COMMENT
            """

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
