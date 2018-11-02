"""Base classes and functions for
the ffmpeg package"""
import pdb
import re
import os
import sys
import re
from subprocess import Popen, PIPE
from utils import find_codec


# general error class to be used to catch specific
# errors in lines produced by tools of the ffmpeg
# tools; error.error_class(*arguments) will be
# thrown. in the following __init__ constructor,
# arguments is going to be a list which stores
# specific regular expressions
class FFMpegError(object):
    def __init__(self, name, error_class, arguments):
        self.name = name
        self.error_class = error_class
        self.arguments = arguments

    #  returns a Bool, True or False?
    def error_matches(self, line):
        return line.startswith(self.name)


# the following deals with encoding errors
class EncoderSelectionFailed(Exception):

    def __init__(self, msg, encoder, media_format):
        super(EncoderSelectionFailed, self).__init__(msg)
        self.msg = msg
        self.encoder = encoder
        self.media_format = media_format

    def __repr__(self):
        return '%s' % self.msg

    def __str__(self):
        return self.__repr__()


class Video(object):  # maybe we don't need it

    def __init__(self, width, height, quality):
        self.codec = None
        self.width = width
        self.height = height
        self.quality = quality


# the following class is going to
# be used inside MediaInfo, an object
# which is being utilized by the
# ffmpeg.ffprobe.BasicFFProbeParser
class FormatInfo(object):

    def __init__(self):
        self.nb_streams = None
        self.start_time = None
        self.format_long_name = None
        self.format_name = None
        self.filename = None

    # we set the attributes declared inside
    # the __init__ constructor through the parsing
    # method which is defined below; key, value approach
    def parse_format(self, key, value):
        if hasattr(self, key):
            setattr(self, key, value)  # attr based on key, value


# the following is a custom base class which can
# be used to create skeleton of an internal structure
# that we are going to utilize to store stream data
class StreamInfo(object):

    # the constructor of the class, __init__
    def __init__(self):
        """Stores data of a stream returned by ffprobe
        utility of the ffmpeg framework into an internal
        structure. This class will be used in MediaInfo
        to build the stream objects."""
        self.has_b_frames = None
        self.duration_ts = None
        self.duration = None  # duration in seconds
        self.creation_time = None  # when is stream created?
        self.nb_frames = None  # frames in stream
        self.index = None  # each stream has its index
        self._codec_info = {}  # store codec info from stream
        self._codec = None  # each stream has a codec

    def parse_stream(self, key, value):
        """Method which parses the stream based on raw
        live output returned by ffprobe utility."""
        codec_keys = ['codec_name', 'codec_tag', 'codec_long_name',
                      'codec_type', 'codec_time', 'codec_tag_string']
        if hasattr(self, key):
            setattr(self, key, value)
        elif key in codec_keys:
            self._codec_info[key] = value

    # each stream has a codec
    @property  # build Codec object
    def codec(self):  # build it from list_codecs?
        if self._codec is None:
            # list codecs
            # set self._codec by looking in codecs returned
            # by list_codecs
            _codec_name = self._codec_info.get('codec_name')
        # for now just return the name of the codec

        return _codec_name

    def __repr__(self):
        return 'Stream %s' % self.codec

    def __str__(self):
        return self.__repr__()


# specific class for the audio streams
class AudioStream(StreamInfo):
    pass


# specific class for the video streams
class VideoStream(StreamInfo):
    pass


