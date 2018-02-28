"""util.py

Champlain College CSI-235, Spring 2018
The following code was adapted by Joshua Auerbach (jauerbach@champlain.edu)
from the UC Berkeley Pacman Projects (see license and attribution below).

----------------------
Licensing Information:  You are free to use or extend these projects for
educational purposes provided that (1) you do not distribute or publish
solutions, (2) you retain this notice, and (3) you provide clear
attribution to UC Berkeley, including a link to http://ai.berkeley.edu.

Attribution Information: The Pacman AI projects were developed at UC Berkeley.
The core projects and autograders were primarily created by John DeNero
(denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
Student side autograding was added by Brad Miller, Nick Hay, and
Pieter Abbeel (pabbeel@cs.berkeley.edu).
"""


import sys
import inspect
import heapq
import random
import io


def raise_not_defined():
    file_name = inspect.stack()[1][1]
    line = inspect.stack()[1][2]
    method = inspect.stack()[1][3]

    print("*** Method not implemented: %s at line %s of %s" %
          (method, line, file_name))
    sys.exit(1)


def lookup(name, namespace):
    """
    Get a method or class from any imported module from its name.
    Usage: lookup(function_name, globals())
    """
    dots = name.count('.')
    if dots > 0:
        module_name, obj_name = '.'.join(
            name.split('.')[:-1]), name.split('.')[-1]
        module = __import__(module_name)
        return getattr(module, obj_name)
    else:
        modules = [obj for obj in list(namespace.values()) if str(
            type(obj)) == "<type 'module'>"]
        options = [getattr(module, name)
                   for module in modules if name in dir(module)]
        options += [obj[1]
                    for obj in list(namespace.items()) if obj[0] == name]
        if len(options) == 1:
            return options[0]
        if len(options) > 1:
            raise Exception('Name conflict for %s')
        raise Exception('%s not found as a method or class' % name)


def pause():
    """
    Pauses the output stream awaiting user feedback.
    """
    print("<Press enter/return to continue>")
    input()


# code to handle timeouts
#
# FIXME
# NOTE: TimeoutFuncton is NOT reentrant.  Later timeouts will silently
# disable earlier timeouts.  Could be solved by maintaining a global list
# of active time outs.  Currently, questions which have test cases calling
# this have all student code so wrapped.
#
import signal
import time


class TimeoutFunctionException(Exception):
    """Exception to raise on a timeout"""
    pass


class TimeoutFunction:
    def __init__(self, function, timeout):
        self.timeout = timeout
        self.function = function

    def handle_timeout(self, signum, frame):
        raise TimeoutFunctionException()

    def __call__(self, *args, **kargs):
        # If we have SIGALRM signal, use it to cause an exception if and
        # when this function runs too long.  Otherwise check the time taken
        # after the method has returned, and throw an exception then.
        if hasattr(signal, 'SIGALRM'):
            old = signal.signal(signal.SIGALRM, self.handle_timeout)
            signal.alarm(self.timeout)
            try:
                result = self.function(*args, **kargs)
            finally:
                signal.signal(signal.SIGALRM, old)
            signal.alarm(0)
        else:
            start_time = time.time()
            result = self.function(*args, **kargs)
            time_elapsed = time.time() - start_time
            if time_elapsed >= self.timeout:
                self.handle_timeout(None, None)
        return result


_ORIGINAL_STDOUT = None
_ORIGINAL_STDERR = None
_MUTED = False


class WritableNull:
    def write(self, string):
        pass


def mute_print():
    global _ORIGINAL_STDOUT, _ORIGINAL_STDERR, _MUTED
    if _MUTED:
        return
    _MUTED = True

    _ORIGINAL_STDOUT = sys.stdout
    #_ORIGINAL_STDERR = sys.stderr
    sys.stdout = WritableNull()
    #sys.stderr = WritableNull()


def unmute_print():
    global _ORIGINAL_STDOUT, _ORIGINAL_STDERR, _MUTED
    if not _MUTED:
        return
    _MUTED = False

    sys.stdout = _ORIGINAL_STDOUT
    #sys.stderr = _ORIGINAL_STDERR
