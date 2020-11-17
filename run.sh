#!/bin/bash
OUTPUT_DIRECTORY="out/"
TEST_DIRECTORY="tests/"
REPORT_DIRECTORY="report/"

echo "Usage: 
./run.sh [testdirectory]
(default test_directory: tests/)
Please end test_directory with /"

OUTPUT_DIRECTORY="out/"
TEST_DIRECTORY="tests/"
REPORT_DIRECTORY="report/"

if [ "$#" -eq 1 ]; then
    TEST_DIRECTORY=$1
fi

echo $TEST_DIRECTORY
mkdir -p out
mkdir -p report
cd $TEST_DIRECTORY
prefix="t" ;
dirlist=(`ls ${prefix}*.in`) ;

NUMBER_OF_PASSED=0
NUMBER_OF_FAILED=0
cd ../
for filelist in ${dirlist[*]}
do
    filename=`echo $filelist | cut -d'.' -f1`;
    output_filename="$filename.out"
    report_filename="$filename.report.txt"
    echo "Running Test $filename -------------------------------------"
    if command -v python3; then
        python3 main.py -i "$TEST_DIRECTORY$filelist" -o $output_filename
    else
        python main.py -i "$TEST_DIRECTORY$filelist" -o $output_filename
    fi
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
            ((NUMBER_OF_FAILED++))
            echo "---- test failed !"
        echo
        fi 
    else
        echo "Code did not execute successfuly!"
        ((NUMBER_OF_FAILED++))
    fi



done

echo "Passed : $NUMBER_OF_PASSED"
echo "Failed : $NUMBER_OF_FAILED"

