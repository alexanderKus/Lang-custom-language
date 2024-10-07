#!/bin/bash

total=0
for entry in ./*
do
  if [ -f "$entry" ]
  then
    lines=`wc -l "$entry" | awk '{print $1}'`
    filename=`wc -l "$entry" | awk '{print $2}'`
    total=$(( $total+$lines ))
    echo "LINES:$lines FILE: $filename"
  fi
done
echo "TOTAL LINES COUNT: $total"