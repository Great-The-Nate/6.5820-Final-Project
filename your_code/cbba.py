class AbrAlg:
    # vid is of type video.Video
    # obj is of type objective.Objective
    def __init__(self, vid, obj, cmdline_args):
        # Use parameters from self.args to define your abr algorithm.
        self.vid = vid
        self.obj = obj
        # self.args = parser.parse_args(cmdline_args)

        self.b_max = cmdline_args.live_delay + vid.get_chunk_duration()
        self.b1 = 0.05 * self.b_max  # In the paper the b_1 was set 90s with 240s buffer capacity.
        self.b_m = 0.40 * self.b_max

        self.num_bitrates = len(self.vid.get_bitrates())

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
        qualities = []
        if buffer_sec < self.b1:  # reservoir
            qualities.append(0)
        elif buffer_sec > self.b_m:  # upper reservoir
            qualities.append(self.num_bitrates - 1)
        else:  # cushion
            qualities.append(
                round((buffer_sec - self.b1) / (self.b_max - self.b1) * (self.num_bitrates - 1))
            )

        return qualities