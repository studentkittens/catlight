#!/bin/bash
# Silly and very rude script.
#
# Somehow using multiprocess prevents
# flask from reloading the application.
# This reloads the server the hard way.

while :
do
    (python2 rest.py 1>&2 > /dev/null) & 
    inotifywait -rqe move  .
    pkill -9 python
done
