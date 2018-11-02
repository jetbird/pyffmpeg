import logging
import sys
import os
import pdb
from ffmpeg import BaseFFMpeg, BasicFFMpegParser
from ffprobe import BasicFFProbe
from base import FFMpegAlreadyExistsError, FFMpegError
# from base import ConversionFailedError, FFMpegAlreadyExistsError, \
#    DamagedVideoError, EncodingFailedError, CompressionFailedError


# exception to be raised when invalid duration
# for a video file or audio file is being specified
class InvalidDurationSpecification(Exception):
    def __init__(self, msg, duration):
        super(InvalidDurationSpecification, self).__init__(msg)
        self.msg = msg
        self.duration = duration

    def __repr__(self):
        return '%s:%s' % (self.msg, self.duration)

    def __str__(self):
        return self.__repr__()


# the following class object deals with encoding errors,
# should we write a default error message to this class?
class EncoderSelectionFailed(Exception):

    def __init__(self, msg, encoder, media_format):
        super(EncoderSelectionFailed, self).__init__(msg)
        self.msg = msg
        self.encoder = encoder
        self.media_format = media_format

    def __repr__(self):
        return '%s for %s' % (self.msg, self.encoder)

    def __str__(self):
        return self.__repr__()  # __str__ goal is to be readable
        # return 'test'


class VideoCutFailed(Exception):
    pass


# should we have specific base parsers?
class VideoFFMpegParser(BasicFFMpegParser):
    # list of errors which are specific
    # for the VideoFFMpeg, error_class is the error
    # which is going to be raised and arguments are going
    # to be passed in the __init__ of the error class
    errors = [FFMpegError('Automatic encoder selection failed',
                          EncoderSelectionFailed,
                          [r'(codec)\s([\w]+)', r'(format)\s([\w]+)']
                          ),
              FFMpegError('InvalidDurationSpecification', InvalidDurationSpecification,
                          [r'\d\d:\d\d:\d\d:\d\d'])

              ]
    #errors = [{'name': 'Automatic encoder selection failed',
    #           'error_class': EncoderSelectionFailed,
    #           'arguments': [r'(codec)\s([\w]+)', r'(format)\s([\w]+)']},
    #          {'name': 'Invalid duration specification',
    #           'error_class': InvalidDurationSpecification,
    #           'arguments': [r'\d\d:\d\d:\d\d:\d\d', ]}
    #          ]


