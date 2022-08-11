import logging
import os
import sys

class Logger:
    def __init__(self, name=None):
        self.__logger = None
        self.__name = self.__class__.__name__
        if name:
            self.__name = name
        self.__setup_logging()

    def __remove_logger(self):
        logs = self.__logger.handlers
        for log in logs:
            self.__logger.removeHandler(log)
            log.flush()
            log.close()

    def __check_logger(self, instance):
        logs = self.__logger.handlers
        for log in logs:
            if not isinstance(log, instance):
                return True

    def __create_path(self, base_path):
        try:
            if not os.path.exists(base_path):
                os.mkdir(base_path)
        except:
            raise

    def log(self, *strings, **kwargs):
        strings = ['at {}'.format(sys._getframe(1).f_code.co_name), '-' if strings else ''] + list(strings)
        level = kwargs.pop('level', 'info').upper()
        self.__logger.log(getattr(logging, level), u' '.join(str(s) for s in strings), exc_info=(level == 'ERROR'))

    def __setup_logging(self, level='INFO'):
        level = level.upper()
        self.__logger = logging.getLogger(self.__name)
        self.__logger.propagate = False
        # self.__remove_logger()
        formatter = logging.Formatter('[%(asctime)s][%(name)s] - %(levelname)s - %(message)s', '%Y-%m-%d %H:%M:%S')

        handler_stream = logging.StreamHandler(sys.stdout)
        handler_stream.setLevel(getattr(logging, level))
        handler_stream.setFormatter(formatter)

        handler_stream_err = logging.StreamHandler()
        handler_stream_err.setLevel(logging.ERROR)
        handler_stream_err.setFormatter(formatter)

        if not self.__check_logger(logging.FileHandler):
            self.__logger.addHandler(handler_stream)
            self.__logger.addHandler(handler_stream_err)
            self.__logger.setLevel(level)