class MediaInfo(object):
    """Base class which stores information
    about a media file such as streams,
    media duration etc; parses the output
    returned by the ffprobe utility into internal
    structures, respectively FormatInfo and StreamInfo."""

    def __init__(self):  # __init__ constructor of class
        self.current_stream = None  # stream reading on or off?
        self.current_format = None  # format reading on or off?
        self.format_info = None  # ffmpeg.base.FormatInfo
        # self.format_info = FormatInfo()  # move it inside parse_ffprobe
        self.streams = []  # store media streams as StreamInfo objects
        # self.format_info = {}  # store FORMAT info

    def parse_ffprobe(self, line):
        line = line.strip()  # remove special characters
        if line == '[STREAM]':
            # set self.parse_stream to True
            # build a stream object?
            self.current_stream = StreamInfo()
        if line == '[/STREAM]':
            # set self.parse_stream to False ?
            self.streams.append(self.current_stream)
            self.current_stream = None  # reset self.current_stream to None

        if line == '[FORMAT]':  # start of format info
            self.current_format = FormatInfo()

        if line == '[/FORMAT]':  # end of format data
            self.format_info = self.current_format
            self.current_format = None

        if '=' in line:
            k, v = line.split('=')
            k = k.strip()
            v = v.strip()
            if self.current_stream:
                self.current_stream.parse_stream(k, v)
            elif self.current_format:
                # self.format_info[k] = v
                self.current_format.parse_format(k, v)

    def get_media_duration(self):
        duration = self.format_info['duration']

        return duration

    def get_media_title(self):
        pass

    def get_media_size(self):
        pass

    def get_media_encoding(self):
        pass

    def get_media_format(self):
        pass

    def get_creation_time(self):
        """Gets the date and time in which the
        media file was created. Returns a datetime
        object"""
        pass


# define the instance factories for
# ffmpeg objects such as filters, encoders,
# decoders, subtitles,
class Filter(object):
    pass


class Decoder(object):
    decoder_attr = []

    def __init__(self):
        pass

    def parse_decoder(self):
        pass


class Device(object):
    """Class which is going to provide
    behavior for ffmpeg devices"""

    def __init__(self):
        self._demuxing = False
        self._muxing = False
        self.device_info = {}
        self.device_name = None
        self.device_desc = None

    def parse_device(self, features, name, desc):
        device_map = {
            'D': {'demuxing': True},
            'E': {'muxing': True}
        }
        for el in features:
            device_data = device_map.get(el)
            if device_data is not None:
                self.device_info.update(device_data)

        # set name and desc for the device
        self.device_name = name
        self.device_desc = desc

        return self.device_info

    @property
    def demuxing(self):
        if not self._demuxing:
            if self.device_info.get('demuxing'):
                self._demuxing = True

        return self._demuxing

    @property
    def muxing(self):
        if not self._muxing:
            if self.device_info.get('muxing'):
                self._muxing = True


class Codec(object):  # Codec instance factory
    # codec.codec_type returns a dict
    # codec.decoding = True or False?
    # codec.name --> xsub

    # init is the first method which is executed in the
    # initialization of the object
    def __init__(self):
        self._codec_type = {}  # audio, video, subtitle
        self._codec_info = {}
        self._video_support = False
        self._audio_support = False
        self._subtitle_support = False
        self._encoding_support = False
        self._decoding_support = False
        self._intraframe_only = False
        self._compression_type = None  # lossy or lossless
        self.codec_name = None  # e.g., xsub
        self.codec_desc = None  # a longer description of codec

        # should we execute parse_codec here

    def __repr__(self):
        """Returns a representation of the
        codec object which helps the developer
        understand the nature of Codec objects."""
        return "%s(%s)" % (self.__class__.__name__,
                           self.codec_name)

    def __str__(self):
        """Returns a representation of the codec object
        which helps the end user to get information on the
        codec object"""
        return "Codec %s;%s" % (self.codec_name, self.codec_desc)

    # method which is used to parse the Codec object
    # from the codec line which comes from ffmpeg output
    # that is read by reading subprocess.Popen process
    def parse_codec(self, features, codec_name,
                    codec_desc):
        # features is a string, e.g., D.V.L.
        # codec_name is a string, e.g., 4xm
        # codec_desc is another string, e.g.,
        # in this case it is 4X Movie
        codec_type_map = {
            'A': 'audio',
            'V': 'video',
            'S': 'subtitle'
        }
        codec_map = {
            'D': {'decoding': True},
            'E': {'encoding': True},
            'I': {'intraframe_only': True},
            'L': {'lossless': True},
            'S': {'lossy': True},
        }
        # features is a string like '..V...' or a string
        # like ..S..S which means subtitle codec support and
        # lossless compression support
        for el in features:
            if features.index(el) == 2:
                # set self._codec_type in here
                self._codec_type = codec_type_map.get(el)
                continue
            codec_map_el = codec_map.get(el)
            if codec_map_el is not None:
                self._codec_info.update(codec_map_el)
        # return some dict in here

        # the following sets up the name of the codec
        # instance and also the description of the codec
        self.codec_name = codec_name
        self.codec_desc = codec_desc
        # self._codec_type = codec_type

        return self._codec_info

    @property
    def audio_support(self):
        """Method which finds out
        if the codec supports audio
        stream or not"""
        # check the codec_type dict, if 'audio' is not
        if not self._audio_support:
            if self._codec_type == 'audio':
                self._audio_support = True

        return self._audio_support

    @property
    def video_support(self):
        if not self._video_support:
            if self._codec_type == 'video':
                # set self._video_support to True
                self._video_support = True

        return self._video_support

    @property
    def subtitle_support(self):
        """Finds out if codec supports subtitles
        or not."""
        if not self._subtitle_support:
            if self._codec_type == 'subtitle':
                # set self._subtitle_support to True
                self._subtitle_support = True

        return self._subtitle_support

    @property
    def compression_type(self):
        """Finds out the compression type of
        codec, is it lossy or lossless."""
        pass

    @property
    def decoding_support(self):
        if not self._decoding_support:
            if self._codec_info.get('decoding') is not None:
                self._decoding_support = True

        return self._decoding_support

    @property
    def encoding_support(self):
        if not self._encoding_support:
            if self._codec_info.get('encoding') is not None:
                self._encoding_support = True

        return self._encoding_support

    @property
    def intraframe_only(self):
        if not self._intraframe_only:
            if self._codec_info.get('intraframe_only') is not None:
                self._intraframe_only = True

        return self._intraframe_only


