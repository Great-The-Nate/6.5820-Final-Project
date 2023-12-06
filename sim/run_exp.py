import argparse
import copy
import json
import os
import sys

sys.path.append("./")
from your_code import abr, objective, video
from absl import app, logging
from sim import network
from sim.env import Env
from sim.generate_plts import generate_plts
import utils


KILO = 1000.0
BITS_IN_BYTE = 8
CHUNK_DUR = 4.0


class CustomPythonFormatter(logging.PythonFormatter):
    def format(self, record):
        return super(logging.PythonFormatter, self).format(record)


parser = argparse.ArgumentParser("Run experiment using Simulator")
parser.add_argument(
    "--video",
    type=str,
    default="real/data/videos/BigBuckBunny/trace.dat",
    help="Root directory of video to play",
)
parser.add_argument(
    "--startup-penalty",
    type=float,
    default=5.0,
    help="Penalty to QoE for each second spent in startup",
)
parser.add_argument(
    "--rebuffer-penalty",
    type=float,
    default=25.0,
    help="Penalty to QoE for each second spent rebuffering",
)
parser.add_argument(
    "--smooth-penalty",
    type=float,
    default=1.0,
    help="Penalty to QoE for smoothness changes in bitrate",
)
parser.add_argument(
    "--max-chunks",
    type=int,
    default=50,
    help="Maximum number of chunks to watch before killing this server."
    + " If negative, there is no limit",
)
parser.add_argument(
    "--mm-trace", type=str, required=True, help="Mahimahi link trace to use"
)
parser.add_argument("--mm-start-idx", type=int, default=0)
parser.add_argument(
    "--results-dir", 
    type=str,  
    default=os.path.join(os.getcwd(), "../results")
)
parser.add_argument(
    "--live-delay",
    type=int,
    default=0,
    help="The delay in seconds that the client is behind the broadcaster beyond the delay implied by \
        the chunk size (e.g. for a fully live stream with 4 second chunks there is a implied minimum \
        delay of 4 seconds but live-delay would be 0)."
)

# use buffer based algorithm: BBA0
parser.add_argument('--bba', action='store_true')
# use buffer based algorithm: BOLA
parser.add_argument('--bola', action='store_true')
# use throughput algorithm
parser.add_argument('--tb', action='store_true')
# use retransmission algorithm
parser.add_argument('--rt', action='store_true')


logging.set_verbosity(logging.INFO)
logging.get_absl_handler().setFormatter(
    CustomPythonFormatter(fmt="[%(name)s:%(lineno)d] %(levelname)s - %(message)s")
)
logging.info("Loaded arguments for single experiment run")


def parse_args(argv):
    if "--" in argv:
        remaining_args = argv[argv.index("--") + 1 :]
        argv = argv[: argv.index("--")]
    else:
        remaining_args = []
    args = parser.parse_args(argv)
    return args, remaining_args