class VideoFFMpeg(BaseFFMpeg):
    # global class variables which
    # help to list codecs and libraries
    # that are created for dealing with
    # video data, used in the ffmpeg framework.
    parser = VideoFFMpegParser  # specific parser to use
    codec_type = 'video'
    lib_type = 'video'

    # TODO
    def convert_video(self, video_input, video_output,
                      overwrite=False, vcodec=None,
                      acodec=None):
        """
        Method which can be used to convert a video
        from one format to another, keeps the original
        video file and creates a new one in the new format.
        :param video_input: the input to be converted.
        :param_type: str, .e.g. video.mp4
        :param video_output: the output to come out
        :param_type: str, .e.g. video.avi
        :param overwrite: tell to overwrite or not
        :param_type: Bool
        :param vcodec: the video codec to use
        :param_type: str, .e.g. -vcodec h264
        :param acodec: the audio codec to use
        :param_type: str, .e.g. -acodec aac
        :return: ?
        """
        # check if video_output already exists or not, if it exists
        # then raise FFMpegAlreadyExistsError to inform the user
        if os.path.exists(video_output):
            if not overwrite:
                raise FFMpegAlreadyExistsError(video_output)  # raise error
            # in here send input commands to ffmpeg to tell it that we want
            # to overwrite the file since overwrite=True

        # what are we going to return in here?
        # define commands for the ffmpeg operation
        _cmds = ['-i', video_input, video_output]

        if vcodec is not None:
            _cmds.append(vcodec)

        if acodec is not None:
            _cmds.append(acodec)

        p = self._spawn(_cmds)  # spawn child process
        # pdb.set_trace()
        _parser = self.parser(p)  # p goes in __init__
        _parser.parse_output()  # parses each line

        return _parser.status_finished  # status of process

    def extract_audio(self, video_input):
        """Method to extract the audio stream
        from a video file, copies the audio stream
        without re-encoding it.
        :param video_input: the input to extract from
        :param_type: str, .e.g. video.avi
        """
        # if video_input does not exist, inform the user
        # and return None, stop processing in ffmpeg something
        # which does not exist
        if not os.path.exists(video_input):
            print('Make sure video exists')
            return None

        # FIXME we need a way to generate the extension of the
        # audio stream, so we can copy without re-encoding it
        # so we need to determine the extension of the audio
        # stream with the help of the ?
        info = BasicFFProbe().probe(video_input)  # probe the video
        for stream in info.streams:
            if stream._codec_info['codec_type'] == 'audio':
                extension = stream._codec_info['codec_name']

        output_audio = '.'.join(['external_audio', extension])

        if os.path.exists(output_audio):
            raise FFMpegAlreadyExistsError(output_audio)

        _cmds = ['-i', video_input, '-vn', '-acodec', 'copy',
                 output_audio]
        p = self._spawn(_cmds)  # spawns a child process
        _parser = self.parser(p)  # child process is passed to the __init__
        _parser.parse_output()  # method to parse output in the parser

        return _parser.status_finished  # return the status of the parser

    def extract_video(self, video_input):
        """Method to extract the video stream
        from a video file, copies without re-encoding
        it.
        param video_input: the input to extract from
        param_type: str, .e.g. 'video.mp4'
        """
        #  if video_input does not exist, inform the user
        #  and return None, stop processing in ffmpeg
        #  something which does not exist
        if not os.path.exists(video_input):
            print('Make sure videos exists')
            return None  # return None if video does not exist

        # determine the extension of the video stream through
        # the ffmpeg.base.MediaInfo.format_info by using the
        # probe utility being found in the BasicFFProbe class

        info = BasicFFProbe().probe(video_input)  # ffmpeg.base.MediaInfo object
        extension = info.format_info['format_name']  # get the extension
        if ',' in extension:  # matroska, webm;
            extension = extension.split(',')[1]
        # pdb.set_trace()
        output_video = '.'.join(['video_stream', extension])  # video file to output
        _cmds = ['-i', video_input, '-an', '-vcodec', 'copy', output_video]  # ffmpeg commands to execute
        p = self._spawn(_cmds)  # spawn the child process
        _parser = self.parser(p)  # activate the parser
        _parser.parse_output()  # parse the output

        return _parser.status_finished  # return status

    def remove_audio(self):
        """Method to remove the
        audio stream from a video."""
        _cmds = []
        p = self._spawn(_cmds)
        _parser = self.parser(p)
        _parser.parse_output()

        return _parser.status_finished

    def add_logo(self):
        """Method which can be used
        to add a logo to a video"""
        _cmds = []
        p = self._spawn(_cmds)
        _parser = self.parser(p)
        _parser.parse_output()

        return _parser.status_finished

    def cut_video(self, video_input, video_output,
                  start_cut, end_cut=None):
        """Method to cut a delta from
        a video.
        param video_input: the video to cut from
        param_type: str, .e.g. 'video.mp4'
        param video_output: the video to output
        param_type: str, .e.g. 'video_cut.mp4'
        param start_cut: the point to start the cut
        param_type: str, .e.g. '%H:%M:%S'
        param end_cut: the point to end the cut
        param_type: str, .e.g. '%H:%M:%S'
        """
        # the end_cut is by default equal to None,
        # if not provided by the user, the program
        # will automatically cut the video from the
        # starting point to the end of it
        if not os.path.exists(video_input):  # check for video_input path
            print('Make sure video exists')
            return None

        if os.path.exists(video_output):
            raise FFMpegAlreadyExistsError(video_output)

        # end_cut is None by default, if it is let so
        # then set end_cut to the entire length of the
        # video with the following if conditional
        if end_cut is None:
            # setup end_cut to the end length of the video
            info = BasicFFProbe().probe('test.mp4')
            end_cut = str(info.get_media_duration())

        # build the commands for cutting the video
        _cmds = ['-i', video_input, '-ss', start_cut, '-to',
                 end_cut, '-c', 'copy', video_output]
        p = self._spawn(_cmds)  # spawn the child process
        _parser = self.parser(p)  # activate the parser
        _parser.parse_output()  # parse the output

        return _parser.status_finished  # return the status

    def extract_image(self, video_input, start_point,
                      extract_all=False):
        """Method to extract image or
        images from a video file"""
        _cmds = ['-i', video_input, '-ss', start_point,
                 '-vframes', '1', 'output.png']  # list of ffmpeg commands
        p = self._spawn(_cmds)  # spawn the child process
        _parser = self.parser(p)  # activate the parser
        _parser.parse_output()  # parse the output

        return _parser.status_finished  # return the status

    # FIXME does not work at all
    def add_audio(self, video_input, audio_input,
                  video_output):
        """Method to add audio stream
        to a video, it just copies the stream
        without re-encoding.
        param video_input: the video to add the audio to
        param type: str, e.g. video.mp4
        param audio_input: the audio to add to the video
        param type: str, e.g. audio.mp3
        param video_output: e.g. the video to output
        param type: str, e.g. output.mp4
        """
        # define the ffmpeg commands to add audio stream
        _cmds = ['-i', video_input, '-i', audio_input, '-c',
                 'copy', '-map', '0:v' '-map' '1:a', video_output]
        p = self._spawn(_cmds)  # spawn the child process
        _parser = self.parser(p)  # activate the parser
        _parser.parse_output()  # parse the ffmpeg output

        return _parser.status_finished  # return the status

    def extract_subtitles(self):
        """Method to extract the subtitles
        from a video file."""
        _cmds = []
        p = self._spawn(_cmds)  # spawn the child process
        _parser = self.parser(p)  # activate the parser
        _parser.parse_output()  # parse the ffmpeg output

        return _parser.status_finished


class BasicVideoFFMpegEdit(BaseFFMpeg):
    """Subclass which deals with basic
    editing of the video"""

    def crop_video(self):
        """Method which is used to
        crop a video"""
        _cmds = []
        p = self._spawn(_cmds)
        _parser = self.parser(p)

        return _parser.parse_output()

    def rotate_video(self):
        """Method which is used to
        rotate video"""
        _cmds = []
        p = self._spawn(_cmds)
        _parser = self.parser(p)

        return _parser.parse_output()

    def blur_video(self):
        _cmds = []
        p = self._spawn(_cmds)
        _parser = self.parser(p)

        return _parser.parse_output()

    def resize_video(self):
        _cmds = []
        p = self._spawn(_cmds)
        _parser = self.parser(p)

        return _parser.parse_output()

    def scale_video(self):
        _cmds = []
        p = self._spawn(_cmds)
        _parser = self.parser(p)

        return _parser.parse_output()


class BasicVideoEncoder(BaseFFMpeg):
    """Class which deals with encoding
    videos"""
    pass


class BasicVideoCompresser(BaseFFMpeg):
    """Class which deals with compressing
    videos"""
    pass


class BasicVideoSubtitle(BaseFFMpeg):
    """Class which deals with subtitles
    in a  video"""
    pass
