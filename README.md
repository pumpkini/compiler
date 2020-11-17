# Compiler project

## Run all tests:
```
./run.sh [testdirectory]
(default test_directory: tests/)
```
*End test_directory with /*

*Default test_directory: tests/*

 &nbsp;


## Run one test with diff:

```
./one_test_run.sh test_number 
./one_test_run.sh test_directory test_number
(default test_directory: tests/)
```
*End test_directory with /*

*Default test_directory: tests/*

&nbsp;

## Run main in debug mode:
- prints to standard output
```
main.py -d -i <inputfile>
```

&nbsp;

## Structure:

scanner.py contain `tokenize` function
main.py call this `tokenize` function and tokenize the input file.

*to be completed*