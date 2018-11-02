"""module to deal with videos that have subtitles
"""


class Subtitle(object):
    def __init__(self, subtitle=None):
        """
        class which creates and modifies
        subtitles.
        """
        self.subtitle = subtitle
        if not self.subtitle:
            self.parse_subtitles()

    def convert_subtitle(self):
        pass

    def parse_subtitles(self):
        pass


class BaseSubtitle(object):
    pass
