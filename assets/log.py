import logging
import os
from itertools import islice
import sys
from citrus_config import LOG_LEVEL, LOG_FILE


class CSVLogger(object):  # pragma: no cover
    def __init__(self, name, log_file=LOG_FILE, level=LOG_LEVEL, provider='undefined'):
        # create logger on the current module and set its level
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        self.logger.setLevel(getattr(logging, level.upper()))
        self.needs_header = True
        self.provider = provider

        # create a formatter that creates a single line of json with a comma at the end
        self.formatter = logging.Formatter(
            (
                '%(name)s,%(funcName)s,"%(asctime)s",%(provider)s,%(levelname)s,"%(message)s"'
            )
        )

        self.log_file = log_file
        if self.log_file:
            # create a channel for handling the logger (stderr) and set its format
            ch = logging.FileHandler(log_file)
        else:
            # create a channel for handling the logger (stderr) and set its format
            ch = logging.StreamHandler()
        ch.setFormatter(self.formatter)

        # connect the logger to the channel
        self.logger.addHandler(ch)

    def log(self, msg, level='info'):
        HEADER = 'module,function,datetime,provider,level,msg\n'
        if self.needs_header:
            if self.log_file and os.path.isfile(self.log_file):
                with open(self.log_file) as file_obj:
                    if len(list(islice(file_obj, 2))) > 0:
                        self.needs_header = False
                if self.needs_header:
                    with open(self.log_file, 'a') as file_obj:
                        file_obj.write(HEADER)
            else:
                if self.needs_header:
                    sys.stderr.write(HEADER)
            self.needs_header = False
        provider = self.provider
        extra = {
            'provider': provider
        }
        func = getattr(self.logger, level)
        func(msg, extra=extra)

    def debug(self, msg):
        return CSVLogger.log(self, msg, level='debug')

    def info(self, msg):
        return CSVLogger.log(self, msg, level='info')

    def warning(self, msg):
        return CSVLogger.log(self, msg, level='warning')

    def error(self, msg):
        return CSVLogger.log(self, msg, level='error')

    def critical(self, msg):
        return CSVLogger.log(self, msg, level='critical')
