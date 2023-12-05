import copy

import numpy as np
from network import Network

MEGA = 1e6
BITS_IN_BYTE = 8
MTU = 1500.
MILLI = 1e-3
KILO = 1e3


class ChunkStats:

  def __init__(self, idx, quality, chunk_size, rebuf_sec, ttd, qoe_qual, rp,
               sp, qoe):
    self.idx = idx
    self.quality = quality
    self.chunk_size = chunk_size
    self.rebuf_sec = rebuf_sec
    self.qoe_qual = qoe_qual
    self.rp = rp
    self.sp = sp
    self.qoe = qoe
    self.ttd = ttd

  def get_download_rate_kbps(self):
    return self.chunk_size / self.ttd * BITS_IN_BYTE / KILO


class Env:

  def __init__(self, vid, obj, net, live_delay):
    self.vid = copy.deepcopy(vid)
    self.obj = copy.deepcopy(obj)
    self.n_bitrates = vid.num_bitrates()
    self.CHUNK_DUR = vid.get_chunk_duration()
    self.net = net
    self.buffer = 0  # seconds
    self.live_delay = live_delay + self.CHUNK_DUR
    self.availableSeconds = live_delay + self.CHUNK_DUR # Number of seconds the server has ready to send

    self.vid_chunk_idx = 0
    self.total_qoe = 0
    self.prev_quality = None
    self.chunk_stats = []

  def _validate_action(self, act):
    assert isinstance(act, int)
    assert act >= 0
    assert act < len(self.vid.get_bitrates())

  def step(self, qualities):
    """The primary step function simulating video streaming."""
    # print(f"Live Delay: {self.live_delay}; Available Seconds: {self.availableSeconds}; Buffer: {self.buffer}")
    lowerQual, higherQual = min(qualities), max(qualities)
    self._validate_action(lowerQual)
    self._validate_action(higherQual)

    # Try downloading smaller bitrate first, if there's leftover time go for larger bitrate too
    smaller_chunk_size = self.vid.chunk_size_for_quality(self.vid_chunk_idx, lowerQual)  # in Mb
    smaller_chunk_size_bytes = smaller_chunk_size * MEGA / BITS_IN_BYTE

    larger_chunk_size = self.vid.chunk_size_for_quality(self.vid_chunk_idx, higherQual)  # in Mb
    larger_chunk_size_bytes = larger_chunk_size * MEGA / BITS_IN_BYTE
    
    prior_net_idx = self.net.idx
    ttd_smaller = self.net.ttd(smaller_chunk_size_bytes)
    ttd_larger = self.net.ttd(larger_chunk_size_bytes)

    # Decide to use smaller or larger bitrate based on if the larger bitrate downloads in time
    # And set/reset network index accordingly
    self.net.set_packet_idx(prior_net_idx)
    if ttd_smaller + ttd_larger < self.CHUNK_DUR:
      ttd = ttd_smaller + ttd_larger
      chunk_size_bytes = smaller_chunk_size_bytes + larger_chunk_size_bytes
      quality = higherQual
      self.net.bytes_downloadable(ttd)
    else:
      ttd = ttd_smaller
      chunk_size_bytes = smaller_chunk_size_bytes
      quality = lowerQual
      self.net.bytes_downloadable(
        max(ttd, self.CHUNK_DUR)# If we chose smaller bitrate, we still tried to download the larger one
      ) 

    if ttd == 0:
      # because of the nature of mahimahi simulation sometime we can have
      # instantaneous bursts and if abr chooses low bitrates then a chunk
      # can be downloaded in a single burst resulting in ttd = 0
      # This is rare but if it happens instead of leading to a ZeroDivisionError
      # we give a high download_rate instead.
      download_rate_kbps = 100 * 1000  # 100 Mbps
      ttd = chunk_size_bytes / download_rate_kbps * BITS_IN_BYTE / KILO
    else:
      download_rate_kbps = chunk_size_bytes / ttd * BITS_IN_BYTE / KILO

    # print("TTD:", ttd)
    rebuf_sec = max(0, ttd - self.buffer)
    self.live_delay += rebuf_sec
    self.availableSeconds += ttd - self.CHUNK_DUR
    
    self.buffer = max(0, self.buffer - ttd)
    self.buffer += self.CHUNK_DUR

    # Fast forward environment to the next time a chunk is available
    if self.availableSeconds < self.CHUNK_DUR:
      self.net.bytes_downloadable(self.CHUNK_DUR - self.availableSeconds)
      self.buffer -= (self.CHUNK_DUR - self.availableSeconds)
      self.availableSeconds = self.CHUNK_DUR
    

    if self.vid_chunk_idx == 0:
      qoe_qual, rp, sp, qoe = self.obj.detailed_qoe_first_chunk(
          self.vid.quality_to_bitrate(quality), ttd)
    else:
      qoe_qual, rp, sp, qoe = self.obj.detailed_qoe(
          self.vid.quality_to_bitrate(quality),
          self.vid.quality_to_bitrate(self.prev_quality), rebuf_sec)

    self.total_qoe += qoe
    self.prev_quality = quality

    cs = ChunkStats(self.vid_chunk_idx, quality, chunk_size_bytes, rebuf_sec,
                    ttd, qoe_qual, rp, sp, qoe)
    self.chunk_stats.append(cs)

    self.vid_chunk_idx += 1

    return ttd, rebuf_sec, sp, download_rate_kbps

  # returns in seconds
  def get_buffer_size(self):
    return self.buffer

  def get_total_qoe(self):
    return self.total_qoe

  def get_bitrates(self):
    return [self.vid.quality_to_bitrate(cs.quality) for cs in self.chunk_stats]

  def get_avg_down_rate_kbps(self):
    l = [cs.get_download_rate_kbps() for cs in self.chunk_stats]
    return np.mean(l)

  '''
      split num chunks into nparts and report avg qoe stats over each part
  '''

  def get_avg_qoe_breakdown(self, n_parts=1):
    N = len(self.chunk_stats)
    qqas, rpas, spas, qoeas = [], [], [], []
    for l in np.array_split(self.chunk_stats, n_parts):
      qoe_qual_avg = np.mean([cs.qoe_qual for cs in l])
      rp_avg = np.mean([cs.rp for cs in l])
      sp_avg = np.mean([cs.sp for cs in l])
      qoe_avg = np.mean([cs.qoe for cs in l])

      qqas.append(qoe_qual_avg)
      rpas.append(rp_avg)
      spas.append(sp_avg)
      qoeas.append(qoe_avg)

    return qqas, rpas, spas, qoeas

  def get_qoes(self):
    qoes = []
    for cs in self.chunk_stats:
      qoes.append([cs.qoe_qual, cs.rp, cs.sp, cs.qoe])
    return qoes

  def log_qoe(self, fname=None):
    ret = ''
    for qoe_qual, rp, sp, qoe in self.get_qoes():
      ret += '%f %f %f %f\n' % (qoe_qual, rp, sp, qoe)

    if fname is not None:
      with open(fname, 'w') as f:
        f.write(ret)

    return ret
  