import numpy as np

class AbrAlg:
    # vid is of type video.Video
    # obj is of type objective.Objective
    def __init__(self, vid, obj, cmdline_args):
        # Use parameters from self.args to define your abr algorithm.
        self.vid = vid
        self.obj = obj

    def next_quality(self, chunk_index, rebuffer_sec, download_rate_kbps, buffer_sec):
        """
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
        qualities = [0]

        return qualities
    
    def retransmit(self, chunk_index, rebuffer_sec, download_rate_kbps, buffer_sec):
        """
        Called after the initially decided bitrate for a chunk is downloaded to see if a higher bitrate
        should be retransmited for that chunk instead.

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
        return None
