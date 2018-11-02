"""Wrapper for the ffprobe utility"""
from base import Base, BasicParser, MediaInfo


class FFprobeParser(BasicParser):
    parse_exec = 'ffprobe'

    def parse_ffprobe(self):
        # parsing of ffprobe -show_streams -show_format
        # should happen in here, that's why we have the
        # parser in here
        self.stdout_read = True  # output goes to stdout
        media_info = MediaInfo()  # ffmpeg.base.MediaInfo
        for line in self.get_live_output():
            media_info.parse_ffprobe(line)

        return media_info


class BasicFFProbe(Base):
    """Class to package the ffprobe
    utilities; can spawn a child process
    since it inherits from Base"""
    parser = FFprobeParser  # parser of child processes
    exec_name = 'ffprobe'  # why do we need this?

    def probe(self, video_input):
        """Method to probe media with
        the help of the ffprobe tool
        which comes with ffmpeg framework"""
        _cmds = ['-show_format', '-show_streams',
                 video_input]
        p = self._spawn(_cmds)  # create child process
        codecs = self.codecs  # ?
        _parser = self.parser(p)  # self.parser = FFprobeParser
        info = _parser.parse_ffprobe()  # ffmpeg.base.MediaInfo

        return info  # return ffmpeg.base.MediaInfo obj to caller

    def test_func(self):
        pass

    def show_devices(self):
        pass

    def show_codecs(self):
        """Method which helps to show
        the available codecs in ffmpeg"""
        pass

    def show_decoders(self):
        """Method which helps to show the
        available decoders in the ffmpeg"""
        pass

    def show_encoders(self):
        """Method which helps to show the
        encoders in the ffmpeg framework"""
        pass

    def show_protocols(self):
        pass

    def show_sample_formats(self):
        pass

    def show_bitstream_filters(self):
        pass
