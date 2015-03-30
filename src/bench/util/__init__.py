import errno
import os

def mkdir_p (path):
    try:
        os.makedirs(path)
    except OSError as ex:
        if ex.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def chunks(l, n):
    """ Yield successive n-sized chunks from l.
    """
    l = list(l)
    for i in xrange(0, len(l), n):
        yield l[i:i+n]
