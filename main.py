import sys, getopt
import re
from collections import namedtuple
import scanner
import my_parser


def only_scanner(code, output_file):
	err, tokens = scanner.tokenize(code)
	for t in tokens:
		if t.group == "OP_PUNCTUATION" or t.group == "KEYWORD":
			output_file.write(t.value+ "\n")
		else:
			output_file.write(t.group + " " + t.value + "\n")
	if err is not None:
		output_file.write(err + "\n")
	output_file.close()


def main(argv):
	debug = False 
	run_scanner = False
	run_parser = False

	inputfile = ''
	outputfile = ''
	try:
		opts, args = getopt.getopt(argv,"dhpsi:o:",["ifile=","ofile="])
	except getopt.GetoptError:
		print ('main.py -i <inputfile> -o <outputfile>\nmain.py -d [-s] [-p] -i <inputfile>')
		sys.exit(2)

	for opt, arg in opts:
		if opt == '-d':
			debug = True
		if opt == '-s':
			run_scanner = True
		if opt == '-p':
			run_parser = True
		if opt == '-h':
			print ('main.py -i <inputfile> -o <outputfile>\nmain.py -d [-s] [-p] -i <inputfile>')
			sys.exit()
		elif opt in ("-i", "--ifile"):
			inputfile = arg
		elif opt in ("-o", "--ofile"):
			outputfile = arg

	code = ""
	with open(inputfile, "r") as input_file:
		code = input_file.read()
	
	if debug:
		if run_scanner:
			scanner.debug_main(code)
		if run_parser:
			my_parser.debug_main(code)
		return

	output_file = open("out/" + outputfile, "w")
	# only_scanner(code, output_file)

	can_parse = my_parser.parse(code)
	if can_parse:
		output_file.write("OK")
	else:
		output_file.write("Syntax Error")


if __name__ == "__main__":
	main(sys.argv[1:])
