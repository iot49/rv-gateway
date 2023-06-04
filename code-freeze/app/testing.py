import sys, io, os
import unittest


# this won't work with freezing!

if not "tests" in sys.path:
    sys.path.append("tests")

def run_all():
    class DUP(io.IOBase):
        def __init__(self, s):
            self.s = s
        def write(self, data):
            self.s += data
            return len(data)
        def readinto(self, data):
            return 0
    
    try:
        s = bytearray()
        os.dupterm(DUP(s))
        for test in os.listdir('/tests'):
            unittest.main(module=test[:-3])
    finally:
        os.dupterm(None)
    return s.decode()
