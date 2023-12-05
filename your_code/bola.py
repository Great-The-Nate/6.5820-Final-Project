import numpy as np

class AbrAlg:
    def __init__(self, vid, obj, cmdline_args):
        # Existing initialization
        self.vid = vid
        self.obj = obj
        # self.args = parser.parse_args(cmdline_args)
        
        # TODO: Need to change these configurations to match the delayed setting.
        self.b_max = 40.0
        self.b1 = (90.0 / 240.0) * self.b_max # Original b_1 value.
        self.b_m = 0.9 * self.b_max

        self.num_bitrates = len(self.vid.get_bitrates())
        self.V = (self.b_max - self.b1) / max(self.vid.get_bitrates())  # BOLA parameter V

    def utility_function(self, quality_index, buffer_sec, rebuffer_sec):
        # Quality score - higher for higher bitrates. You can adjust the coefficients.
        quality_score = self.vid.get_bitrates()[quality_index] / 1000  # Assuming bitrate is in kbps

        # Buffer score - higher when buffer is closer to the optimal level.
        buffer_optimal = 0.5 * (self.b1 + self.b_m)  # Midpoint of optimal buffer range
        buffer_score = -abs(buffer_sec - buffer_optimal)  # Negative of the absolute difference from optimal

        # Rebuffering penalty - reduces the utility score if there has been recent rebuffering.
        rebuffering_penalty = 0 if rebuffer_sec is None else -rebuffer_sec * 10  # Penalty coefficient can be adjusted

        # Total utility is a combination of these factors.
        total_utility = quality_score + buffer_score + rebuffering_penalty
        return total_utility

    def next_quality(self, chunk_index, rebuffer_sec, download_rate_kbps, buffer_sec):
        """
        Buffer based algorithm that looks at the buffer occupancy and picks another quality aside from the base quality.

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
        # Calculate utility for each bitrate and choose the one with the highest utility.
        utilities = [(self.utility_function(i, buffer_sec, rebuffer_sec) + self.V * self.vid.get_bitrates()[i]) / (self.vid.get_bitrates()[i] + 1) for i in range(self.num_bitrates)]
        return list(set([0, int(np.argmax(utilities))]))