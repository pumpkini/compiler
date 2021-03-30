# Decaf Compiler

CE414 Compiler course project\
Sharif University of Technology\
Fall 1399/2020

---

This is a *Decaf* compiler in python that compiles decaf code to mips.

Decaf documention can be found in project root.

CAUTION! This is not complete decaf compiler but support most of language features.

## Usage

Install requirements from `requirements.txt`.

Install *spim*.

### Run all tests

Run `run.sh` to run all tests. You can change test directory in `run.sh` file.

### Compile one program

Put your decaf file in `./tmp/in.d` and run `./src/cgen.py`. This will create a `res.mips` file in `./tmp`. You can run mips file with spim using following command:
```bash
spim -a -f res.mips < input.txt > output.txt
```
