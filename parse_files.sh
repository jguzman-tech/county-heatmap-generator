#!/bin/bash

pattern="./data/*.csv"
total=$(ls $pattern | wc -l)
count=0

for file in $pattern
do
    in_file="$file"
    # change file extension from .csv to .pkl
    file=$(echo "$file" | sed "s/.csv/.pkl/g")
    # change directory from ./data to ./jar
    file=$(echo "$file" | sed "s/.\/data/.\/jar/g")
    out_file="$file"
    command="python3 data_parser.py ${in_file} ${out_file}"
    echo "parsing file $in_file"
    $command
    count=$((count + 1))
    echo "parsed ${count} out of ${total} files"
done
