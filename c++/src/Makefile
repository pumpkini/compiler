# NOTE1: You can use wildcards in dependencies and g++ command.
# NOTE2: main should depend on all headers and code files. (*.h and *.cpp if you have multiple files)
all: ../main

../main: lex.yy.c lex.yy.h main.cpp
	g++ -o ../main -std=c++14 -w lex.yy.c main.cpp

lex.yy.c lex.yy.h: scanner.l
	flex scanner.l

debug: lex.yy.c lex.yy.h main.cpp
	g++ -o ../main -std=c++14 lex.yy.c main.cpp
	
clean:
	rm ../main lex.yy.c lex.yy.h
