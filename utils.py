import numpy as np
import argparse

# Unary Functions
def isqrt(x):
    try:
        return np.sqrt(x)
    except:
        return None

class Factorial(object):
    def __init__(self, n=100000):
        self._n = n
        self._table = np.cumprod([1.0] + range(1,n))
    def __call__(self, x):
        if x>=self._n or x<0 or x != int(x):
            return None
        return self._table[int(x)]

fact = Factorial()

# Binary Functions
def pw(a,b):
    try:
        return float(a)**float(b)
    except:
        return None

def rt(a,b):
    try:
        return float(a) ** float(1./b)
    except:
        return None

def div(a,b):
    return a/b if (b and a%b==0) else None

def str2bool(v):
    """
    Convert string to boolean, for argparse.
    See the source below, for details:
    https://stackoverflow.com/questions/15008758/parsing-boolean-values-with-argparse
    """
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')