def main(argv):
    args, _ = parse_args(argv[1:])
    vid = video.Video(args.video)

    if args.max_chunks is not None:
        vid.set_max_chunks(args.max_chunks)

    pqs = vid.get_bitrates()
    max_pq = max(pqs)
    pqs = [100 * float(q) / max_pq for q in pqs]

    pq_dict = {}
    for br, pq in zip(vid.get_bitrates(), pqs):
        pq_dict[br] = pq

    obj = objective.Objective(pq_dict, args.startup_penalty, args.rebuffer_penalty, args.smooth_penalty)
    net = network.Network(args.mm_trace, args.mm_start_idx)
    env = Env(vid, obj, net, args)

    objective_client = copy.deepcopy(obj)
    video_client = copy.deepcopy(vid)
    
    # Updated to use differnt algorithms by adding flags
    if args.bba:
        from your_code.bba import AbrAlg
        abr_alg_fn = AbrAlg
    if args.bola:
        from your_code.bola import AbrAlg
        abr_alg_fn = AbrAlg
    elif args.tb:
        from your_code.tb import AbrAlg
        abr_alg_fn = AbrAlg
    elif args.rt:
        from your_code.rt import AbrAlg
        abr_alg_fn = AbrAlg
    else:
        # Default to BBA
        from your_code.bba import AbrAlg        
        abr_alg_fn = AbrAlg
    abr_alg = abr_alg_fn(video_client, objective_client, args)

    total_rebuf_sec = 0
    rebuf_sec = None
    prev_chunk_rate = None
    buff_lens = [env.get_buffer_size()]
    ttds = []

    for i in range(vid.num_max_chunks()):
        feedback = {
            "chunk_index": i,
            "rebuffer_sec": rebuf_sec,
            "download_rate_kbps": prev_chunk_rate,
            "buffer_sec": env.get_buffer_size()
        }

        bitrateQualities = abr_alg.next_quality(**feedback)
        
        if not args.rt:
            ttd, rebuf_sec, smooth_pen, prev_chunk_rate = env.step(bitrateQualities)
        else:
            orig_ttd, orig_quality, orig_rebuf_sec, orig_chunk_size_bytes, orig_download_rate = env.rt_step(bitrateQualities)
            rt_feedback = {
                "chunk_index": i,
                # Use rebuffering from prev download not this download since a retransmit chunk 
                # isn't allowed to rebuffer
                "rebuffer_sec": rebuf_sec, 
                "download_rate_kbps": orig_download_rate,
                "buffer_sec": env.get_buffer_size(),
                "chunk_download_time": orig_ttd,
                "live_delay": env.live_delay
            }
            rt_quality = None if rebuf_sec else abr_alg.try_retransmit(**rt_feedback)
            
            ttd, rebuf_sec, smooth_pen, prev_chunk_rate = env.rt_retransmit(
                rt_quality, orig_ttd, orig_quality, orig_rebuf_sec, orig_chunk_size_bytes, orig_download_rate
            )

        if i > 0:
            total_rebuf_sec += rebuf_sec
        buff_lens.append(env.get_buffer_size())
        ttds.append(ttd)

    tot_qoe = env.get_total_qoe()
    avg_qoe = tot_qoe / vid.num_max_chunks()

    print(("Avg QoE: ", avg_qoe))
    print(("Total Rebuf (sec): ", total_rebuf_sec))
    print(("Avg Down Rate (Mbps): %.2f" % (env.get_avg_down_rate_kbps() / KILO)))

    i = 0
    for l in zip(*env.get_avg_qoe_breakdown(4)):
        print(
            (
                "%d/%d part Qoe-Qual: %.2f, rp: %.2f, sp: %.2f, total-qoe: %.2f"
                % (i, 4, l[0], l[1], l[2], l[3])
            )
        )
        i += 1

    for l in zip(*env.get_avg_qoe_breakdown(1)):
        print(
            (
                "%d/%d part Qoe-Qual: %.2f, rp: %.2f, sp: %.2f, total-qoe: %.2f"
                % (0, 1, l[0], l[1], l[2], l[3])
            )
        )

    # print('Avg network throughput (Mbps): %.2f'% network.avg_throughput_Mbps_time(args.mm_trace, vid.num_max_chunks()* 4.0))
    if args.results_dir is not None:
        utils.mkdir_if_not_exists(args.results_dir)
        env.log_qoe(os.path.join(args.results_dir, "qoe.txt"))

    with open(os.path.join(args.results_dir, "results.json"), "w") as f:
        (qual,), (rp,), (sp,), (qoe,) = env.get_avg_qoe_breakdown(1)
        json.dump(
            dict(
                avg_quality_score=qual,
                avg_rebuf_penalty=rp,
                avg_smoothness_penalty=sp,
                avg_net_qoe=qoe,
            ),
            f,
            indent=4,
            sort_keys=True,
        )
    generate_plts(
        args.results_dir,
        env.get_bitrates(),
        env.get_qoes(),
        buff_lens,
        ttds,
        args.mm_trace,
        args.mm_start_idx,
    )


if __name__ == "__main__":
    # main()
    app.run(main)
