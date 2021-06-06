import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import csv
import math
import statistics
from scipy import stats
import os,sys,inspect

import re

import glob

font = {'weight' : 'normal',
        'size'   : 30}

matplotlib.rc('font', **font)
matplotlib.rc('lines', linewidth=2.0)
matplotlib.rc('lines', markersize=8)

downlink = ['Downlink', 'rxPkOk:vector(packetBytes)']
uplink = ['Uplink', 'txPk:vector(packetBytes)']
maxSimTime = 400

globalCounter = 0

def partialCDFBegin(numSubplots):
    fig, ax = plt.subplots(numSubplots, figsize=(16,12*numSubplots))
    return fig, ax

def partialCDFPlotData(fig, ax, data, label, lineType, lineColor):
    sorted_data = np.sort(data)
    linspaced = np.linspace(0, 1, len(data), endpoint=True)
    ax.plot(sorted_data, linspaced, lineType, label=label, color=lineColor)

def partialCDFPlotDataNoColor(fig, ax, data, label, lineType):
    sorted_data = np.sort(data)
    linspaced = np.linspace(0, 1, len(data), endpoint=True)
    ax.plot(sorted_data, linspaced, lineType, label=label)

def partialCDFEnd(fig, ax, title, xLabel, outPath):
    try:
        iterator = iter(ax)
    except TypeError:
        ax.set_ylim(0,1.1)
        ax.grid(True)
    else:
        for axs in ax:
            axs.set_ylim(0,1.1)
            axs.grid(True)
    plt.legend()
    if title != '':
        plt.title(title)
    plt.xlabel(xLabel)
    plt.ylabel("CDF")
    fig.savefig(outPath, dpi=100, bbox_inches='tight')
    plt.close('all')

def partialCDFEndPNG(fig, ax, title, xLabel, outPath):
    try:
        iterator = iter(ax)
    except TypeError:
        ax.set_ylim(0,1.1)
        ax.grid(True)
    else:
        for axs in ax:
            axs.set_ylim(0,1.1)
            axs.grid(True)
    plt.legend()
    if title != '':
        plt.title(title)
    plt.xlabel(xLabel)
    plt.ylabel("CDF")
    fig.savefig(outPath, dpi=100, bbox_inches='tight', format='png')
    plt.close('all')

def makeFullScenarioName(testName, numCLI, nodeTypes, nodeSplit):
    scenName = str(testName) + '_' + str(numCLI)
    for nodeType,numNodesType in zip(nodeTypes, nodeSplit):
        scenName += '_' + nodeType.replace('host','') + str(numNodesType)
    return scenName
    # return str(testName) + '_' + str(numCLI) + '_VID' + str(nodeSplit[0]) + '_FDO' + str(nodeSplit[1]) + '_SSH' + str(nodeSplit[2]) + '_VIP' + str(nodeSplit[3])

def makeNodeIdentifier(nodeType, nodeNum):
    if nodeNum < 0:
        return nodeType
    else:
        return nodeType + str(nodeNum)

def importDF(testName, numCLI, nodeTypes, nodeSplit, dataType):
    # File that will be read
    fullScenarioName = makeFullScenarioName(testName, numCLI, nodeTypes, nodeSplit)
    file_to_read = '../exports/extracted/' + str(dataType) + '/' + fullScenarioName + '.csv'
    print("Results from run: " + file_to_read)
    # Read the CSV
    return pd.read_csv(file_to_read)

def importDFextended(testName, numCLI, nodeTypes, nodeSplit, dataType, extension):
    # File that will be read
    fullScenarioName = makeFullScenarioName(testName, numCLI, nodeTypes, nodeSplit)
    file_to_read = '../exports/extracted/' + str(dataType) + '/' + fullScenarioName + extension + '.csv'
    print("Results from run: " + file_to_read)
    # Read the CSV
    return pd.read_csv(file_to_read)

def filterDFType(df, filterType):
    return df.filter(like=filterType)

def chooseName(dataName):
    if dataName == 'hostVID':
        return 'VoD'
    elif dataName == 'hostFDO':
        return 'Download'
    elif dataName == 'hostSSH':
        return 'SSH'
    elif dataName == 'hostVIP':
        return 'VoIP'
    elif dataName == 'hostLVD':
        return 'Live Video'

gbrToColor = {
    100 : 'lime',
    95 : 'tab:orange',
    90 : 'tab:red',
    85 : 'tab:pink',
    80 : 'tab:blue',
    75 : 'tab:cyan',
    70 : 'tab:green',
    65 : 'tab:purple',
    60 : 'tab:brown',
    55 : 'tab:olive',
    50 : 'tab:gray',
}

mbrToPoint = {
    100 : 'o',
    125 : 'v',
    150 : 'P',
    175 : 's',
    200 : 'p',
    225 : 'X',
    250 : 'D',
    275 : '1',
    300 : '*'
}


