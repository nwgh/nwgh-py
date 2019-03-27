import fcntl
import inspect
import os
import resource
import signal
import sys


def warn(msg):
    """Print a warning message.

    Arguments:
        msg: <string> message to print
    """
    sys.stderr.write('%s\n' % (msg,))


def die(msg, code=1):
    """Print a warning message and exit abnormally.

    Arguments:
        msg: <string> message to print
        code: <int, optional> code to exit with
    """
    warn(msg)
    sys.exit(code)


def main(_main):
    """Decorator to mark a function as the main function for a program.
    """
    parent = inspect.stack()[1][0]
    name = parent.f_locals.get('__name__', None)
    if name == '__main__':
        rval = 1

        try:
            rval = _main(sys.argv[1:])
        except Exception as e:
            warn(str(e))

        sys.exit(rval)
    return _main


class cwd(object):
    """A context manager to change our working directory when we enter the
    context, and then change back to the original working directory when we
    exit the context
    """
    def __init__(self, dirname):
        self.newcwd = dirname
        self.oldcwd = os.getcwd()
        #logging.debug('creating cwd object with newcwd %s and oldcwd %s' %
        #              (self.newcwd, self.oldcwd))

    def __enter__(self):
        #logging.debug('changing cwd to %s' % (self.newcwd,))
        os.chdir(self.newcwd)

    def __exit__(self, *args):
        #logging.debug('returning cwd to %s' % (self.oldcwd,))
        os.chdir(self.oldcwd)


def daemon_sig(pidfile):
    """Signal handler for daemons created with daemonize.
    """
    #logging.debug('signal handler: unlinking pidfile')
    os.unlink(pidfile)
    #logging.debug('signal handler: daemon exiting')
    sys.exit(0)


def daemonize(pidfile, function, **kwargs):
    """Run a function as a daemon.

    pidfile - Name of file to write PID to
    function - Function object to call as the daemon
    kwargs - Arguments to pass to <function>
    """

    #logging.debug('forking for daemonization')
    pid = os.fork()

    if pid < 0:
        # Fork failure
        #logging.error('fork failed (%s)' % (os.strerror(pid,)))
        sys.exit(1)

    if pid:
        # Parent
        sys.exit(0)

    sid = os.setsid()
    if sid == -1:
        # Error setting session ID
        #logging.error('error setting sid')
        sys.exit(1)

    devnull = getattr(os, 'devnull', '/dev/null')
    #logging.debug('devnull = %s' % (devnull,))

    log_fds = set()
    #logger = logging.getLogger()
    #for handler in logger.handlers:
        #if isinstance(handler, logging.FileHandler):
            #log_fds.add(handler.stream.fileno())
    #logging.debug('log fds = %s' % (log_fds,))

    for fd in range(resource.getrlimit(resource.RLIMIT_NOFILE)[0]):
        if fd in log_fds:
            #logging.debug('not closing fd %s (log)' % (fd,))
            pass
        else:
            try:
                os.close(fd)
                #logging.debug('closed fd %s' % (fd,))
            except OSError:
                # Didn't have it open, don't care
                pass

    # Make stdin, stdout & stderr point to /dev/null
    #logging.debug('pointing std{in,out,err} -> devnull')
    os.open(devnull, os.O_RDWR)
    os.dup(0)
    os.dup(0)

    # Set a sane umask
    #logging.debug('setting umask 022')
    os.umask(0o22)

    # Change to the usual daemon directory
    #logging.debug('chdir -> /')
    os.chdir('/')

    with open(pidfile, 'w') as f:
        #logging.debug('locking %s' % (pidfile,))
        fcntl.lockf(f, fcntl.LOCK_EX | fcntl.LOCK_NB)

        #logging.debug('writing pid')
        f.write('%s' % (os.getpid(),))
        f.flush()

        #logging.debug('setting up sigterm handler')
        signal.signal(signal.SIGTERM, lambda sig, frame: daemon_sig(pidfile))

        #logging.debug('calling daemon function')
        function(**kwargs)

        # If we get here, we assume the program is exiting cleanly
        #logging.debug('unlinking pidfile')
        os.unlink(pidfile)
        #logging.debug('daemon exiting')
        sys.exit(0)
