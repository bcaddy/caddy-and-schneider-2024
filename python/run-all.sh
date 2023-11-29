#!/usr/bin/env bash

# description

#set -x #echo all commands

# If ctrl-c is sent trap it and kill all child processes
trap "kill -- -$$" EXIT

python ./advecting-field-loop.py -f &
python ./blast-wave.py -f &
python ./circularly-polarized-alfven-convergence.py -f &
python ./linear-wave-convergence.py -f &
python ./orszag-tang-vortex.py -f &
python ./scaling_plots.py -f &
python ./shock-tubes.py -f &

wait
