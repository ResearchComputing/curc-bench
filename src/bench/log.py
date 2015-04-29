import logging
import os


package_name = __name__.split('.')[0]
package_logger = logging.getLogger(package_name)


def configure_package_logger(level=logging.DEBUG):
    package_logger.setLevel(level)


def configure_stderr_logging(level=logging.WARNING):
    formatter = logging.Formatter(': '.join((package_name, '%(message)s')))
    handler = logging.StreamHandler()
    handler.setLevel(level)
    handler.setFormatter(formatter)
    package_logger.addHandler(handler)


def configure_file_logging(directory):
    formatter = logging.Formatter(
        '%(asctime)s %(levelname)s %(message)s',
        datefmt='%b %d %H:%M:%S')
    handler = logging.FileHandler(os.path.join(directory, 'bench.log'))
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(formatter)
    package_logger.addHandler(handler)
