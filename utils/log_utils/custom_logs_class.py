import os
import codecs
from datetime import datetime

from logging.handlers import TimedRotatingFileHandler


class TimelyRotatingFileHandler(TimedRotatingFileHandler):
    def __init__(self, log_title, when_to="midnight", intervals=1, *args, **kwargs):
        self.new_dir = None
        self.when = when_to.upper()
        self.inter = intervals
        self.log_file_path = os.path.join(os.getcwd(), "logs")
        if not os.path.isdir(self.log_file_path):
            os.mkdir(self.log_file_path)
        if self.when == "S":
            self.extStyle = "%Y-%m-%d: %H:%M:%S"
        if self.when == "M":
            self.extStyle = "%Y-%m-%d: %H:%M"
        if self.when == "H":
            self.extStyle = "%Y-%m-%d: %H"
        if self.when == "MIDNIGHT" or self.when == "D":
            self.extStyle = "%Y-%m-%d"

        self.dir_log = os.path.abspath(
            os.path.join(self.log_file_path, datetime.now().strftime(self.extStyle))
        )
        if not os.path.isdir(self.dir_log):
            os.mkdir(self.dir_log)
        self.title = log_title
        filename = os.path.join(self.dir_log, self.title)
        TimedRotatingFileHandler.__init__(
            self,
            filename,
            when=when_to,
            interval=self.inter,
            backupCount=kwargs.get("backupCount", 0),
            encoding=None,
        )
        self._header = ""
        self._log = None
        self._counter = 0

    def doRollover(self):
        """
        TimedRotatingFileHandler remix - rotates logs on daily basis, and filename of current logfile is time.strftime("%m%d%Y")+".txt" always
        """
        self.stream.close()
        # get the time that this sequence started at and make it a TimeTuple

        self.new_dir = os.path.abspath(
            os.path.join(self.log_file_path, datetime.now().strftime(self.extStyle))
        )

        if not os.path.isdir(self.new_dir):
            os.mkdir(self.new_dir)
        self.baseFilename = os.path.abspath(os.path.join(self.new_dir, self.title))
        if self.encoding:
            self.stream = codecs.open(self.baseFilename, "w", "utf-8")
        else:
            self.stream = open(self.baseFilename, "w")

        self.rolloverAt = self.rolloverAt + self.inter