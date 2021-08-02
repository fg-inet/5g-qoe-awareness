import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.insert(0,currentdir) 

import numpy as np

# These functions were determined experimentally
cliTypeFuncMapping = {'hostSSH' : [900, 0.288, 1],
                      'hostVIP' : [2.66e+05, 2.80e-01, 2.64e+01],
                      'hostVID' : [1.67e+02, 3.54e-03, 1.53e-22],
                      'hostLVD' : [1.69e+01, 4.83e-03, 5.50e-01],
                      'hostFDO' : [4.51e+01, 4.21e-03, 1.66e+00]
                     }

def negExpFunc(x, a, b, c):
    return a * np.exp(-b*x) + c

def negLinFunc(x, a, b, c):
    return -a*x + b

def estDelay(cliType, availBand):
    funcMap = cliTypeFuncMapping[cliType]
    if cliType in cliTypeFuncMapping:
        delay = negExpFunc(availBand, *funcMap)
        if cliType == 'hostVIP':
            return delay
        return delay/2
    else:
        return 1000