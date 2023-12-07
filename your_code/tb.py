import numpy as np
import argparse

# parser = argparse.ArgumentParser()


class AbrAlg:
    # vid is of type video.Video
    # obj is of type objective.Objective
    def __init__(self, vid, obj, cmdline_args):
        # Use parameters from self.args to define your abr algorithm.
        self.vid = vid
        self.obj = obj
        # self.args = parser.parse_args(cmdline_args)

        self.b_max = 40.0
        self.b1 = (
            90.0 / 240.0
        ) * self.b_max  # In the paper the b_1 was set 90s with 240s buffer capacity.
        self.b_m = 0.9 * self.b_max

        self.prev_rates = []

        self.num_bitrates = len(self.vid.get_bitrates())
        
        # rebuffer aware
        self.rebuffer_react_chunks = 0

    def next_quality(self, chunk_index, rebuffer_sec, download_rate_kbps, buffer_sec):
        """
        Throughput based algorithm that estimates the current throughput and picks another quality aside from the base quality.

        Args:
            chunk_index (int): The index of the first chunk that is yet to be fetched, starting at 0.
            rebuffer_sec (float): The number of seconds spent rebuffering immediately before the previously watched chunk.
            download_rate_kbps (float): The average download rate (in kbps) of the previous transmition
            buffer_sec (float): The size of the client's playback buffer (in seconds)

        Returns:
            list: A list containing either one or two quality that the chunk_index should be downloaded at.

        Note:
            Please note that for the first chunk when there is no network feedback yet
            some of the above arguments take the following default values
            chunk_index = 0
            rebuffer_sec = None
            download_rate_kbps = None
            buffer_sec = 0
        """
        if download_rate_kbps is None:
            return [0]
        # Update previous rates
        if len(self.prev_rates) == 8:
            self.prev_rates.pop(0)
        self.prev_rates.append(download_rate_kbps)
        # quick start
        if chunk_index < 3:
            return [0]
        # throughput estimation
        harmonic_mean_rate = len(self.prev_rates) / np.sum(
            1.0 / np.array(self.prev_rates)
        )

        next_bitrate = 0
        for i, bitrate in enumerate(self.vid.get_bitrates()):
            if bitrate > harmonic_mean_rate:
                break
            next_bitrate = bitrate

        if buffer_sec < self.b1:  # reservoir
            next_bitrate = next_bitrate * 0.8
        elif buffer_sec > self.b_m:  # upper reservoir
            next_bitrate = next_bitrate * 1.2

        if rebuffer_sec is not None and rebuffer_sec > 0:
            print(f"rebuffer_sec: {rebuffer_sec}, chunk_index: {chunk_index}")
            self.rebuffer_sec = rebuffer_sec
            self.rebuffer_react_chunks = 3

        if self.rebuffer_react_chunks > 0:
            self.rebuffer_react_chunks -= 1
            if rebuffer_sec > 20:
                next_bitrate = next_bitrate * 0.6
            elif rebuffer_sec > 10:
                next_bitrate = next_bitrate * 0.7
            elif rebuffer_sec > 5:
                next_bitrate = next_bitrate * 0.8
            else:
                next_bitrate = next_bitrate * 0.9

        # quality end
        if self.vid.num_max_chunks() - chunk_index < 8 and buffer_sec > self.b_m * 1.5:
            next_bitrate = next_bitrate * 1.3

        # Find the highest bitrate less than the estimatiton
        bitrate_index = 0
        for i, bitrate in enumerate(self.vid.get_bitrates()):
            if bitrate > next_bitrate:
                break
            bitrate_index = i

        return list(set([0, bitrate_index]))
