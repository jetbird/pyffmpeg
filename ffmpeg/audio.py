from ffmpeg import BaseFFMpeg


# should we have a specific base parser for audio?
class AudioFFMpegParser():
    pass


class AudioFFMpeg(BaseFFMpeg):
    lib_type = 'audio'
    codec_type = 'audio'

    def cut_audio(self, end_start):
        """Method to cut delta from
        audio files.
        """
        pass

    def convert_audio(self, audio):
        """Method which converts an
        audio file from one format
        to another"""
        pass
