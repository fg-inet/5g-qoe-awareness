import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.insert(0,currentdir) 

import numpy as np

cliTypeFuncMapping = {'hostSSH' : [900, 0.288, 1],#[8.99e+02, 2.82e-01, 9.43e+00],
                      'hostVIP' : [2.66e+05, 2.80e-01, 2.64e+01],#[30, 0.00435, 0],#[1.52e+03, 4.35e-03, 2],
                      'hostVID' : [1600,0.0013,10],
                      'hostLVD' : [500, 0.0011, 60],#[40, 0.00568, 1], 
                      'hostFDO' : [600, 0.0006, 20]#[450,0.0006,20]
                     }

def negExpFunc(x, a, b, c):
    return a * np.exp(-b*x) + c

def negLinFunc(x, a, b, c):
    return -a*x + b

def estDelay(cliType, availBand):
    funcMap = cliTypeFuncMapping[cliType]
    # if cliType == 'hostVIP':
    #     retVal = negLinFunc(availBand, *funcMap)
    #     if retVal < 2:
    #         return 2
    #     else:
    #         return retVal
    if cliType in cliTypeFuncMapping:
        delay = negExpFunc(availBand, *funcMap)
        if cliType == 'hostVIP':
            return delay
        return delay/2
    else:
        return 1000