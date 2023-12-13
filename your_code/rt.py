import numpy as np
from your_code.tb import AbrAlg

MEGA = 1e6
BITS_IN_BYTE = 8
MTU = 1500.
MILLI = 1e-3
KILO = 1e3

class AbrAlg(AbrAlg):
    # vid is of type video.Video
    # obj is of type objective.Objective
    def __init__(self, vid, obj, cmdline_args):
        # Use parameters from self.args to define your abr algorithm.
        super().__init__(vid, obj, cmdline_args)

    def next_quality(self, chunk_index, rebuffer_sec, download_rate_kbps, buffer_sec):
        """
        Args:
            chunk_index (int): The index of the first chunk that is yet to be fetched, starting at 0.
            rebuffer_sec (float): The number of seconds spent rebuffering immediately before the previously watched chunk.
            download_rate_kbps (float): The average download rate (in kbps) of the previous transmition
            buffer_sec (float): The size of the client's playback buffer (in seconds)

        Returns:
            int: An int of the quality that the chunk_index should be downloaded at.

        Note:
            Please note that for the first chunk when there is no network feedback yet
            some of the above arguments take the following default values
            chunk_index = 0
            rebuffer_sec = None
            download_rate_kbps = None
            buffer_sec = 0
        """
        return super().next_quality(chunk_index, rebuffer_sec, download_rate_kbps, buffer_sec)
    
    def try_retransmit(self, chunk_index, sent_quality, rebuffer_sec, download_rate_kbps, buffer_sec, chunk_download_time, live_delay):
        """
        Called after the initially decided bitrate for a chunk is downloaded to see if a higher bitrate
        should be retransmited for that chunk instead.
        Only called if the original download didn't rebuffer.

        Args:
            chunk_index (int)
            rebuffer_sec (float): The number of seconds spent rebuffering immediately before the previously watched chunk.
            download_rate_kbps (float): The average download rate (in kbps) of the previous transmition
            buffer_sec (float)
            
            chunk_download_time(float): The number of seconds spent downloading the original chunk
            live_delay(float): The number of seconds behind live the video is

        Returns:
            int or None: None if no chunk should be retransmitted or, otherwise, the quality to retransmit
        """
        
        new_quality = max(self.next_quality(chunk_index, rebuffer_sec, download_rate_kbps, buffer_sec))
        
        if new_quality <= sent_quality:
            return None
        
        chunk_size = self.vid.chunk_size_for_quality(chunk_index, new_quality)  # in Mb
        chunk_size_bytes = chunk_size * MEGA / BITS_IN_BYTE
        estimate_ttd = chunk_size_bytes / download_rate_kbps * BITS_IN_BYTE / KILO
        if buffer_sec > 1.5 * estimate_ttd:
            return new_quality

        return None
