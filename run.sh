#!/bin/bash
echo "
Usage: 
./run.sh [testdirectory]
(default test_directory: tests/)
Please end test_directory with /

"

OUTPUT_DIRECTORY="out/"
TEST_DIRECTORY="tests/"
REPORT_DIRECTORY="report/"
SOURCE_DIRECTORY="src/"


if [ "$#" -eq 1 ]; then
    TEST_DIRECTORY=$1
fi

mkdir -p $OUTPUT_DIRECTORY
mkdir -p $REPORT_DIRECTORY

cd $TEST_DIRECTORY

prefix="t" ;
dirlist=(`ls ${prefix}*.d`) ;

NUMBER_OF_PASSED=0
NUMBER_OF_FAILED=0
cd ../

echo ' ' > wrong-tests.txt
for filelist in ${dirlist[*]}
do
    filename=`echo $filelist | cut -d'.' -f1`;
    output_filename="$filename.out"
    output_asm="$filename.s"
    program_input="$filename.in"
    report_filename="$filename.report.txt"

    echo "Running Test $filename -------------------------------------"
    if command -v python3; then
        python3 "$SOURCE_DIRECTORY/main.py" -i "$TEST_DIRECTORY$filelist" -o "$OUTPUT_DIRECTORY$output_asm"
    else
        python "$SOURCE_DIRECTORY/main.py" -i "$TEST_DIRECTORY$filelist" -o "$OUTPUT_DIRECTORY$output_asm"
    fi
    if [ $? -eq 0 ]; then
        echo "Code Compiled Successfuly!"
	spim -a -f "$OUTPUT_DIRECTORY$output_asm" < "$TEST_DIRECTORY$program_input" > "$OUTPUT_DIRECTORY$output_filename"
    # echo ""
    # echo "RESULT"
    # cat "$OUTPUT_DIRECTORY$output_filename"
	if [ $? -eq 0 ]; then
		echo "Code Executed Successfuly!"
		if command -v python3; then
		    python3 comp.py -a "$OUTPUT_DIRECTORY$output_filename" -b "$TEST_DIRECTORY$output_filename" -o "$REPORT_DIRECTORY$report_filename"
		else
		    python comp.py -a "$OUTPUT_DIRECTORY$output_filename" -b "$TEST_DIRECTORY$output_filename" -o "$REPORT_DIRECTORY$report_filename"
		fi
		if [[ $? = 0 ]]; then
		    ((NUMBER_OF_PASSED++))
		    echo "++++ test passed"
		else
            echo $filename >> wrong-tests.txt
		    ((NUMBER_OF_FAILED++))
		    echo "---- test failed !"
		echo
		fi
    	fi 
    else
        echo $filename >> wrong-tests.txt
        echo "Code did not execute successfuly!"
        ((NUMBER_OF_FAILED++))
    fi



done

echo "Passed : $NUMBER_OF_PASSED"
echo "Failed : $NUMBER_OF_FAILED"

cat wrong-tests.txt

if [ "$#" -eq 1 ]; then
    zero=0;
    if [ "$NUMBER_OF_FAILED" -eq "$zero" ]; then
        exit 0;
    fi
    exit 1;
fi