def getFileInfo(filename, desInfo):
    eN = filename.split('/')[-1].split('.')[0]
    resDict = {}
    resDict['name'] = eN
    for param in eN.split('-')[-1].split('_'):
        split = re.split('(\d+)',param)
        if split[0] in desInfo:
            resDict[split[0]] = int(split[1])
    return resDict

def plotParameterStudyMOS(testPrefix, appType, mbrs, gbrs, qs, maxNumCliPlot):
    print('-------------', testPrefix, '-------------')
    prePath = '../exports/extracted/mos2/'
    filenames = glob.glob(prePath+testPrefix+'-*')
    print('-> There are', len(filenames), 'experiments in this parameter study.')
    fig, ax = plt.subplots(1, figsize=(16,12))
    filterName = 'Val'
    
    reqRunInfo = ['Q', 'M', 'C'] # Q = target QoE, M = GBR multiplier, C = MBR multiplier
    reqRunInfo.append(appType) # This will get the number of clients in experiment

    runResults = {}
    numClis = []
    minValue = 5.0

    for filename in filenames:
        fid = getFileInfo(filename, reqRunInfo)
        if fid['Q'] == qs and fid['M'] in gbrs and fid['C'] in mbrs and fid[appType] <= maxNumCliPlot:
            print('\t-> Run:', fid['name'], end=': ')
            runDict = {}
            runDict['Q'] = fid['Q'] # Target QoE in run
            runDict['M'] = fid['M'] # GBR multiplier in run
            runDict['C'] = fid['C'] # MBR multiplier in run
            runDict['numCli'] = fid[appType] # Number of clients in run
            if runDict['numCli'] not in numClis:
                numClis.append(runDict['numCli'])
            
            # Getting values
            runDF = pd.read_csv(filename)
            valDF = filterDFType(filterDFType(runDF, filterName), appType)
            meanRunVals = []

            # Get mean for each client in run first
            for col in valDF:
                meanRunVals.append(statistics.mean(valDF[col].dropna().tolist()))
            # Then calculate the mean for fun based on client means
            runDict['meanVal'] = statistics.mean(meanRunVals)
            minValue = min(minValue, runDict['meanVal'])
            print('mean QoE =', runDict['meanVal'])
            runResults[fid['name']] = runDict # Store it ready to plot
    
    numClis = sorted(numClis)
    # minmax = (1.0,4.5)
    minmax = (minValue-0.05,4.5)

    # Plot the means
    for run in runResults:
        runData = runResults[run]
        ax.scatter(2*numClis.index(runData['numCli']), runData['meanVal'], marker=mbrToPoint[runData['C']], color=gbrToColor[runData['M']], alpha=0.7, s=16**2)
    
    # Take care of the legend
    legendHandles = []
    for mbr in mbrs:
        point = ax.scatter(-10,5, marker=mbrToPoint[mbr], color='black', label='MBR of ' + str(mbr) + '%', s=14**2)
        legendHandles.append(point)
    for gbr in gbrs:
        ptch = mpatches.Patch(color=gbrToColor[gbr], label='GBR of ' + str(gbr) + '%')
        legendHandles.append(ptch)

    ticks = []
    labels = []
    for num in range(len(numClis)):
        ax.vlines(2*num+1, ymin=minmax[0], ymax=minmax[1], color='black')
        ticks.append(2*num)
        labels.append(numClis[num])

    # Finish plotting
    preOutPath = '../exports/paramStudyPlots/mosVsNumCli/'
    if not os.path.exists(preOutPath):
        os.makedirs(preOutPath)
    ax.set_ylim(minmax)
    ax.set_xlim(-1,2*len(numClis)-1)

    plt.xticks(ticks, labels, rotation=0)
    plt.legend(handles=legendHandles, fontsize=25, bbox_to_anchor=(1, 1), loc='upper left')
    plt.grid(axis='y')
    plt.xlabel('Number of Clients')
    plt.ylabel('Mean ' + chooseName('host'+appType) + ' MOS')
    outPath = preOutPath+'sysUtilClient'+testPrefix+'_M'+str(gbrs)+'_C'+str(mbrs)+'_maxNumClis'+str(maxNumCliPlot)+'.png'
    fig.savefig(outPath, dpi=100, bbox_inches='tight', format='png')
    plt.close('all')

############################################################################################

testNames = ['parameterStudyVoIP'] # Name prefix of the QoE test
targetQoEs = [35] # Target QoEs
mbrs = [100,125,150,175,200]
gbrs = [100, 95, 90, 85, 80, 75, 70, 65, 60, 55, 50]
sliNamess = [['none']]
clients = ['VIP']
maxNumCliPlot = [142,200]
for testName, client in zip(testNames, clients):
    for tQ in targetQoEs:
        for numCli in maxNumCliPlot:
            plotParameterStudyMOS(testName, client, mbrs, gbrs, tQ, numCli)
            for mbr in mbrs:
                plotParameterStudyMOS(testName, client, [mbr], gbrs, tQ, numCli)