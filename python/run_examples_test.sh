#!/bin/bash

search_dir=../examples
for entry in "$search_dir"/*
do
  python3 lang.py "$entry" > /dev/null
  result=`echo $?`
  if [ "$result" -eq 0 ]
  then
    echo -e "$entry \033[32mPASSED...\033[0m"
  else 
    if [ "$entry" == "../examples/blocks_funny.lang" ]
    then
      echo -e "$entry \033[31mFALIED...\033[0m - and should have failed"
      continue
    fi
    echo -e "$entry \033[31mFALIED...\033[0m"
  fi
done