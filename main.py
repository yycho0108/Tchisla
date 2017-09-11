#!/usr/bin/python

"""
Script for Solving Tchisla,
For computing (y#x <= max_c),

Sample Usage:
    python main.py --x 5 --y 1776 --max_c 7 [--max_u 1] [--proc] [--debug] 

For more information/help:
    python main.py -h

Non-configurable Parameters:
    max_v (for v_filter)

Note that the program may not find the optimum solution.
It would terminate when any solution is found such that c<=max_c.
In addition, the search is limited to a number of constraints,
as defined by max_u and max_v (and possibly others).

Author : Yoonyoung Cho
Date Created : 09/10/2017
Date Modified : 09/10/2017
"""

import numpy as np
from collections import defaultdict
import sys
from utils import *
from threading import Thread
from multiprocessing import Pool
import argparse
import warnings
import operator
import time

def v_filter(v, max_v=1e100):
    """ Filter Values. """
    if v is None:
        return False
    try:
        # checking int-ness ...
        for i in range(1,10):
            k = v**i
            if k == int(k):
                break
        else:
            return False

        if np.isnan(v) or np.isinf(v):
            return False
        v = float(v)
        return (v==0) or (np.abs(np.log(v)) < np.log(max_v))
    except:
        return False

def d_check(v, c, v2c, max_c):
    """ Check valid entry """
    c_v = v_filter(v)

    c_e = (v in v2c)
    c_c = (c <= max_c)

    c_new = ((not c_e) and c_c)
    c_old = (c_e and c < v2c[v])

    return c_v and (c_new or c_old)

def d_update(v, c, v2c, v2o, ufs, max_c, d=0, max_u=1):
    """ Update Entries (Unary) """
    if d >= max_u:
        return

    for (uf_n, uf) in ufs.iteritems():
        vn = uf(v)
        if not d_check(vn,c,v2c,max_c):
            continue
        v2c[vn] = c
        v2o[vn] = (uf_n, v)
        d_update(vn, c, v2c, v2o, ufs, max_c, d+1, max_u)

def tch_iter(args):
    """Iterate once for a group of candidate values"""
    # unpack arguments ...
    y,lhs,rhs,v2c,v2o,ufs,bfs,v_filter,max_c,max_u=args
    for v_l in lhs:
        c_l = v2c[v_l]
        for v_r in rhs:
            c = c_l + v2c[v_r]
            if c > max_c:
                continue
            for bf_n, bf in bfs.iteritems():
                v = bf(v_l, v_r)
                if not v_filter(v):
                    continue
                if v not in v2c:
                    v2c[v] = c
                    v2o[v] = (bf_n, v_l, v_r)
                    d_update(v,c,v2c,v2o,ufs,max_c,max_u)
                    if (y in v2c) and (v2c[y] <= max_c):
                        return v2c, v2o
    return v2c,v2o

def tchisla(
        y,x, # values
        v2c,v2o, # results
        ufs,bfs,v_filter, # functions
        max_c=5, max_u=4, # constraints
        num_workers=8,
        proc=True
        ):
    """
    Parameters:
    y : target value
    x : construction number
    d : pre-created dictionary of shortest paths
    ufs : available unary functions
    bfs : available binary functions
    """

    ## Initialization
    for i in range(1, max_c+1):
        v = x*int('1'*i)
        c = i
        v2c[v] = c
        v2o[v] = ('cat%d'%i, x)
        d_update(v=v,c=c,v2c=v2c,v2o=v2o,ufs=ufs,max_c=max_c,max_u=max_u)

    # Now run ...
    print '--- Parameters ---'
    print 'Target Value : %d' % y 
    print 'Construction : %d' % x
    print 'Max Depth    : %d' % max_c
    print 'Max Update   : %d' % max_u
    print 'Use Process  : %s' % str(proc)

    print ''
    print '--- Run Start ---' 

    tic = time.time()

    prv = set() # "visited" values
    for c_idx in range(max_c-1):
        # set to max_c-1 since
        # @ c_idx = 0, ({1},{1}}... -> {2}, min_c=2
        # @ c_idx = 1, {{2},{1,2}} ... -> {3,4}, min_c=3
        # i.e. @ c_idx = i, min_c = i+2
        # @ c_idx = (max_c-2), min_c = max_c

        # Set Arguments...
        vs = [v for v in v2c.keys() if v_filter(v)]
        rhs = vs
        lhs = [v for v in rhs if (v not in prv)]
        [prv.add(v) for v in lhs]

        # Logging ...
        print '[%d] n(lhs):%d; n(rhs):%d' % (c_idx, len(lhs), len(rhs))
        lhs_s = np.array_split(lhs, num_workers)

        if proc:
            # use processes
            res = Pool(num_workers).map(
                    tch_iter,
                    [[y,lhs,rhs,v2c,v2o,ufs,bfs,v_filter,max_c,max_u] for lhs in lhs_s]
                    )
            # Grooming
            for _v2c, _v2o in res:
                for v in _v2c:
                    if v not in v2c:
                        v2c[v] = _v2c[v]
                        v2o[v] = _v2o[v]
                    else:
                        if v2c[v] > _v2c[v]:
                            v2c[v] = _v2c[v]
                            v2o[v] = _v2o[v]
        else:
            # use threads
            threads = [Thread(target=tch_iter, args=((y,lhs,rhs,v2c,v2o,ufs,bfs,v_filter,max_c,max_u),)) for lhs in lhs_s]
            for t in threads:
                t.daemon=True
                t.start()
            [t.join() for t in threads]

        if y in v2c:
            break
    toc = time.time()
    print 'Took %.2f Seconds' % (toc-tic)
    return (y in v2c)

