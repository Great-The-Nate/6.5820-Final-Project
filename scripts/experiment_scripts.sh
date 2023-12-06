#!/bin/bash

python3 scripts/run_exps.py --name=avg_1Mbps_abr --trace_set=hsdpa --n_train_runs=8 --n_test_runs=8 --results_dir=results/ --bba --target_thr=1.0

# Runs experiment:
# Video: livestream
# Trace: Verizon1
# Algorithm: bba
# Max chunks: No limit
python3 sim/run_exp.py -- --video=real/data/videos/livestream/video.dat --mm-trace=network/traces/cellular/Verizon1.dat --results-dir=results/bba_test --max-chunks=-1 --bba

# Runs experiment:
# Video: livestream
# Trace: Verizon1
# Algorithm: bola
# Max chunks: No limit
python3 sim/run_exp.py -- --video=real/data/videos/livestream/video.dat --mm-trace=network/traces/cellular/Verizon1.dat --results-dir=results/bola_test --max-chunks=-1 --bola

# Runs experiment:
# Video: livestream
# Trace: Verizon1
# Algorithm: throughput
# Max chunks: No limit
python3 sim/run_exp.py -- --video=real/data/videos/livestream/video.dat --mm-trace=network/traces/cellular/Verizon1.dat --results-dir=results/throughput_test --max-chunks=-1 --tb