class Subtitle(object):
    subtitle_attr = []

    def __init__(self):
        pass

    def parse_subtitle(self):
        pass


class Encoder(object):
    encoder_attr = []

    def __init__(self):
        pass

    def parse_encoder(self):
        pass


# the following class should be used to raise
# an error when looking for an executable which
# is missing; a binary build that doesn't exist
class ExecutableDoesNotExistError(Exception):
    # what kind of executable are we looking for?
    # for example, ffmpeg, ffprobe, ffplay etc.
    def __init__(self, message):
        self.message = message

    # method which is used to represent the
    # object, it is designed for the developer.
    def __repr__(self):
        return 'Executable %s does not exist' % \
               self.message

    # method which is used by the print statement
    # to print a string representation of object, it
    # is primarily designed for the end user, this method
    # is used by python when error is being raised
    def __str__(self):
        return self.__repr__()


# base class for raising an error when a
# file already exists
class FFMpegAlreadyExistsError(Exception):

    def __init__(self, message):
        self.message = message

    # this method is for developers, it helps
    # the developer in creating a printable
    # representation of the object
    def __repr__(self):
        return 'File (%s) already exists' % self.message

    # this magic method is for end users, it is used
    # by the str() builtin and print statement to get
    # the string representation of an object
    def __str__(self):
        return self.__repr__()


