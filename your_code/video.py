"""
Loads in the video data from the video trace file.
"""

import os, math
import numpy as np
import logging

logger = logging.getLogger(__name__)

BITS_IN_A_BYTE = 8.0
KILO = 1000.0
MILLISEC_IN_SEC = 1000.0


# Holds the trace for a video, as read from the given trace file, along with all
# the relevant specs. All the video-specific data should be stored in this
# object. Since all clients share this object, no per-client state should be maintained here
# The video will 'play' until the length is reached. In other words, it will
# return valid chunk sizes until ix > length, looping back to the start of the video if
# required.
class Video(object):
    def __init__(self, video_trace):
        logger.info("=========CREATING VIDEO OBJECT=========")
        logger.info(f"Loaded video trace data from file: {video_trace}")
        if not os.path.exists(video_trace):
            raise Exception("Video trace does not exist")
        f = open(video_trace)
        sizeline = f.readline().strip().split()
        self.chunk_length_ms = int(sizeline[1])
        # List of available bitrates from low to high, in Kbps
        self.bitrates = [
            float(x.replace("k", "")) for x in f.readline().strip().split()[1:]
        ]
        logger.info(f"Got bitrates {self.bitrates}")
        # Make sure this list is sorted in ascending order.
        assert sorted(self.bitrates) == self.bitrates
        self.chunks = []
        for line in f.read().splitlines():
            brs = [float(x) for x in line.strip().split()]
            # But store them in ascending order to match bitrates, and convert
            # them to Mb instead of Bytes.
            self.chunks.append([8.0 * b / 1000.0 / 1000.0 for b in sorted(brs)])

        self.max_video_chunks = len(self.chunks)
        logger.info(f"Chunks loaded from file, got {self.max_video_chunks} chunks in the video")
        logger.info("=========VIDEO OBJECT CREATED=========")

    # Scales the video length up or down by 'repeat_factor'. The video will
    # return valid chunk sizes drawn from the trace in a loop until this length
    # is reached.
    def set_max_chunks(self, n):
        if n >= 0:
            self.max_video_chunks = n

    # The length of the original video barring relooping
    def num_chunks(self):
        return len(self.chunks)

    def num_max_chunks(self):
        return self.max_video_chunks

    # Returns a list of available bitrates (in Kbps).
    def get_bitrates(self):
        return self.bitrates

    # Given a quality from 0 to len(self.bitrates) - 1, returns the corresponding
    # bitrate in Kbps.
    def quality_to_bitrate(self, quality):
        return self.bitrates[quality]

    # Returns the duration of each video chunk, in seconds.
    def get_chunk_duration(self):
        return self.chunk_length_ms / 1000.0

    def num_bitrates(self):
        return len(self.bitrates)

    def get_all_chunk_sizes(self):
        lchunks = len(self.chunks)
        chunk_sizes = []
        i = 0
        while len(chunk_sizes) < len(self.chunks):
            chunk_sizes.append(self.chunks[i % len(self.chunks)])
            i += 1
        return chunk_sizes

    # Return the bitrates for chunk i (0-indexed), in an array of descending
    # bitrates. Sizes are in Mb.
    def get_chunk_sizes(self, i):
        if i >= self.max_video_chunks:
            return []
        return self.chunks[i % len(self.chunks)]

    def size_for_bitrate(self, ix, br):
        j = self.bitrates.index(br)
        return self.get_chunk_sizes(ix)[j]

    # Return the bitrates for chunk i (0-indexed), in an array of descending
    # bitrates. A chunk may be requested for a
    # chunk size is measured in bits
    def sizes_for_chunk(self, i):
        if i >= self.max_video_chunks:
            return []
        return self.chunks[i % len(self.chunks)]

    def chunk_size_for_quality(self, ix, quality):
        if ix < 0 or ix >= self.max_video_chunks:
            print(("index is %d and max chunks are %d" % (ix, self.max_video_chunks)))
            assert False
            return 0
        szs = self.sizes_for_chunk(ix)
        return szs[quality]