def report(v, k, v2c, v2o):
    """
    Generates reports on creating v from k,
    based on v2c and v2o.
    """

    int_or_float = (lambda x : int(x) if (x == int(x)) else x)

    def _report(v,k,v2c,v2o,tree,depth):
        """
        Function used internally for report()
        in order to maintain layer structure
        without exposing internal variables such as tree and depth.
        """
        c,o = v2c[v], v2o[v]
        if len(o)==2 and v != k:
            f,p = o
            v,c,p = map(int_or_float, (v,c,p))
            s = ('%s(%s) = %s(%s)' % tuple(str(x) for x in (v,c,f,p)))
            tree[depth].append(s)
            _report(p,k,v2c,v2o,tree,depth+1)
        elif len(o)==3:
            f,l,r = o
            v,c,l,r = map(int_or_float, (v,c,l,r))
            s = ('%s(%s) = %s(%s,%s)' % tuple(str(x) for x in (v,int(c),f,l,r)))
            tree[depth].append(s)
            _report(l,k,v2c,v2o,tree,depth+1)
            _report(r,k,v2c,v2o,tree,depth+1)

    tree=defaultdict(lambda:[])
    _report(v,k,v2c,v2o,tree,0)

    print ''
    print '--- Report ---'
    for i in range(len(tree)):
        print tree[i]

def main(args):
    print '===================================='
    # parameters
    target = args.y 
    value = args.x
    max_c = args.max_c
    max_u = args.max_u
    proc = args.proc

    # unary functions, (name : y=f(x))
    ufs = {
        'sqrt' : isqrt,
        'fact' : fact,
        #'identity' : lambda x:x,
        'negate' : operator.neg
        }

    # binary functions
    bfs = {
        'add' : operator.add,
        'sub' : operator.sub,
        'mul' : operator.mul,
        'div' : div,
        #'sw_div' : lambda b,a:div(a,b),
        'pow' : pw,
        #'sw_pow' : lambda b,a:pw(a,b),
        'root' : rt,
        #'sw_rt' : lambda b,a:rt(a,b),
        }
    v2c = {}
    v2o = {}

    suc = tchisla(
            target,value,
            v2c,v2o,
            ufs,bfs,v_filter,
            max_c,max_u,
            proc=proc
            )

    print ''
    print '--- Run Finished ---'

    if suc:
        print 'Tchisla Succeeded!'
        report(target, value, v2c, v2o)
        print '%d#%d = %d' % (target, value, v2c[target])
    else:
        print 'Tchisla Failed!'
    print '===================================='

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
            '--y',
            type=int,
            help='target value',
            required=True
            )
    parser.add_argument(
            '--x',
            type=int,
            help='construction value',
            required=True
            )
    parser.add_argument(
            '--max_c',
            type=int,
            help='maximum search depth',
            required=True,
            )
    parser.add_argument(
            '--max_u',
            type=int,
            help='maximum unary updates',
            required=False,
            default=1
            )
    parser.add_argument(
            '--proc',
            type=str2bool,
            help='flag to use process, rather than threads',
            required=False,
            default=True
            )
    parser.add_argument(
            '--debug',
            type=str2bool,
            help='flag for logging warning messages',
            required=False,
            default=False
            )

    args = parser.parse_args(sys.argv[1:])

    if args.debug:
        main(args)
    else:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            main(args) 