# we need a parser in this base module
# which is going to deal with parsing
# output returned from the opened child
# process such as subprocess.Popen object
class BasicParser(object):
    """Class to parse live output
    which comes from the opened child
    process with subprocess.Popen, based
    on this basic parser we are going to
    build all the specific parsers for
    ffprobe, ffmpeg and other utilities."""
    errors = []  # default list of errors to catch and throw
    parse_exec = None  # overridden in a subclass

    #  takes a child subprocess in the __init__,
    #  subprocess.Popen object should be passed
    def __init__(self, child_p):
        # child_p is needed for reading the data
        # which we going to parse from.
        # execute the main parse method in here?
        self.child_p = child_p  # instance var
        self.stdout_read = False  # normal output goes
        # self.parse_output()     # to stdout
        self.status_finished = None  # child process status

    # the following method reads output from the opened
    # subprocess which is passed in the __init__; reads
    # output from self.child_p, a subprocess.Popen object
    # FIXME find a better way to check the status of child_p
    def get_live_output(self):
        """Get live output from the opened
        subprocess.Popen object, reads chunk by chunk."""
        line = ''  # an empty line of ffmpeg output .e.g.
        new_lines = ['\n', '\r\n', '\r']  # help to find the end of line
        # base parsing is going to be the same
        # for any kind of executable, read data
        # chunk by chunk, append it to line, yield line,
        # reset line and so on until the whole data is read

        # the following while loop generates a python generator
        # it helps to read the ffmpeg output in live mode
        while True:  # we need a while True condition in here
            # when there is predicted that there is no error
            # in the output, it is redirected to stdout
            # instead of stderr where live ffmpeg output goes
            if self.stdout_read:  # read from stdout
                chunk = self.child_p.stdout.read(1)
            else:  # read from stderr
                chunk = self.child_p.stderr.read(1)
            # pdb.set_trace()
            if chunk == '' and self.child_p.poll() is not None:
                self.status_finished = True
                break  # break the while True loop
            #  pdb.set_trace()
            line += chunk  # build the line chunk by chunk
            if chunk in new_lines:  # line finished, yield line
                yield line  # generate a line
                line = ''  # reset line to empty string, start over

    def parse_output(self):  # parses live output, checks for errors
        # depending on the output of which tool
        # we are parsing we need to return the
        # specific objects, e.g MediaInfo objects
        # for the output which comes from ffprobe
        # parse_output at the moment just prints to
        # stdout raw output, does not process it at all
        arguments = []  # store arguments for the error class

        for line in self.get_live_output():  # iterate through live output
            #  pdb.set_trace()
            print(line)  # prints line on console
            # pdb.set_trace()
            for error in self.errors:  # iterate errors of the specific parser
                if error.error_matches(line):  # if error matches, process it
                    arguments.append(error.name)  # append the name argument
                    # TODO get the args from the line with a regex
                    # arguments = ['Failed to select codec', 'h264', 'mp4']
                    # _arguments = error.arguments
                    for argument in error.arguments:
                        match_obj = re.search(argument, line)
                        if match_obj is not None:
                            arguments.append(match_obj.group())
                    # pdb.set_trace()
                    raise error.error_class(*arguments)  # raise the error in here

        #  should we catch and raise the ffmpeg errors in here?
        #  if line.startswith('Automatic encoder selection failed'):
        #        raise EncoderSelectionFailed('Encoder selection failed', 'h264', 'mp4')

    def parse_filters(self):
        pass

    def parse_blocks(self, sep=None, sep_by=2,
                     unproc_lines=10):
        """Method which can be used to parse
        blocks separated by space, builds and
        return an object of type list out of them"""
        # the dictionary which is going to be returned
        # is a nested dictionary
        # S..... ssa Windows Media Audio 2
        line_counter = 0
        blocks = []
        # read live output and parse the one which
        # we need for our project
        for line in self.get_live_output():
            line_counter += 1
            # pdb.set_trace()
            if line_counter <= unproc_lines:
                continue  # continue to the next iteration
            data = line.split(sep, sep_by)  # returns list
            blocks.append(data)

        return blocks

    def parse_version(self):
        # should we make it private?
        """Method which is used to parse the version
        of ffmpeg, ffprobe, ffplay and other executables
        part of the ffmpeg multimedia framework."""
        _line = ''
        # read the live output in here
        # line is the string to be matched,
        for line in self.get_live_output():
            _line = line  # read the first line
            break         # there is version stored
        pattern = r'%s version (.*)' % self.parse_exec
        match_obj = re.match(pattern, _line, flags=0)
        if match_obj:
            return match_obj.group(1)

    def basic_regex_parsing(self, pattern):
        # this method can be used to parse
        # a specific part in a string, for
        # example version of the exe tool
        # pattern to match in the string
        _line = ''
        for line in self.get_live_output():
            _line = line
            break
        match_obj = re.compile(pattern, _line)
        if match_obj:
            return match_obj.group()


