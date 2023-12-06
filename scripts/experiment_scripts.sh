#!/bin/bash

python3 scripts/run_exps.py --name=avg_1Mbps_abr --trace_set=hsdpa --n_train_runs=8 --n_test_runs=8 --results_dir=results/ --bba --target_thr=1.0

# Runs experiment:
# Video: livestream
# Trace: Verizon1
# Algorithm: bba
python3 sim/run_exp.py -- --video=real/data/videos/livestream/video.dat --mm-trace=network/traces/cellular/Verizon1.dat --results-dir=results/bba_test --bba