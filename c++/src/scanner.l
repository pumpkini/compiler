%option noyywrap

%option header-file="lex.yy.h"

%{
#define YY_DECL int yylex()
%}

KEYWORD void|int|double|bool|string|class|interface|null|this|extends|implements|for|while|if|else|return|break|continue|new|NewArray|Print|ReadInteger|ReadLine|dtoi|itos|btoi|itob|private|protected|public
DIGIT    [0-9]
T_ID       [a-zA-Z][a-zA-Z0-9_]*

%%
 /* keywords: */
{KEYWORD} { fprintf(yyout, "%s\n", yytext); }

 /* T_BOOLEANLITERAL */
(false|true) { fprintf(yyout, "T_BOOLEANLITERAL %s\n", yytext); }

 /* T_ID */
{T_ID} { fprintf(yyout, "T_ID %s\n", yytext); }

 /* T_DOUBLELITERAL */
[-+]?{DIGIT}+\.{DIGIT}*(?:[eE][-+]?{DIGIT}+)? { fprintf(yyout, "T_DOUBLELITERAL %s\n", yytext); }

 /* T_INTLITERAL */
((?:0x|0X)[0-9a-fA-F]+)|({DIGIT}+) { fprintf(yyout, "T_INTLITERAL %s\n", yytext); }

 /* COMMENT */
(\/\*([^*]|[\r\n]|(\*+([^*\/]|[\r\n])))*\*+\/)|(\/\/.*) {}

 /* OP_PUNCTUATION */
==|>=|<=|<|>|\+|\-|\*|\/|\%|\=|!=|\|\||\&\&|!|;|,|\.|\[|\]|\(|\)|\{|\} { fprintf(yyout, "%s\n", yytext); }

 /* T_STRINGLITERAL */
\"[^\n\"]*\" { fprintf(yyout, "T_STRINGLITERAL %s\n", yytext); }

 /* NEWLINE */
\n {}

 /* SKIP */
[ \t\v\f]+ {}

 /* UNDEFINED_TOKEN */
. { fprintf(yyout, "UNDEFINED_TOKEN\n"); }

%% 