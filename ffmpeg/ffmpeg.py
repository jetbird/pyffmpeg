from base import Base, BasicParser


class BasicFFMpegParser(BasicParser):
    parse_exec = 'ffmpeg'


class BaseFFMpeg(Base):
    """Class to act as a base for
    ffmpeg with general methods that
    are required by other subclasses"""
    parser = BasicFFMpegParser
    codec_type = None
    lib_type = None
    exec_name = 'ffmpeg'

    # TODO create a represenation method for dev
    # thing is that we can do in base subclass
    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__,
                           self.executable)

    def list_codecs(self):
        """Method to list codecs supported
        by the ffmpeg multimedia framework"""
        # list all codecs
        if self.codec_type is None:
            return None

        return True

    def list_libraries(self):
        """Lists all the libraries
        with wich ffmpeg has been build
        with"""
        if self.lib_type is None:
            return None

        return True
