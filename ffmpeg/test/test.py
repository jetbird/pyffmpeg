import os
import unittest
import sys

# the following line is needed for
# going to the root of the project
sys.path.append('../')

# import from the ffmpeg module after we have appended
# ../ to the sys.path list
from ffmpeg import FFMpeg, VideoFFMpeg, AudioAlreadyExistsError, \
    FFMpegAlreadyExistsError
from ffmpeg import BaseFFMpeg
from subprocess import Popen, PIPE


class BaseFFMpegTest(unittest.TestCase):

    def setUp(self):
        self.bf = BaseFFMpeg()

    def test_ffmpeg_executable_exists(self):
        # bf = BaseFFMpeg()
        version = '3.2 Copyright (c)'

        self.assertIn(version, self.bf.version)

    def test_version_works(self):
        version = self.bf.version
        self.assertEqual(version,
                         '3.2 Copyright (c) 2000-2016 the FFmpeg developers')

    # test methods shared by all tools, e.g
    # common methods shared by ffmpeg, ffprobe
    def test_colors(self):
        first_el = self.bf.colors[0]['Blue']
        self.assertEqual(first_el, '#0000ff')
        # self.assertEqual({}, self.bf._colors)

    def test_filters(self):
        pass

    def test_encoders(self):
        pass

    def test_decoders(self):
        pass

    def test_layouts(self):
        pass

    def test_codecs(self):
        codecs = self.bf.codecs
        # self.assertIs(codecs, [])
        # self.assertIsInstance(codecs, [])
        self.assertEqual(414, len(codecs))

    def test_devices(self):
        devices = self.bf.devices
        device = devices[0]

        self.assertEqual(len(devices), 2)
        self.assertEqual(device.device_name, 'avfoundation')
        self.assertTrue(device.demuxing)
        self.assertFalse(device.muxing)

    def test_muxers(self):
        pass


class FFMpegTests(unittest.TestCase):

    def test_ffmpeg_binary_paths(self):
        f = FFMpeg()
        self.assertIsNotNone(f.ffmpeg_path)
        self.assertIsNotNone(f.ffprobe_path)

    def test_check_ffmpeg_status(self):
        pass

    def test_ffmpeg_live_output(self):
        f = FFMpeg()
        p = Popen('ffmpeg', stderr=PIPE, stdin=PIPE,
                  stdout=PIPE)
        generator = f._ffmpeg_live_output(p)
        for line in generator:
            first_line = line
            break

        self.assertIn('ffmpeg version 3.2', first_line)

    def test_ffmpeg_probe(self):
        # instantiate the FFMpeg object
        f = FFMpeg()
        self.assertEqual(f.probe('nonexistent'), None)
        self.assertEqual(f.probe(''), None)
        info = f.probe('test.mp4')
        format_info = info.format_info
        streams = info.streams
        self.assertEqual(len(streams), 2)
        self.assertEqual(format_info.get('nb_streams'), '2')
        self.assertEqual(format_info.get('nb_programs'), '0')
        self.assertEqual(format_info.get('bit_rate'), '1452696')
        self.assertAlmostEqual(float(format_info.get('duration')), 293.63,
                               places=0)

        # get the video stream and create tests for it
        v_stream = streams[0]
        self.assertEqual(v_stream.height, '720')
        self.assertEqual(v_stream.width, '1280')
        self.assertEqual(v_stream.codec.codec_type, 'video')
        self.assertEqual(v_stream.codec.codec_name, 'h264')
        self.assertEqual(v_stream.codec.codec_tag_string, 'avc1')
        self.assertEqual(v_stream.codec.codec_tag, '0x31637661')

        # get the audio stream and create tests for it
        a_stream = streams[1]
        self.assertEqual(a_stream.height, None)
        self.assertEqual(a_stream.width, None)
        self.assertAlmostEqual(float(a_stream.duration), 293.63,
                               places=0)
        self.assertEqual(a_stream.codec.codec_long_name,
                         'AAC (Advanced Audio Coding)')
        self.assertEqual(a_stream.codec.codec_name, 'aac')
        self.assertEqual(a_stream.codec.codec_type, 'audio')
        self.assertEqual(a_stream.codec.codec_tag_string, 'mp4a')
        self.assertEqual(a_stream.codec.codec_tag, '0x6134706d')
 
    def test_get_extension(self):
        f = FFMpeg()
        audio_extension = f._get_extension('test.aac', 'audio')
        mp3_extension = f._get_extension('test.mp3', 'audio')
        video_extension = f._get_extension('test.mp4', 'video')
        avi_extension = f._get_extension('test.avi', 'video')

        self.assertEqual(audio_extension, 'aac')
        self.assertEqual(mp3_extension, 'mp3')
        self.assertEqual(video_extension, 'mp4')
        self.assertEqual(avi_extension, 'avi')

    def test_get_media_type(self):
        # instantiate the class
        f = FFMpeg()
        self.assertEqual(f.get_media_type('test.mp4'), {'audio': True,
                                                        'video': True})
        self.assertEqual(f.get_media_type('test.aac'), {'audio': True})
        self.assertEqual(f.get_media_type('noaudio.mp4'), {'video': True})

    def test_list_codecs(self):
        f = FFMpeg()
        codecs = f.list_codecs()
        codec = codecs[0]
        _codec = {'012v':
                  {'codec_type': 'video',
                   'decoding': True,
                   'description': 'Uncompressed 4:2:2 10-bit',
                   'intraframe_only': True
                   }
                  }
        self.assertIsInstance(codecs, list)
        self.assertIsInstance(codec, dict)
        self.assertEqual(414, len(codecs))
        self.assertDictEqual(codec, _codec)

    def test_parse_codec_line(self):
        f = FFMpeg()
        features, codec_name, desc = ['DES...', 'xsub',
                                      'XSUB']
        codec = f._parse_codec_line(features, codec_name,
                                    desc)
        _codec = {'xsub':
                  {'encoding': True,
                   'codec_type': 'subtitle',
                   'description': 'XSUB',
                   'decoding': True
                   }
                  }
        self.assertIsInstance(codec, dict)
        self.assertDictEqual(codec, _codec)