class Base(object):
    """Class which is the base engine
    of the entire project, deals with
    opening child processes, finding the
    executables, cross platform support,
    parsing the data which is read from
    output returned to stderr , stdout"""
    # the binary build to look for in PATH
    # environmental variable, global class
    # variable to be override by subclass
    exec_name = None  # exec_name = 'ffmpeg'
    parser = None  # class object to parse data

    def __init__(self, executable=None,
                 verbose=True):
        """
        :param executable: executable provided
        by the user in the specific subclass.
        :param_type: str: e.g. ffmpeg
        :param verbose: boolean to decide
        if output should be printed in stdout or
        not.
        :param_type: Bool: e.g. verbose=True
        """
        # executable = /usr/local/bin/ffmpeg or
        # e.g. C:\Program Files\ffmpeg\bin\ffmpeg.exe
        # and C:\Program Files\ffmpeg\bin\ffprobe.exe
        # verbose = False, stops printing on console

        self._filters = []
        self._encoders = []
        self._decoders = []
        self._muxers = []
        self._devices = []  # list to store Device obj
        self._codecs = []  # list to store Codec obj
        self._version = None  # version of exec
        self._colors = []  # colors supported by ffmpeg
        self._layouts = {}  # layouts supported by ffmpeg
        # if verbose is set to true, print to stdout
        self.verbose = verbose  # we need to keep state
        self.cmds = []  # list to store default commands
        split_by = ':'  # default split for unix PATH
        # if system runs windows exec_name should be
        # with .exe at the end for which(name) to locate it
        # in the PATH windows environment variable
        if os.name == 'nt':  # in Windows paths are separated
            split_by = ';'   # by a ; instead of a : like nix

        # the following function checks for an executable inside
        # the directories of the $PATH environmental variable
        def which_name(name):
            # get the PATH environment variable, which is str
            path = os.getenv('PATH', os.defpath)
            for d in path.split(split_by):
                f_path = os.path.join(d, name)
                if os.path.exists(f_path) and os.access(f_path, os.X_OK):
                    return f_path
            return None  # python None by def, makes code readable

        # if executable is not provided in __init__
        if executable is None:
            executable = self.exec_name  # set executable to global exec_name
        # pdb.set_trace()

        # this condition returns always True? shitty hack?
        # if the path stored in executable is not a unix or a windows path
        # then we make use of which_name tool to automatically look for the
        # path of the executable within the deafult PATH of the current os
        if '/' not in executable and '\\' not in executable:  # \\ windows path
            executable = which_name(self.exec_name) or executable

        # pdb.set_trace()
        self.executable = executable  # setup the executable as instance var
        # pdb.set_trace()
        self.cmds = [self.executable, ]  # why keep track of cmds here?

        # what arguments should the following class call take,
        # self and message; we raise an ExecutableDoesNotExistError in here
        # to inform the user that the executable is not available in the os
        if not os.path.exists(self.executable):
            raise ExecutableDoesNotExistError(self.executable)

    # private method to spawn a child process, we need
    # this method to spawn the specific processes in the
    # subclasses such as VideoFFMpeg, AudioFFMpeg etc. The
    # following method is private because it is not meant to
    # be utilized directly from the user; but by the tools of the
    # project.
    def _spawn(self, cmds=[]):  # returns a subprocess.Popen obj
        # we better run _base_cmds here in order
        # to add the base commands to the arguments
        cmds = self._base_cmds(cmds)  # returns a list obj
        # pdb.set_trace()
        # then we open a subprocess.Popen object with
        # the help of the Python's builtin subprocess
        # module, being found in the standard library
        try:
            p = Popen(cmds, stderr=PIPE, stdin=PIPE,
                      stdout=PIPE, close_fds=True)
            return p  # return the child process for the self.parser
        except OSError:
            e = sys.exc_info()[1]
            print(e)

    # we need this to build commands list so we don't
    # build them inside the methods of the wrapper
    def _base_cmds(self, cmds=[]):
        # why should we store cmds in a private
        # method?
        _cmds = [self.executable, ]  # self.cmds?
        """
        Private method to build the base
        commands needed for spawning the process.
        :param cmds: list to store commands
        :param_type: list
        :return:
        """
        # for the moment it is just ['/usr/local/bin/ffmpeg']
        if len(cmds):
            _cmds.extend(cmds)  # extend to the default cmds

        return _cmds

    @staticmethod
    def _live_output(open_p):
        """Method to read live output
        from the opened subprocess and
        yield it; python generator."""
        line = ''  # create an empty line
        # define new line chars to find end
        # of line so we can reset line variable
        # and yield the line for print to stdout
        new_lines = ['\n', '\r\n', '\r']  # end of line
        while True:
            # read data chunk by chunk from stderr
            chunk = open_p.stderr.read(1)
            # if there is no chunk to read and
            # open_p.poll() is not None then yield True
            # and break the while loop, finished.
            # shitty hack to find out if reading data is
            # finished, look for a more cool way to do it.
            if chunk == '' and open_p.poll() is not None:
                yield 'True'  # finished reading data
                break

            # populate the line with chunks and
            # yield it
            line += chunk
            if chunk in new_lines:
                yield line
                line = ''  # set line to empty

    def _check_status(self, open_p):
        """Method to check status of a child
        process, is it finished or not, and
        give the specific response based on the
        data read in the open_p object. """
        pattern = r'File (.*) already exists'
        for line in self._live_output(open_p):
            if self.verbose:
                print(line)

            # if File already exists in line raise
            # FFMpegAlreadyExistsError,implement it by
            # using the regular expressions module.
            if re.match(pattern, line, flags=0):
                raise FFMpegAlreadyExistsError(line)

            if 'True' in line:
                return True

