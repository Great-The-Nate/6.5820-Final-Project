import numpy as np
import json
import os
import sys
import argparse
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
sys.path.append('./')
import utils

parser = argparse.ArgumentParser()
parser.add_argument('--no_title', action='store_true')
parser.add_argument('--abr', type=str, help='abr algorithm for title')
parser.add_argument('--runs', required=True, nargs='+', type=str)
parser.add_argument('--results_dir', type=str, default='results/')
args = parser.parse_args()

OUT_DIR = 'cdfs'


def plot_cdf(ax, vals, label=''):
  x = sorted(vals)
  y = [i / float(len(vals)) for i in range(len(vals))]
  ax.plot(x, y, label=label + '(Mean: %.2f)' % np.mean(x))
  ax.legend()


def main():
  runs = sorted(args.runs)
  for mode in ['train', 'test']:
    f, axarr = plt.subplots(2, 1)
    for run in runs:
      rebufs, smooths, qualities, qoes, ssims = [], [], [], [], []
      d = os.path.join(args.results_dir, run, mode)
      for fname in os.listdir(d):
        with open(os.path.join(d, fname, 'results.json')) as f:
          j = json.load(f)
        rebufs.append(j['avg_rebuf_penalty'])
        smooths.append(j['avg_smoothness_penalty'])
        qualities.append(j['avg_quality_score'])
        qoes.append(j['avg_net_qoe'])
        ssims.append(j['avg_ssim'])

      plot_cdf(axarr[0], rebufs, label=run)
      axarr[0].set_xlabel('Rebuffer penalty')
      if args.no_title:
        pass   
      elif args.abr:
        axarr[0].title.set_text(f"Single Bitrate vs. Multiple Bitrates using {args.abr} Algorithm")
      else:
        axarr[0].title.set_text("SSIM and Rebuffer Penalty by Single or Multiple Bitrates")
      plot_cdf(axarr[1], ssims, label=run)
      axarr[1].set_xlabel('Average SSIM')

    plt.tight_layout()
    utils.mkdir_if_not_exists(os.path.join(OUT_DIR, '_'.join(runs)))
    plt.savefig(os.path.join(OUT_DIR, '_'.join(runs), '%s.png' % mode))


if __name__ == '__main__':
  main()
