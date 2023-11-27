#!/bin/bash

alg="bbaOthers"
speed="${1}mbps"

mkdir results/${alg}
mkdir results/${alg}/$speed
mkdir results/${alg}/$speed/cellular/

results_dir=results/${alg}/$speed/cellular/
echo 
echo Putting results in ${results_dir}

arr=("ATT1" "ATT2" "TMobile1" "TMobile2" "Verizon1" "Verizon2")

for trace in "${arr[@]}"
do
    echo "-------------"
    echo Running $trace trace
    mkdir results/${alg}/$speed/cellular/$trace
    python sim/run_exp.py -- \
        --results-dir=${results_dir}/${trace} \
        --mm-trace=network/scaled_traces/${speed}/cellular/${trace}_scaled_${speed}.dat
done


