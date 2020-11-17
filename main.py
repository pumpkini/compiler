import sys, getopt
import re
from collections import namedtuple
import scanner

debug = False 

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
		scanner.debug_main(inputfile)
		return

	code = ""
	with open(inputfile, "r") as input_file:
		code = input_file.read()
	
	output_file = open("out/" + outputfile, "w")
	err, tokens = scanner.tokenize(code)
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
