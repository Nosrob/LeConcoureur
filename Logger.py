# coding: utf-8

import logging

class Logger(object):

    def __init__(self, name='logger', level=logging.DEBUG):
        #Creates the logger object that is used for logging in the file
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        #Create log outputs
        fh = logging.FileHandler('%s.log' % name, 'w')
        sh = logging.StreamHandler()

        #Log format
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        #Set logging format
        fh.setFormatter(formatter)
        sh.setFormatter(formatter)

        #Set level per output
        fh.setLevel(logging.DEBUG)
        sh.setLevel(logging.INFO)

        self.logger.addHandler(fh)
        self.logger.addHandler(sh)

    def debug(self, msg):
        self.logger.debug(msg)

    def info(self, msg):
        self.logger.info(msg)

    def warning(self, msg):
        self.logger.warning(msg)

    def error(self, msg):
        self.logger.error(msg)