# shared options among the ff* tools
    @property
    def version(self):
        """Method to show version of the program
        executable in use."""
        if self._version is None:
            child_p = self._spawn()  # spawn process
            # pdb.set_trace()
            # parsing should be done in self.parser object
            _parser = self.parser(child_p)
            # pdb.set_trace()
            version = _parser.parse_version()
            # change the state of the _version
            self._version = version

        return self._version  # return object._version

    @property  # TODO
    def filters(self):
        """Method which is used to list
        filters in ffmpeg multimedia
        framework"""
        cmds = ['-filters']
        child_p = self._spawn(cmds)
        _parser = self.parser(child_p)
        _parser.stdout_read = True
        _parser.parse_output()

    @property  # TODO
    def encoders(self):
        cmds = ['-encoders']
        child_p = self._spawn(cmds)
        _parser = self.parser(child_p)
        _parser.stdout_read = True
        _parser.parse_output()

    @property  # TODO
    def decoders(self):
        cmds = ['-decoders']
        child_p = self._spawn(cmds)
        _parser = self.parser(child_p)
        _parser.stdout_read = True
        _parser.parse_output()

    @property  # TODO
    def layouts(self):  # special parsing
        if not len(self._layouts):
            cmds = ['-layouts']
            child_p = self._spawn(cmds)
            _parser = self.parser(child_p)
            _parser.stdout_read = True
            _parser.parse_output()

        # return self._layouts

    # FIXME return a list with dicts [{'Blue': '0000ff'}]
    @property  # FIXME output goes to stdout
    def colors(self):
        """Method which is used to list
        all the colors available in the
        ffmpeg multimedia framework."""
        # {'AliceBlue': 'f0f8ff'}
        if not len(self._colors):
            cmds = ['-colors']
            child_p = self._spawn(cmds)
            _parser = self.parser(child_p)
            _parser.stdout_read = True
            # pdb.set_trace()
            for color in _parser.parse_blocks():
                color_dict = {color[0]: color[1]}
                self._colors.append(color_dict)
        # we need to return colors in some
        # dictionary in here self._colors
        return self._colors

    @property
    def codecs(self):
        unproc_lines = 10  # ignore the first 10 lines
        if not len(self._codecs):
            cmds = ['-codecs']  # spawn a process
            child_p = self._spawn(cmds)
            _parser = self.parser(child_p)
            _parser.stdout_read = True
            for block in _parser.parse_blocks(
                    sep_by=2,
                    unproc_lines=unproc_lines):
                # pdb.set_trace()
                features, codec_name, desc = block
                codec = Codec()
                codec.parse_codec(
                    features, codec_name, desc
                    )
                self._codecs.append(codec)

        return self._codecs

    @property  # TODO
    def devices(self):
        unproc_lines = 4  # lines to be skipped
        if not len(self._devices):
            cmds = ['-devices']
            child_p = self._spawn(cmds)  # spawns child process
            _parser = self.parser(child_p)
            _parser.stdout_read = True  # output goes to stdout
            for block in _parser.parse_blocks(
                    sep_by=2,
                    unproc_lines=unproc_lines):
                features, device_name, desc = block
                device = Device()
                device.parse_device(features, device_name, desc)

                self._devices.append(device)  # add Device obj to list

        return self._devices  # return the devices in the list

    @property  # TODO
    def muxers(self):
        cmds = ['-muxers']
        child_p = self._spawn(cmds)
        _parser = self.parser(child_p)
        _parser.stdout_read = True
        _parser.parse_output()
