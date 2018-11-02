"""Holds important utils which
will be used for the ffmpeg package"""
import time


# codec objects in a list

# util to convert time to '%H:%M:%S'
# format using the time.strftime func
def sec_to_time_format(seconds):
    if type(seconds) is not float:
        seconds = float(seconds)
    time_obj = time.strftime('%H:%M:%S',
                             time.gmtime(seconds))

    return time_obj


# finds a codec by name in a list
def find_codec(codec_name, codecs=[]):
    # codecs = [] is the list with codecs
    # which is built by list_codecs method
    # of the Base of the entire project
    for codec in codecs:
        if codec_name == codec.codec_name:
            return codec

    return None
