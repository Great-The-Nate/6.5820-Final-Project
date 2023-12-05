# 6.5820 Final Project

## Dev Commands
There are currently three ABR algorithms implemented in `your_code/bba.py`, `your_code/bola.py`, and `your_code/tb.py`

To run the batched mode experiment using rescaled 1Mbps hsdpa traces with bba, run `python3 scripts/run_exps.py --name=avg_1Mbps_abr --trace_set=hsdpa --n_train_runs=8 --n_test_runs=8 --results_dir=results/ --bba  --target_thr=1.0`

If you want to run bola or tb, replace `--bba` with `--bola` or `--tb` respectively.

# ABR Algorithms

## Description

In a realistic ABR setting, a client (typically a mobile device) is streaming video from a web server on a
bandwidth-limited network link (typically a cellular link). The ABR algorithm runs on the client end and
makes decisions about the next bitrate to fetch based on the network conditions and current client state.
Client state includes features such as its current buffer occupancy, among others. The decisions made by
the ABR algorithm affect the QoE experienced by the user watching the video. For instance, if the ABR
algorithm always fetches video chunks of low quality, then it might never lead to buffering but it would lead to
poor perceptual video quality. On the other hand, if it always fetches chunks of the highest quality, then it
might cause too much buffering when the network bandwidth is low. So, a good ABR algorithm
has to *adapt* to the current network conditions.

## Setup

### Installation

You'll need the following packages. Feel free to install using your favorite method (e.g., conda, pip3, ...)
```
numpy
absl-py
matplotlib
```
(for instance, for pip do `pip3 install numpy absl-py matplotlib`)

### Video

We will be streaming [Big Buck Bunny](https://www.youtube.com/watch?v=aqz-KE-bpKQ).
Since we're using simulation, you won't be able to see the video play in real-time.

This video is encoded in the following bitrates (in Kbps):

```
44 86 125 173 212 249 315 369 497 564 764 985 1178 1439 2038 2353 2875 3262 3529 3844
```

Each chunk is of `4 seconds` duration.
The chunk sizes are declared in `real/data/videos/BigBuckBunny/trace.dat`.
We expose a video object to your ABR algorithm (see `your_code/video.py`) for you to read this metadata easily.

### Traces

There are a few sample traces in `network/traces/cellular` for you to run simple experiments with your ABR algorithm.
We also provide another two sets of traces for a more thorough evaluation:
[HSDPA](http://home.ifi.uio.no/paalh/dataset/hsdpa-tcp-logs/),
[FCC](https://www.fcc.gov/general/measuring-broadband-america).

Please don't try to overfit to the `test` traces for the above datasets.

Some of these traces might have a very high or very low average throughput. You might want to rescale it to a
more reasonable value for ABR say somewhere between 300 Kbps and 4 Mbps.
In order to scale a trace down to the desired average throughput, we provide you with the `network/scale_trace.py` script.
Please don't modify the `network/traces` directory; instead, make a separate directory for traces that you scaled yourself.
For example, to scale a trace to 2Mbps rescaled trace from `network/traces/cellular/Verizon1.dat`, run:

```
mkdir -p network/traces/scaled_traces
python3 network/scale_trace.py --trace-in network/traces/cellular/Verizon1.dat --trace-out /tmp/test.txt --target-mbps=2
```

### Video, Objective, and QOE
This class is instantiated with the ABR server and has access to both a `Video` and `Objective` object. The `Video` gives you
information about the available bitrates of the video and chunk sizes for all video chunks. The `Objective` is your interface to the
Quality of Experience (QoE) metric you'll use to judge how "good" your algorithm is. Recall that the QoE for the first chunk
is:

```
QoE(e_0) = P(e_0) - c * R(e_0)
```

and QoE for the `i`th chunk is:

```
QoE(e_i) = P(e_i) - a * R(e_i) - b * |P(e_i) - P(e_{i-1})|
```

where:
 - `e_i` is the bitrate of the i-th chunk
 - `P(e_i)` is the perceptual quality of the chunk. For your experiments, `P(e_i) = 100 * e_i / max{e_i}`, i.e. it is on a scale of 0--100.
 - `R(e_0)` is the delay between loading the video player and playing the first chunk
 - `R(e_i)` for i > 0 is the rebuffering time required to play the i-th chunk
 - `a` is the rebuffering penalty, which is set to 25. This means that rebuffering for 4 seconds negates the value of playing a single high-quality chunk.
 - `b` is the smoothness penalty, which is set to 1.
 - `c` is the startup delay penalty, which is 5.

You must fill out the `next_quality(..)` function in the `ABR` class.
Read the comments in `abr.py`, `video.py`, and `objective.py` to understand what information is available to you. You may use this information however you'd like in your ABR algorithm. Please do **not** modify `video.py` or `objective.py`.

A reference rate based ABR algorithm is provided for your reference in `your_code/rb.py`.
Please refer to it before you start implementing your own algorithm.

### Running experiments

Over the course of developing an ABR algorithm, you may want to  evaluate your algorithm in single trace mode and batched mode.

#### Single trace

In this case, you are evaluating your algorithm on just a single trace. This is helpful when you're trying to study the behavior of your algorithm on a single interesting case.

In order to run an experiment with your ABR algorithm on the trace `network/traces/cellular/Verizon1.dat`, use the following command:

```
python3 sim/run_exp.py -- --mm-trace=network/traces/cellular/Verizon1.dat --results-dir=${results_dir}
```

For instance, if you specify `results/test` for the `results_dir` argument, then you should be able to find the following files there on a successful run:

* `buffer-bitrate-throughput.png` : Plots buffer size, bitrates fetched by abr and link capacity in a single plot
* `qoe_plot.png`: Plots different components of the QoE objective.
* `results.json`: Aggregate QoE metrics for the run.
* `qoe.txt`: Chunk-by-chunk breakdown of the qoe objective achieved

#### Batched mode

In this case, you are evaluating your algorithm on a relatively large set of traces. This is helpful when you would like to perform a comprehensive evaluation on a set of traces. For this, you would need to split the dataset of traces into `train` and `test` sets. We already provide you with these splits for `hsdpa` and `fcc` traces in `network/traces/` directory.

To evaluate your algorithm in batched mode run the following command:

```
python3 scripts/run_exps.py --name=batch_eval_1 --trace_set=fcc --n_train_runs=8 --n_test_runs=8 --results_dir=results/
```

This will sample a random set of 8 traces (with replacement) from `network/traces/fcc/train` and 8 from `network/traces/fcc/test`.
It would scale these traces so that their average throughput is in the range from `300 Kbps` to `4 Mbps`.
It would kick-off experiments on these traces in parallel and dump the results into the specified `results_dir/batch_eval_1`.

**CDFs.** In order to compare different ABR algorithms on different sets of traces, we give you the script `scripts/plt_cdf.py` to plot multiple runs together in a CDF. For instance, if you have used the above batched mode command to create two runs `batch_eval_1` and `batch_eval_2` in `results` folder, then use the following to plot the cdf of qoe values:

```
python3 scripts/plt_cdf.py --runs batch_eval_1 batch_eval_2
```

If this was successful, you will see the plot in the file `cdfs/batch_eval_1_batch_eval_2/*.png`
For example, CDFs comparing robust-mpc, buffer-based and rate-based schemes on hsdpa train dataset is in [figures/hsdpa.png](figures/hsdpa.png).
