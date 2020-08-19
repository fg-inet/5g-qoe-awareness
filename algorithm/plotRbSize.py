import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import csv
import math
import statistics
from scipy import stats
import scipy
import os

font = {'weight' : 'normal',
        'size'   : 40}

matplotlib.rc('font', **font)
matplotlib.rc('lines', linewidth=2.0)
matplotlib.rc('lines', markersize=8)

def plotRbSize(fileName):
    print(fileName)
    rbSizes = []
    # assignments = []
    objFunc = []
    minMos = []
    maxMos = []
    avgMos = []
    mosFairness = []

    file_to_read = fileName+'.csv'
    with open(file_to_read, mode='r') as readFile:
        csv_reader = csv.reader(readFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                rbSizes = row
            # elif line_count == 1:
            #     assignments = row
            elif line_count == 2:
                objFunc = row
            elif line_count == 3:
                minMos = row
            elif line_count == 4:
                maxMos = row
            elif line_count == 5:
                avgMos = row
            elif line_count == 6:
                mosFairness = row
            line_count += 1
    
    rbSizesNames = [str(int(x)) for x in rbSizes]
    fig, ax1 = plt.subplots(1, figsize=(16,12))
    ax1.plot(rbSizesNames, [eval(x)[2] for x in minMos], label='Minimal Utility', marker='o', ls='--')
    ax1.plot(rbSizesNames, [eval(x)[2] for x in maxMos], label='Maximal Utility', marker='o', ls='--')
    ax1.plot(rbSizesNames, avgMos, label='Mean Utility', marker='o', ls='-')
    ax1.set_ylim(0.95,5.05)
    ax1.set_ylabel('Utility')
    ax1.set_xlabel('Resource Block Size [kbps]')
    plt.legend()
    plt.grid(True)
    if not os.path.exists('plots/rbSizeTests/'+fileName+'/'):
        os.makedirs('plots/rbSizeTests/'+fileName+'/')
    outPath = 'plots/rbSizeTests/'+fileName+'/mos.pdf'
    fig.savefig(outPath, dpi=100, bbox_inches='tight')
    outPath = 'plots/rbSizeTests/'+fileName+'/mos.png'
    fig.savefig(outPath, dpi=100, bbox_inches='tight')
    plt.close('all')

    fig, ax1 = plt.subplots(1, figsize=(16,12))
    ax1.plot(rbSizesNames, mosFairness, label='QoE Fairness', marker='o', ls='-')
    ax1.plot(rbSizesNames, objFunc, label='Objective Function', marker='o', ls='-')
    ax1.set_ylim(-0.01,1.01)
    ax1.set_ylabel('Value')
    ax1.set_xlabel('Resource Block Size [kbps]')
    plt.legend()
    plt.grid(True)
    if not os.path.exists('plots/rbSizeTests/'+fileName+'/'):
        os.makedirs('plots/rbSizeTests/'+fileName+'/')
    outPath = 'plots/rbSizeTests/'+fileName+'/fairnessObjective.pdf'
    fig.savefig(outPath, dpi=100, bbox_inches='tight')
    outPath = 'plots/rbSizeTests/'+fileName+'/fairnessObjective.png'
    fig.savefig(outPath, dpi=100, bbox_inches='tight')
    plt.close('all')
    
   
plotRbSize('5sliRbSizeTest1')
plotRbSize('2sliLVD_DESRbSizeTest1')
plotRbSize('2sliLVD_BWSRbSizeTest1')