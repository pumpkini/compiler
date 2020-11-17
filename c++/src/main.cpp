#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <lex.yy.h>
#include <stdio.h>
using namespace std ;

extern FILE *yyin,*yyout;
extern int yylex();
extern char *yytext;

int main(int argc, char* argv[]){

    if (argc < 5 ){
        cerr<< "Usage: " << argv[0] << " -i <input> -o <output>" << endl ;
        return 1;
    }

    string input_file_path = argv[2];
    string output_file_path = argv[4];

    yyout = fopen(output_file_path.c_str(), "w");
    yyin = fopen(input_file_path.c_str(),"r");

	while (yylex() != 0) {};

    return 0;

}