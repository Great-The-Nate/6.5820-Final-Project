# A class that expresses the main QoE metric that your ABR algorithm will be
# evaluated on. An instance of this class will be passed into your AbrAlg
# constructor. You may call any of its functions at any point.
import json
import os
import logging

logger = logging.getLogger(__name__)

class Objective:
    """
    Params:
        - `perceptual_qualities` is a dictionary mapping bitrate (kbps) to
        perceptual quality (on a scale of 0 - 100.
        - `startup_penalty` is the penalty for each second spent waiting for the
        first chunk to buffer.
        - `rebuffer_penalty` is the penalty for each second spent rebuffering after
        the first chunk.
        - `smoothness` is the penalty for changes in bitrate.

    Note: All penalties are non-negative floating point numbers.
    """

    def __init__(
        self,
        perceptual_qualities: dict[int, float],
        startup_penalty: float,
        rebuffer_penalty: float,
        smoothness_penalty: float,
    ):
        self._perceptual_qualities = perceptual_qualities
        self._startup_penalty = startup_penalty
        self._rebuffer_penalty = rebuffer_penalty
        self._smoothness_penalty = smoothness_penalty

        # Load the SSIM QOE metric from the JSON file
        with open(os.path.join("real", "data", "raw-ssim-scores.json"), "r") as f:
            self._chunk_ssim_by_bitrate = json.load(f)

    def __get_ssim_from_chunk(self, bitrate, chunk_idx) -> float:
        # Convert decimal bitrate to key in the JSON
        bitrate_key = f"{round(bitrate)}k"
        chunk_idx_key = str(chunk_idx)
        try:
            return self._chunk_ssim_by_bitrate[bitrate_key][chunk_idx_key]
        except KeyError:            
            logger.error(f"Could not find ssim from bitrate {bitrate_key} and chunk idx {chunk_idx_key}")
            return 0
            
    def perceptual_qualities(self):
        return self._perceptual_qualities

    def startup_penalty(self):
        return self._startup_penalty

    def rebuf_penalty(self):
        return self._rebuffer_penalty

    def smooth_penalty(self):
        return self._smoothness_penalty

    def qoe(self, cur_bitrate, prev_bitrate, rebuf_sec, chunk_idx):
        """Computes the QoE for any chunk (except the first).

        Params:
            - `cur_bitrate`: the bitrate of that chunk
            - `prev_bitrate`: the bitrate of the previous chunk
            - `rebuf_sec`: the number of seconds spent waiting for this chunk to
                rebuffer. Note that rebuffering penalties are assigned to the
                chunk immediately following a rebuffering event.
            - `chunk_idx`: The current chunk index
        """
        pq_cur = self._perceptual_qualities[cur_bitrate]
        pq_prev = self._perceptual_qualities[prev_bitrate]
        return (
            pq_cur
            - self._rebuffer_penalty * rebuf_sec
            - self._smoothness_penalty * abs(pq_prev - pq_cur)
        )

    def detailed_qoe(self, cur_bitrate, prev_bitrate, rebuf_sec, chunk_idx):
        """Returns the different components of the QoE in a tuple."""
        pq_cur = self._perceptual_qualities[cur_bitrate]
        pq_prev = self._perceptual_qualities[prev_bitrate]
        rp = self._rebuffer_penalty * rebuf_sec
        sp = self._smoothness_penalty * (abs(pq_prev - pq_cur))
        qoe = pq_cur - rp - sp
        ssim_cur = self.__get_ssim_from_chunk(cur_bitrate, chunk_idx)

        return pq_cur, -rp, -sp, qoe, ssim_cur

    def qoe_first_chunk(self, cur_bitrate, delay_sec):
        """Computes the QoE for the first chunk in a video.

        Params:
            - `cur_bitrate`: the bitrate of the first chunk
            - `delay_sec`: The number of seconds it took to fetch the first
              chunk and start playing the video.
        """
        pq_cur = self._perceptual_qualities[cur_bitrate]
        return pq_cur - self._startup_penalty * delay_sec

    def detailed_qoe_first_chunk(self, cur_bitrate, delay_sec):
        pq_cur = self._perceptual_qualities[cur_bitrate]
        rp = self._startup_penalty * delay_sec
        qoe = pq_cur - rp
        ssim = self.__get_ssim_from_chunk(cur_bitrate, 0)
        return pq_cur, -rp, 0, qoe, ssim