class VideoFFMpegTests(unittest.TestCase):

    def test_ffmpeg_already_exists_error(self):
        # test if FFMpegAlreadyExistsError exception
        # is thrown when file we want to produce with
        # ffmpeg already exists
        message = "File 'test.avi' already exists. Overwrite ? [y/N]"
        v = VideoFFMpeg(verbose=False)
        try:
            v.convert_video('test.mp4', 'test.avi')
        except FFMpegAlreadyExistsError:
            e = sys.exc_info()[1]
            self.assertEqual(e.message, message)
        else:
            self.fail('Exception was not thrown')

    def test_convert_video_success(self):
        v = VideoFFMpeg(verbose=False)
        status = v.convert_video('test.mp4', 'test.flv')
        if os.path.exists('test.flv'):
            os.unlink('test.flv')

        self.assertTrue(status)

    def test_cut_video(self):
        pass

    def test_extract_image(self):
        pass

    def test_extract_images(self):
        pass

    def test_extract_audio(self):
        pass

    def test_extract_video(self):
        pass

    def test_resize_video(self):
        pass

    def test_compress_video(self):
        pass

    def test_encode_video(self):
        pass

    def test_generate_video_with_thumb(self):
        pass

    def test_add_audio_to_video(self):
        # test if method can add an audio stream
        # to a video file which does not have one
        f = FFMpeg(verbose=False)
        v = VideoFFMpeg(verbose=False)
        v.add_audio_to_video('noaudio.mp4', 'gotaudio.mp4',
                             'test.aac')
        # get the second stream
        stream = f.probe('gotaudio.mp4').streams[1]

        self.assertEqual(stream.codec.codec_type, 'audio')

        # unlink the output video file
        if os.path.exists('gotaudio.mp4'):
            os.unlink('gotaudio.mp4')

    def test_add_audio_already_exists(self):
        v = VideoFFMpeg(verbose=False)
        # test.mp4 already has an audio stream
        # check if AudioAlreadyExists error is being
        # raised when trying to add audio stream to a
        # video file which already has one
        try:
            v.add_audio_to_video('test.mp4', 'testwithaudio.mp4',
                                 'test.aac')
        except AudioAlreadyExistsError:
            e = sys.exc_info()[1]
            self.assertEqual(e.message, 'Audio stream exists')
        else:
            self.fail('Exception was not thrown')

    def test_extract_subtitles(self):
        pass


class AudioFFMpegTests(unittest.TestCase):

    def test_convert_audio(self):
        pass

    def test_cut_audio(self):
        pass

    def test_join_audio(self):
        pass

    def test_extract_lyrics(self):
        pass

    def test_encode_audio(self):
        pass


class ImageFFmpegTests(unittest.TestCase):
    pass


if __name__ == '__main__':
    unittest.main()
