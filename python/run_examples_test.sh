#!/bin/bash

search_dir=../examples
for entry in "$search_dir"/*
do
  python3 main.py "$entry" > /dev/null
  result=`echo $?`
  if [ "$result" -eq 0 ]
  then
    echo -e "$entry \033[32mPASSED...\033[0m"
  else
    echo -e "$entry \033[31mFALIED...\033[0m"
    exit 69
  fi
done