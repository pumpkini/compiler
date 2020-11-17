import sys, getopt
import re
from collections import namedtuple

debug = False 

Token = namedtuple('Token', 'group, value')

keywords = (
"void",
"int",
"double",
"bool",
"string",
"class",
"interface",
"null",
"this",
"extends",
"implements",
"for",
"while",
"if",
"else",
"return",
"break",
"continue",
"new",
"NewArray",
"Print",
"ReadInteger",
"ReadLine",
"dtoi",
"itos",
"btoi",
"itob",
"private",
"protected",
"public"
)

token_specification = [
	('T_BOOLEANLITERAL',r'(false|true)\b'),           							 			# Boolean
	('T_ID',       		r'[a-zA-Z]\w*'),    										# Identifiers
    ('T_DOUBLELITERAL', r'[-+]?\d+\.\d*(?:[eE][-+]?\d+)?'), 								# floating number
    ('T_INTLITERAL',	r'((?:0x|0X)[0-9a-fA-F]+)|([0-9]+)'),  								# Integer or decimal number
    ('COMMENT',       	r'(/\*([^*]|[\r\n]|(\*+([^*/]|[\r\n])))*\*+/)|(//.*)'),      		# COMMENT
	('OP_PUNCTUATION',	r'==|>=|<=|<|>|\+|\-|\*|\/|\%|\=|!=|\|\||\&\&|!|;|,|\.|\[|\]|\(|\)|\{|\}'), # OP and PUNCT
    ('T_STRINGLITERAL', r'\"[^\n\"]*\"'),        											# String
    ('NEWLINE',  		r'\n'),           													# Line endings
    ('SKIP',     		r'[ \t\v\f]+'),      												# Skip over spaces and tabs
    ('MISMATCH', 		r'.'),            													# Any other character
]


def tokenize(code):
	regex = '|'.join('(?P<{}>{})'.format(t[0], t[1]) for t in token_specification)
	line_num = 1
	tokens = []
	for match in re.finditer(regex, code):
		value = match.group()
		group = match.lastgroup

		if debug:
			print("group:", group, "\tvalue:", repr(value))

		if group == 'T_ID' and value in keywords:
			group = "KEYWORD"
		elif group == 'NEWLINE':
			line_num += 1
			continue
		elif group == 'SKIP' or group == "COMMENT":
			continue
		elif group == 'MISMATCH':
			return ('UNDEFINED_TOKEN', tokens)
		token = Token(group=group, value=value)
		tokens.append(token)
	return (None, tokens)


def debug_main(inputfile):
	code = ""
	with open(inputfile, "r") as input_file:
		code = input_file.read()

	print("~~~input")
	print(code)
	try:
		err, tokens = tokenize(code)
		print("~~~tokens:")
		for t in tokens:
			if t.group == "OP_PUNCTUATION" or t.group == "KEYWORD":
				print(t.value)
			else:
				print(t.group, t.value)
		if err is not None:
			print(err)
	except RuntimeError as e:
		print("SyntaxError:", e)
	

def main(argv):
	global debug

	inputfile = ''
	outputfile = ''
	try:
		opts, args = getopt.getopt(argv,"dhi:o:",["ifile=","ofile="])
	except getopt.GetoptError:
		print ('main.py -i <inputfile> -o <outputfile>\nmain.py -d -i <inputfile>')
		sys.exit(2)

	for opt, arg in opts:
		if opt == '-d':
			debug = True
		if opt == '-h':
			print ('main.py -i <inputfile> -o <outputfile>\nmain.py -d -i <inputfile>')
			sys.exit()
		elif opt in ("-i", "--ifile"):
			inputfile = arg
		elif opt in ("-o", "--ofile"):
			outputfile = arg

	if debug:
		debug_main(inputfile)
		return

	
	code = ""
	with open(inputfile, "r") as input_file:
		code = input_file.read()
	
	output_file = open("out/" + outputfile, "w")
	err, tokens = tokenize(code)
	for t in tokens:
		if t.group == "OP_PUNCTUATION" or t.group == "KEYWORD":
			output_file.write(t.value+ "\n")
		else:
			output_file.write(t.group + " " + t.value + "\n")
	if err is not None:
		output_file.write(err + "\n")
	output_file.close()


if __name__ == "__main__":
	main(sys.argv[1:])
