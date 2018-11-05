#!/bin/bash

while read n l; do
    echo -en "$n\t"
    for i in $l; do
        echo -en "$(echo "scale=8;$i*12*2.54"|bc|sed 's/0\+$//')\t" 
    done
    echo
done < <(grep -v '^#' "$1")

# vim: set ts=2 sw=2 expandtab tw=100
