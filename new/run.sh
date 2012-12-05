#!/bin/bash

while :
do
    inotifywait -rqe move  .
    pkill -9 python
    python2 rest.py &
done
