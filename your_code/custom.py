import numpy as np
import argparse
parser = argparse.ArgumentParser()
# TODO: Add the required command line arguments to your abr algorithm here.
# See below for an example
parser.add_argument('--past_n_throughput_vals', type=float, default=5)


class CustomAlg:
  def __init__(self, vid, obj, cmdline_args):
    # Use parameters from self.args to define your abr algorithm.
    self.vid = vid # type: video.Video
    self.obj = obj # type: objective.Objective
    self.args = parser.parse_args(cmdline_args)

    self._prev_download_rates = []
    self._past_n_throughput_vals = self.args.past_n_throughput_vals


  def next_transmit(self, chunk_index, rebuffer_sec, download_rate_kbps,
             buffer_sec) -> (list, list):
    """
    Estimates the current network conditions and determines the optimal chunks and their respective bitrates 
    for transmission in the next step of streaming.

    Args:
      chunk_index (int): The index of the first chunk that is yet to be fetched, starting at 0.
      rebuffer_sec (float): The number of seconds spent rebuffering immediately before the previously watched chunk.
      download_rate_kbps (float): The average download rate (in kbps) of the previous transmition
      buffer_sec (float): The size of the client's playback buffer (in seconds)
      
    Returns:
      tuple: A tuple containing two lists: the indices of chunks to be transmitted next, and their corresponding bitrates.

    Note:
      Please note that for the first chunk when there is no network feedback yet
      some of the above arguments take the following default values
      chunk_index = 0
      rebuffer_sec = None
      download_rate_kbps = None
      buffer_sec = 0
    """
    return [], []
