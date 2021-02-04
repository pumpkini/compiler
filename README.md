# Compiler project

## Install lark
```
pip install lark-parser --upgrade
```
source: https://github.com/lark-parser/lark

doc: https://lark-parser.readthedocs.io/en/latest/index.html
 
 &nbsp;

## Run all tests:
- End test_directory with /

- Default test_directory: tests/
```
./run.sh [testdirectory]
```

 &nbsp;


## Run one test with diff:

- End test_directory with /

- Default test_directory: tests/
```
./one_test_run.sh test_number(with leading zero) 
./one_test_run.sh test_directory test_number(with leading zero)
```


&nbsp;

## Run main:
```
main.py -i <inputfile> -o <outputfile>
```

&nbsp;

## Run main in debug mode:
- prints to standard output
```
main.py -d [-s] [-p] -i <inputfile>

options for debug mode:
-s :	run scanner (use with -d)
-p :	run parser (use with -d)
```

&nbsp;
