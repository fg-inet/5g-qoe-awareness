import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import csv
import math
import statistics
from scipy import stats
import os,sys,inspect

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
    elif dataName == '2link0':
        return 'Bandwidth Slice'
    elif dataName == '2link1':
        return 'Delay Slice'
    elif dataName == '1link0':
        return 'Link'
    elif dataName == '3link0':
        return 'Bandwidth Slice'
    elif dataName == '3link1':
        return 'Delay Slice'
    elif dataName == '3link2':
        return 'Return Link'

colormap = plt.get_cmap('Set1').colors
print(colormap)
colorMapping = {
    'VID' : colormap[0],
    'LVD' : colormap[1], 
    'FDO' : colormap[2], 
    'SSH' : colormap[3], 
    'VIP' : colormap[4],
    'all' : colormap[5]
}
def chooseColor(dataName):
    # if dataName == 'hostVID':
    #     return 'y'
    # elif dataName == 'hostFDO':
    #     return 'g'
    # elif dataName == 'hostSSH':
    #     return 'r'
    # elif dataName == 'hostVIP':
    #     return 'b'
    # if dataName == 'hostLVD':
    #     return 'm'
    if dataName == 'hostVID':
        return colorMapping['VID']
    elif dataName == 'hostFDO':
        return colorMapping['FDO']
    elif dataName == 'hostSSH':
        return colorMapping['SSH']
    elif dataName == 'hostVIP':
        return colorMapping['VIP']
    if dataName == 'hostLVD':
        return colorMapping['LVD']
    elif dataName == '2link0':
        return 'c'
    elif dataName == '2link1':
        return 'm'
    elif dataName == '1link0':
        return 'k'
    elif dataName == '3link0':
        return 'c'
    elif dataName == '3link1':
        return 'm'
    elif dataName == '3link2':
        return 'k'

niceDataTypeName = {
    'DABL' : 'Buffer Length [s]',
    'DAMS' : 'MOS',
    'DAVB' : 'Requested Video Bitrate [kbps]',
    'DAVR' : 'Requested Video Resolution [p]',
    'DLVD' : 'Delay To Live Video Edge [s]',
    'Mos' : 'MOS',
    'RTT' : 'Round Trip Time [s]',
    'DAEB' : 'Estimated Bitrate [kbps]',
    'E2ED' : 'End to End Delay [s]',
    'PkLR' : 'Packet Loss Rate',
    'PlDel' : 'Playout Delay [s]',
    'PlLR' : 'Playout Loss Rate',
    'TDLR' : 'Taildrop Loss Rate',
    'rtt' : 'Round Trip Time [s]'
}

def plotMeanDataTypeCdfAllApps(testName, numCLI, nodeTypes, nodeSplit, dataIdent, folderName, nodeTypesToPlot):
    df = importDF(testName, numCLI, nodeTypes, nodeSplit, folderName)
    fig, ax1 = partialCDFBegin(1)
    maxValue = 0
    for nodeType,numNodes in zip(nodeTypes,nodeSplit):
        if nodeType in nodeTypesToPlot:
            tempValue = []
            for nodeNum in range(numNodes):
                colName = makeNodeIdentifier(nodeType, nodeNum) + " " + dataIdent + " Val"
                data = df[colName].dropna().tolist()
                if len(data) > 0:
                    tempValue.append(statistics.mean(data))
            # print(tempValue)
            if len(tempValue) > 0:
                if maxValue < max(tempValue):
                    maxValue = max(tempValue)
                partialCDFPlotData(fig, ax1, tempValue, chooseName(nodeType), '-o', chooseColor(nodeType))
    if dataIdent == 'Mos':
        ax1.set_xlim(0.95,5.05)
    else:
        ax1.set_xlim(0,1.01*maxValue)
    partialCDFEnd(fig,ax1,'', 'Mean Client ' + niceDataTypeName[dataIdent], '../exports/plots/'+makeFullScenarioName(testName, numCLI, nodeTypes, nodeSplit)+'/'+str(globalCounter)+'_meanCdf' + dataIdent + str(nodeTypesToPlot) + '.pdf')
    partialCDFEndPNG(fig,ax1,'', 'Mean Client ' + niceDataTypeName[dataIdent], '../exports/plots/'+makeFullScenarioName(testName, numCLI, nodeTypes, nodeSplit)+'/'+str(globalCounter)+'_meanCdf' + dataIdent + str(nodeTypesToPlot) + '.png')

minMaxQoE = {'hostFDO' : {'minMOS' : 1.0,
                            'maxMOS' : 5.0},
                'hostSSH' : {'minMOS' : 1.0,
                            'maxMOS' : 4.292851753999999},
                'hostVID' : {'minMOS' : 1.0,
                            'maxMOS' : 4.394885531954699},
                'hostVIP' : {'minMOS' : 1.0,
                            'maxMOS' : 4.5},
                'hostLVD' : {'minMOS' : 1.0,
                            'maxMOS' : 4.585703050898499}}

def normalizeQoE(cliType, mos):
    retMos = (mos - minMaxQoE[cliType]['minMOS'])*((5.0 - 1.0)/(minMaxQoE[cliType]['maxMOS'] - minMaxQoE[cliType]['minMOS'])) + 1.0
    return max(1.0, min(retMos, 5.0))

def plotDataTypeCdfAllApps(testName, numCLI, nodeTypes, nodeSplit, dataIdent, folderName, nodeTypesToPlot):
    df = importDF(testName, numCLI, nodeTypes, nodeSplit, folderName)
    fig, ax1 = partialCDFBegin(1)
    maxValue = 0
    for nodeType,numNodes in zip(nodeTypes,nodeSplit):
        if nodeType in nodeTypesToPlot:
            tempValue = []
            for nodeNum in range(numNodes):
                colName = makeNodeIdentifier(nodeType, nodeNum) + " " + dataIdent + " Val"
                tempValue.extend(df[colName].dropna().tolist())
            # print(tempValue)
            if len(tempValue) > 0:
                if maxValue < max(tempValue):
                    maxValue = max(tempValue)
                partialCDFPlotData(fig, ax1, tempValue, chooseName(nodeType), '-o', chooseColor(nodeType))
    if dataIdent == 'Mos':
        ax1.set_xlim(0.95,5.05)
    else:
        ax1.set_xlim(0,1.01*maxValue)
    partialCDFEnd(fig,ax1,'', 'Client ' + niceDataTypeName[dataIdent], '../exports/plots/'+makeFullScenarioName(testName, numCLI, nodeTypes, nodeSplit)+'/'+str(globalCounter)+'_cdf' + dataIdent + str(nodeTypesToPlot) + '.pdf')
    partialCDFEndPNG(fig,ax1,'', 'Client ' + niceDataTypeName[dataIdent], '../exports/plots/'+makeFullScenarioName(testName, numCLI, nodeTypes, nodeSplit)+'/'+str(globalCounter)+'_cdf' + dataIdent + str(nodeTypesToPlot) + '.png')

def plotUtilityCdfAllApps(testName, numCLI, nodeTypes, nodeSplit, nodeTypesToPlot):
    folderName = 'mos'
    dataIdent = 'Mos'
    df = importDF(testName, numCLI, nodeTypes, nodeSplit, folderName)
    fig, ax1 = partialCDFBegin(1)
    maxValue = 0
    for nodeType,numNodes in zip(nodeTypes,nodeSplit):
        if nodeType in nodeTypesToPlot:
            tempValue = []
            for nodeNum in range(numNodes):
                colName = makeNodeIdentifier(nodeType, nodeNum) + " " + dataIdent + " Val"
                tempValue.extend([normalizeQoE(nodeType, x) for x in df[colName].dropna().tolist()])
            # print(tempValue)
            if len(tempValue) > 0:
                if maxValue < max(tempValue):
                    maxValue = max(tempValue)
                partialCDFPlotData(fig, ax1, tempValue, chooseName(nodeType), '-o', chooseColor(nodeType))
    if dataIdent == 'Mos':
        ax1.set_xlim(0.95,5.05)
    else:
        ax1.set_xlim(0,1.01*maxValue)
    prePath = '../exports/plots/baseSlicingComps/'
    if not os.path.exists(prePath):
        os.makedirs(prePath)
    plt.legend(loc='upper left')
    partialCDFEnd(fig,ax1,'', 'Utility', prePath+makeFullScenarioName(testName, numCLI, nodeTypes, nodeSplit)+'_'+str(globalCounter)+'_cdf' + dataIdent + str(nodeTypesToPlot) + '.pdf')
    partialCDFEndPNG(fig,ax1,'', 'Utility', prePath+makeFullScenarioName(testName, numCLI, nodeTypes, nodeSplit)+'_'+str(globalCounter)+'_cdf' + dataIdent + str(nodeTypesToPlot) + '.png')

# plotUtilityCdfAllApps('baselineTest', 250, ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [50 for x in range(5)], ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'])
# plotUtilityCdfAllApps('baselineTestNS_2sli_LVD-BWS_AlgoTest_alpha05', 250, ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [50 for x in range(5)], ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'])
# plotUtilityCdfAllApps('baselineTestNS_5sli_AlgoTest_alpha05', 250, ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [50 for x in range(5)], ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'])
# plotMosBaseSliComp('baselineTest', 'baselineTestNS_2sli_LVD-BWS_AlgoTest_alpha05', 'baselineTestNS_5sli_AlgoTest_alpha05', 250, ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [50 for x in range(5)], 'hostVID')

niceTestName = {
    'baselineTest' : 'Baseline',
    'baselineTestTemp' : 'Temporary Baseline',
    'baselineTestNS_2sli_LVD-DES' : '2 Slices, Live in Delay, No Algorithm',
    # 'baselineTestNS_2sli_LVD-BWS' : '2 Slices, Live Video in Bandwidth Slice',
    'baselineTestNS_2sli_LVD-BWS' : '2 Slices, Live in Bandwidth, No Algorithm',
    'baselineTestNS_2sliSingle_LVD-DES' : '2 Slices + Single Link, Live Video in Delay Slice',
    'baselineTestNS_2sliSingle_LVD-BWS' : '2 Slices + Single Link, Live Video in Bandwidth Slice',
    'baselineTestNS_2sliSingle2sli_LVD-DES' : '2 Slices + Single Link + 2 Slices, Live Video in Delay Slice',
    'baselineTestNS_2sliSingle2sli_LVD-BWS' : '2 Slices + Single Link + 2 Slices, Live Video in Bandwidth Slice',
    'baselineTestNS_2sliDouble_LVD-DES' : 'Directional 2 Slices + Single Link, Live Video in Delay Slice',
    'baselineTestNSPrioQueue_2sliSingle2sliNBS_LVD-DES' : '2 Same Prio Queues: 2 + Single + 2 Links, Live Vid in Delay Slice',
    'baselineTestNSPrioQueueAF_2sliSingle2sliNBS_LVD-DES' : '2 Different Prio Queues: 2 + Single + 2 Links, Live Vid in Delay Slice',
    'baselineTestNSPrioQueue_2sliSingle2sliNBS_LVD-BWS' : '2 Same Prio Queues: 2 + Single + 2 Links, Live Vid in Bandwidth Slice',
    'baselineTestNSPrioQueueAF_2sliSingle2sliNBS_LVD-BWS' : '2 Different Prio Queues: 2 + Single + 2 Links, Live Vid in Bandwidth Slice',
    'baselineTestNS_2sliDouble_LVD-BWS' : 'Directional 2 Slices + Single Link, Live Video in Bandwidth Slice',
    'baselineTestNS_5sli' : '5 Slices',
    'baselineTestNS_5sliSingle' : '5 Slices + Single Link',
    'baselineTestNS_5sliSingle5sli' : '5 Slices + Single Link + 5 Slices',
    'baselineTestNS_5sliDouble' : 'Directional 5 Slices + Single Link',
    'baselineTestNSPrioQueueAF_Single_LVD-DES' : 'Single Link with priority queue for Delay Slice, Live Video in Delay Slice',
    'baselineTestNSPrioQueueAF_SingleLBS_LVD-DES' : 'Single Link with priority queue for Delay Slice, Live Video in Delay Slice',
    'baselineTestNSPrioQueueAF_Single50_LVD-DES' : 'Single Link with priority queue for Delay Slice, Live Video in Delay Slice',
    'baselineTestNSPrioQueueAF_SingleNBS_LVD-DES' : 'Single Link with priority queue for Delay Slice, Live Video in Delay Slice',
    'baselineTestNSPrioQueue_SingleDW_LVD-BWS' : 'Single Link with WRR sheduler, Live Video in Bandwidth Slice',
    'baselineTestNSPrioQueue_SingleDWR_LVD-DES' : 'Single Link with WRR sheduler, Live Video in Delay Slice',
    'baselineTestNSPrioQueue_SingleDWR_LVD-BWS' : 'Single Link with WRR sheduler, Live Video in Bandwidth Slice',
    'baselineTestNSPrioQueue_SingleDWRLQ_LVD-DES' : 'One Link + WRR sheduler LQ, Live Vid in Delay Sli',
    'baselineTestNSPrioQueue_SingleDWRLQ_LVD-BWS' : 'One Link + WRR sheduler LQ, Live Vid in Bandwidth Sli',
    'baselineTestNSPrioQueueDES_2sliSingle2sli_LVD-DES' : '1 + 1 + 1 Links with Priority for Delay Slice, Live Video in Delay Slice',
    'baselineTestNSPrioQueueDES_2sliSingle2sli_LVD-BWS' : '1 + 1 + 1 Links with Priority for Delay Slice, Live Video in Bandwidth Slice',
    'baselineTestNSPrioQueue_2sliSingle2sliDWR_LVD-DES' : '1 + 1 + 1 Links with Weighted Queues, Live Video in Delay Slice',
    'baselineTestNSPrioQueue_2sliSingle2sliDWR_LVD-BWS' : '1 + 1 + 1 Links with Weighted Queues, Live Video in Bandwidth Slice',
    'baselineTestNSPrioQueueDES2_2sliSingle2sli_LVD-DES' : '2 + 1 + 2 Links with Priority for Delay Slice, Live Video in Delay Slice',
    'baselineTestNSPrioQueueDES2_2sliSingle2sli_LVD-BWS' : '2 + 1 + 2 Links with Priority for Delay Slice, Live Video in Bandwidth Slice',
    'baselineTestNSPrioQueueDES4_2sliSingle2sli_LVD-DES' : '2 + 1 + 2 Links with 4x Priority for Delay Slice, Live Video in Delay Slice',
    'baselineTestNSPrioQueueDES4_2sliSingle2sli_LVD-BWS' : '2 + 1 + 2 Links with 4x Priority for Delay Slice, Live Video in Bandwidth Slice',
    'baselineTestNSPrioQueue_2sliSingle2sliDWR2_LVD-DES' : '2 + 1 + 2 Links with Weighted Queues, Live Video in Delay Slice',
    'baselineTestNSPrioQueue_2sliSingle2sliDWR2_LVD-BWS' : '2 + 1 + 2 Links with Weighted Queues, Live Video in Bandwidth Slice',
    'baselineTestNSPrioQueue_2sliSingle2sliDWRLQ_LVD-DES' : '2 + 1 + 2 Links with WRR, Live Video in Delay Slice',
    'baselineTestNSPrioQueue_2sliSingle2sliDWRLQ_LVD-BWS' : '2 + 1 + 2 Links with WRR, Live Video in Bandwidth Slice',
    'baselineTestNSPrioQueue_2sliSingle2sliDWRLQPD_LVD-DES' : '2 + 1 + 2 Links WRR Delay Prio, Live Video in Delay Slice',
    'baselineTestNSPrioQueue_2sliSingle2sliDWRLQPD_LVD-BWS' : '2 + 1 + 2 Links WRR Delay Prio, Live Video in Bandwidth Slice',
    'baselineTestNS_5sli_AlgoTest1' : '5 Slices, Algorithm v0.1',
    'baselineTestNS_5sli_AlgoTest2' : '5 Slices, Algorithm v0.11',
    'baselineTestNS_5sli_AlgoTest3' : '5 Slices, Algorithm v0.12',
    'baselineTestNS_2sli_LVD-DES_AlgoTest1' : '2 Slices, Live in Delay, Algorithm v0.11',
    'baselineTestNS_2sli_LVD-BWS_AlgoTest1' : '2 Slices, Live in Bandwidth, Algorithm v0.11',
    'baselineTestNS_2sli_LVD-DES_AlgoTest3' : '2 Slices, Live in Delay, Algorithm v0.12',
    'baselineTestNS_2sli_LVD-BWS_AlgoTest3' : '2 Slices, Live in Bandwidth, Algorithm v0.12'
}



def plotMeanDataTypeCdfAllAppsComp(testNameMain, testNameSecondary, numCLI, nodeTypes, nodeSplit, dataIdent, folderName, nodeTypesToPlot):
    df = importDF(testNameMain, numCLI, nodeTypes, nodeSplit, folderName)
    df2 = importDF(testNameSecondary, numCLI, nodeTypes, nodeSplit, folderName)
    fig, ax = partialCDFBegin(2)
    maxValue = 0
    for nodeType,numNodes in zip(nodeTypes,nodeSplit):
        if nodeType in nodeTypesToPlot:
            tempValue = []
            tempValue2 = []
            for nodeNum in range(numNodes):
                colName = makeNodeIdentifier(nodeType, nodeNum) + " " + dataIdent + " Val"
                data = df[colName].dropna().tolist()
                data2 = df2[colName].dropna().tolist()
                if len(data) > 0:
                    tempValue.append(statistics.mean(data))
                if len(data2) > 0:
                    tempValue2.append(statistics.mean(data2))
            # print(tempValue)
            if len(tempValue) > 0:
                if maxValue < max(tempValue):
                    maxValue = max(tempValue)
                if len(tempValue2) > 0:
                    if maxValue < max(tempValue2):
                        maxValue = max(tempValue2)
                partialCDFPlotData(fig, ax[0], tempValue, chooseName(nodeType), '-o', chooseColor(nodeType))
                partialCDFPlotData(fig, ax[1], tempValue2, chooseName(nodeType), '-o', chooseColor(nodeType))
    for axs in ax:
        if dataIdent == 'Mos':
            axs.set_xlim(0.95,5.05)
        else:
            axs.set_xlim(0,1.01*maxValue)
    ax[0].title.set_text(niceTestName[testNameMain])
    ax[1].title.set_text(niceTestName[testNameSecondary])
    partialCDFEnd(fig,ax,'', 'Mean Client ' + niceDataTypeName[dataIdent], '../exports/plots/'+makeFullScenarioName(testNameMain, numCLI, nodeTypes, nodeSplit)+'/'+str(globalCounter)+'_meanCdf' + dataIdent + str(nodeTypesToPlot) + 'compWith' + str(testNameSecondary) + '.pdf')
    partialCDFEndPNG(fig,ax,'', 'Mean Client ' + niceDataTypeName[dataIdent], '../exports/plots/'+makeFullScenarioName(testNameMain, numCLI, nodeTypes, nodeSplit)+'/'+str(globalCounter)+'_meanCdf' + dataIdent + str(nodeTypesToPlot) + 'compWith' + str(testNameSecondary) + '.png')

# plotMeanDataTypeCdfAllAppsComp('baselineTestNS_2sliSingle_LVD-DES', 'baselineTest', 250, ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [50 for x in range(5)], 'Mos', 'mos', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'])

def plotDataTypeCdfAllAppsComp(testNameMain, testNameSecondary, numCLI, nodeTypes, nodeSplit, dataIdent, folderName, nodeTypesToPlot):
    df = importDF(testNameMain, numCLI, nodeTypes, nodeSplit, folderName)
    df2 = importDF(testNameSecondary, numCLI, nodeTypes, nodeSplit, folderName)
    fig, ax = partialCDFBegin(2)
    maxValue = 0
    for nodeType,numNodes in zip(nodeTypes,nodeSplit):
        if nodeType in nodeTypesToPlot:
            tempValue = []
            tempValue2 = []
            for nodeNum in range(numNodes):
                colName = makeNodeIdentifier(nodeType, nodeNum) + " " + dataIdent + " Val"
                tempValue.extend(df[colName].dropna().tolist())
                tempValue2.extend(df2[colName].dropna().tolist())
            # print(tempValue)
            if len(tempValue) > 0:
                if maxValue < max(tempValue):
                    maxValue = max(tempValue)
                if len(tempValue2) > 0:
                    if maxValue < max(tempValue2):
                        maxValue = max(tempValue2)
                partialCDFPlotData(fig, ax[0], tempValue, chooseName(nodeType), '-o', chooseColor(nodeType))
                partialCDFPlotData(fig, ax[1], tempValue2, chooseName(nodeType), '-o', chooseColor(nodeType))
    if dataIdent == 'Mos':
        for axs in ax:
            axs.set_xlim(0.95,5.05)
    else:
        ax[0].set_xlim(0,1.01*maxValue)
        ax[1].set_xlim(0,1.01*maxValue)
    ax[0].title.set_text(niceTestName[testNameMain])
    ax[1].title.set_text(niceTestName[testNameSecondary])
    partialCDFEnd(fig,ax,'', 'Client ' + niceDataTypeName[dataIdent], '../exports/plots/'+makeFullScenarioName(testNameMain, numCLI, nodeTypes, nodeSplit)+'/'+str(globalCounter)+'_cdf' + dataIdent + str(nodeTypesToPlot) + 'compWith' + str(testNameSecondary) + '.pdf')
    partialCDFEndPNG(fig,ax,'', 'Client ' + niceDataTypeName[dataIdent], '../exports/plots/'+makeFullScenarioName(testNameMain, numCLI, nodeTypes, nodeSplit)+'/'+str(globalCounter)+'_cdf' + dataIdent + str(nodeTypesToPlot) + 'compWith' + str(testNameSecondary) + '.png')

def plotEstimatedChosenBitrateLVD(testName, numCLI, nodeTypes, nodeSplit, nodeTypesToPlot):
    df = importDF(testName, numCLI, nodeTypes, nodeSplit, 'daeb')
    df2 = importDF(testName, numCLI, nodeTypes, nodeSplit, 'davb')
    fig, ax = partialCDFBegin(1)
    maxValue = 0
    for nodeType,numNodes in zip(nodeTypes,nodeSplit):
        if nodeType in nodeTypesToPlot:
            tempValue = []
            tempValue2 = []
            for nodeNum in range(numNodes):
                colName = makeNodeIdentifier(nodeType, nodeNum) + " DAEB Val"
                colName2 = makeNodeIdentifier(nodeType, nodeNum) + " DAVB Val"
                tempValue.extend(df[colName].dropna().tolist())
                tempValue2.extend(df2[colName2].dropna().tolist())
            # print(tempValue)
            if len(tempValue) > 0:
                if maxValue < max(tempValue):
                    maxValue = max(tempValue)
                if maxValue < max(tempValue2):
                    maxValue = max(tempValue2)
                partialCDFPlotData(fig, ax, tempValue, 'Estimated Bitrate', '-o', 'g')
                partialCDFPlotData(fig, ax, tempValue2, 'Chosen Video Bitrate', '-o', 'b')
    ax.set_xlim(0,1.01*maxValue)
    partialCDFEnd(fig,ax,'', 'Bitrate [kbps]', '../exports/plots/'+makeFullScenarioName(testName, numCLI, nodeTypes, nodeSplit)+'/'+str(globalCounter)+'_cdfDAEBDAVB'  + str(nodeTypesToPlot) + '.pdf')
    partialCDFEndPNG(fig,ax,'', 'Bitrate [kbps]', '../exports/plots/'+makeFullScenarioName(testName, numCLI, nodeTypes, nodeSplit)+'/'+str(globalCounter)+'_cdfDAEBDAVB'  + str(nodeTypesToPlot) + '.png')

# plotDataTypeCdfAllAppsComp('baselineTestNS_2sliSingle_LVD-DES', 'baselineTest', 250, ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [50 for x in range(5)], 'Mos', 'mos', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], 'PNG')

def plotTPdirection(testName, numCLI, nodeTypes, nodeSplit, numSlices, direction):
    df = importDFextended(testName, numCLI, nodeTypes, nodeSplit, 'throughputs', '_' + direction[0])
    fig, ax1 = plt.subplots(1, figsize=(16,12))
    times = range(1,maxSimTime+1,1)
    for nodeType,numNodes in zip(nodeTypes,nodeSplit):
        tempDF = pd.DataFrame()
        for nodeNum in range(numNodes):
            colName = direction[0] + " Throughput " + makeNodeIdentifier(nodeType, nodeNum)
            tempDF = pd.concat([tempDF,df[colName]],axis=1,ignore_index=False)
        ax1.plot(times, [x/1000 for x in tempDF.sum(axis=1).tolist()], label=chooseName(nodeType), marker='o', ls='-', color=chooseColor(nodeType))
    for sliceNum in range(numSlices):
        linkDF = filterDFType(df, direction[0] + ' Throughput resAllocLink' + str(sliceNum))
        ax1.plot(times, [x/1000 for x in linkDF.sum(axis=1).tolist()], label=chooseName(str(numSlices)+'link'+str(sliceNum)), marker='o', ls='-', color=chooseColor(str(numSlices)+'link'+str(sliceNum)))
        # print(linkDF)
    ax1.set_ylabel(direction[0]+' Throughput [mbps]')
    ax1.set_xlabel('Simulation Time [s]')
    ax1.set_xlim(0,1.01*times[-1])
    # ax1.set_ylim(0,105)
    plt.legend()
    plt.grid(True)
    fig.savefig('../exports/plots/'+makeFullScenarioName(testName, numCLI, nodeTypes, nodeSplit)+'/'+str(globalCounter)+'_'+direction[0]+'Throughputs' + str(nodeTypes) + '.pdf', dpi=100, bbox_inches='tight')

def plotTPScdfDirection(testName, numCLI, nodeTypes, nodeSplit, numSlices, direction, cutoff):
    df = importDFextended(testName, numCLI, nodeTypes, nodeSplit, 'throughputs', '_' + direction[0])
    fig, ax1 = partialCDFBegin(1)
    maxTPS = 0
    for nodeType,numNodes in zip(nodeTypes,nodeSplit):
        tempTPSall = []
        for nodeNum in range(numNodes):
            colName = direction[0] + " Throughput " + makeNodeIdentifier(nodeType, nodeNum)
            tempTPSall.extend([x/1000 for x in df[colName].tolist()[:int(cutoff)+1]])
        if maxTPS < max(tempTPSall):
            maxTPS = max(tempTPSall)
        partialCDFPlotData(fig, ax1, tempTPSall, chooseName(nodeType), '-o', chooseColor(nodeType))

    # for sliceNum in range(numSlices):
    #     tempTPSslice = []
    #     colName = direction[0] + ' Throughput resAllocLink' + str(sliceNum)
    #     tempTPSslice.extend([x/1000 for x in df[colName].tolist()[:int(cutoff)+1]])
    #     partialCDFPlotData(fig, ax1, tempTPSslice, chooseName(str(numSlices)+'link'+str(sliceNum)), '-o', chooseColor(str(numSlices)+'link'+str(sliceNum)))
    #     if maxTPS < max(tempTPSslice):
    #         maxTPS = max(tempTPSslice)

    ax1.set_xlim(0,1.01*maxTPS)
    partialCDFEndPNG(fig,ax1,'', 'Throughput [mbps]', '../exports/plots/'+makeFullScenarioName(testName, numCLI, nodeTypes, nodeSplit)+'/'+str(globalCounter)+'_cdf'+direction[0]+'ThroughputsCutoff'+ str(cutoff) + str(nodeTypes) + '.png')
    partialCDFEnd(fig,ax1,'', 'Throughput [mbps]', '../exports/plots/'+makeFullScenarioName(testName, numCLI, nodeTypes, nodeSplit)+'/'+str(globalCounter)+'_cdf'+direction[0]+'ThroughputsCutoff'+ str(cutoff) + str(nodeTypes) + '.pdf')

def plotMeanTPScdfDirection(testName, numCLI, nodeTypes, nodeSplit, direction, cutoff):
    df = importDFextended(testName, numCLI, nodeTypes, nodeSplit, 'throughputs', '_' + direction[0])
    fig, ax1 = partialCDFBegin(1)
    maxTPS = 0
    for nodeType,numNodes in zip(nodeTypes,nodeSplit):
        tempTPSall = []
        for nodeNum in range(numNodes):
            colName = direction[0] + " Throughput " + makeNodeIdentifier(nodeType, nodeNum)
            tempTPSall.append(statistics.mean([x/1000 for x in df[colName].tolist()[:int(cutoff)+1]]))
        if maxTPS < max(tempTPSall):
            maxTPS = max(tempTPSall)
        partialCDFPlotData(fig, ax1, tempTPSall, chooseName(nodeType), '-o', chooseColor(nodeType))

    ax1.set_xlim(0,1.01*maxTPS)
    partialCDFEnd(fig,ax1,'', 'Mean Client Throughput [mbps]', '../exports/plots/'+makeFullScenarioName(testName, numCLI, nodeTypes, nodeSplit)+'/'+str(globalCounter)+'_cdfMean'+direction[0]+'ThroughputsCutoff'+ str(cutoff) + str(nodeTypes) + '.pdf')
    partialCDFEndPNG(fig,ax1,'', 'Mean Client Throughput [mbps]', '../exports/plots/'+makeFullScenarioName(testName, numCLI, nodeTypes, nodeSplit)+'/'+str(globalCounter)+'_cdfMean'+direction[0]+'ThroughputsCutoff'+ str(cutoff) + str(nodeTypes) + '.png')

def plotMeanTPScdfDirectionComp(testNameMain, testNameSecondary, numCLI, nodeTypes, nodeSplit, direction, cutoff):
    df = importDFextended(testNameMain, numCLI, nodeTypes, nodeSplit, 'throughputs', '_' + direction[0])
    df2 = importDFextended(testNameSecondary, numCLI, nodeTypes, nodeSplit, 'throughputs', '_' + direction[0])
    fig, ax = partialCDFBegin(2)
    maxTPS = 0
    for nodeType,numNodes in zip(nodeTypes,nodeSplit):
        tempTPSall = []
        tempTPSall2 = []
        for nodeNum in range(numNodes):
            colName = direction[0] + " Throughput " + makeNodeIdentifier(nodeType, nodeNum)
            tempTPSall.append(statistics.mean([x/1000 for x in df[colName].tolist()[:int(cutoff)+1]]))
            tempTPSall2.append(statistics.mean([x/1000 for x in df2[colName].tolist()[:int(cutoff)+1]]))
        if maxTPS < max(tempTPSall):
            maxTPS = max(tempTPSall)
        if maxTPS < max(tempTPSall2):
            maxTPS = max(tempTPSall2)
        partialCDFPlotData(fig, ax[0], tempTPSall, chooseName(nodeType), '-o', chooseColor(nodeType))
        partialCDFPlotData(fig, ax[1], tempTPSall2, chooseName(nodeType), '-o', chooseColor(nodeType))
    for axs in ax:
        axs.set_xlim(0,1.01*maxTPS)
    ax[0].title.set_text(niceTestName[testNameMain])
    ax[1].title.set_text(niceTestName[testNameSecondary])
    partialCDFEnd(fig,ax,'', 'Mean Client Throughput [mbps]', '../exports/plots/'+makeFullScenarioName(testNameMain, numCLI, nodeTypes, nodeSplit)+'/'+str(globalCounter)+'_cdfMean'+direction[0]+'ThroughputsCutoff'+ str(cutoff) + str(nodeTypes) + 'compWith' + str(testNameSecondary) + '.pdf')
    partialCDFEndPNG(fig,ax,'', 'Mean Client Throughput [mbps]', '../exports/plots/'+makeFullScenarioName(testNameMain, numCLI, nodeTypes, nodeSplit)+'/'+str(globalCounter)+'_cdfMean'+direction[0]+'ThroughputsCutoff'+ str(cutoff) + str(nodeTypes) + 'compWith' + str(testNameSecondary) + '.png')


def plotRTOcdf(testName, numCLI, nodeTypes, nodeSplit):
    rtos = []
    numSession = 0
    numSessionWithRTO = 0
    fullScenarioName = makeFullScenarioName(testName, numCLI, nodeTypes, nodeSplit)
    file_to_read = '../exports/extracted/rto/' + fullScenarioName + '.csv'
    with open(file_to_read, mode='r') as readFile:
        csv_reader = csv.reader(readFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                rtos = row
            elif line_count == 1:
                numSession = row[0]
            elif line_count == 2:
                numSessionWithRTO = row[0]
            line_count += 1
    # print(rtos)
    print('Total Number of sessions at the SSH server: ' + str(numSession))
    print('Number of sessions at the SSH server where at least one retransmission timeout occured: ' + str(numSessionWithRTO))
    print('Percentage of sessions with a timeout: ' + str(numSessionWithRTO*100/numSession) + '%')
    fig, ax1 = partialCDFBegin(1)
    partialCDFPlotData(fig, ax1, rtos, 'SSH Server', '-o', chooseColor('hostSSH'))
    ax1.text(0.25,0.12, 'SSH server sessions - total: ' + str(int(numSession)), horizontalalignment='left', transform=ax1.transAxes)
    ax1.text(0.25,0.07, 'SSH server sessions - with timeout: ' + str(int(numSessionWithRTO)), horizontalalignment='left', transform=ax1.transAxes)
    ax1.text(0.25,0.02, 'Sessions with timeout: ' + str(round(numSessionWithRTO*100/numSession, 2)) + '%', horizontalalignment='left', transform=ax1.transAxes)
    partialCDFEnd(fig,ax1,'', 'RTO Value [s]', '../exports/plots/'+makeFullScenarioName(testName, numCLI, nodeTypes, nodeSplit)+'/'+str(globalCounter)+'_cdfRTO[\'serverSSH\'].pdf')

def plotSSHRTOcdfMultiTest(testNames, numCLIs, lineColors):
    fig, ax1 = partialCDFBegin(1)
    iterator = 0
    for testName in testNames:
        rtos = []
        numSession = 0
        numSessionWithRTO = 0
        fullScenarioName = str(testName) + '_' + str(numCLIs[iterator])
        file_to_read = '../exports/extracted/rto/' + fullScenarioName + '.csv'
        with open(file_to_read, mode='r') as readFile:
            csv_reader = csv.reader(readFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
            line_count = 0
            for row in csv_reader:
                if line_count == 0:
                    rtos = row
                elif line_count == 1:
                    numSession = row[0]
                elif line_count == 2:
                    numSessionWithRTO = row[0]
                line_count += 1
        # print(rtos)
        print('Total Number of sessions at the SSH server: ' + str(numSession))
        print('Number of sessions at the SSH server where at least one retransmission timeout occured: ' + str(numSessionWithRTO))
        print('Percentage of sessions with a timeout: ' + str(numSessionWithRTO*100/numSession) + '%')
        
        partialCDFPlotData(fig, ax1, rtos, testName, '-o', lineColors[iterator])
        ax1.text(0.25,0.02+iterator*0.05, testName + ' # Sessions: ' + str(int(numSession)) + '; With Timeout: ' + str(round(numSessionWithRTO*100/numSession, 2)) + '%', horizontalalignment='left', transform=ax1.transAxes, fontsize=20)
        iterator += 1
    partialCDFEndPNG(fig,ax1,'', 'RTO Value [s]', '../exports/plots/'+str(testNames)+'_sshRtoCDF.png')

def chooseColorNS(nodeSplit):
    if nodeSplit == [10,10,10,10]:
        return 'c'
    elif nodeSplit == [20,20,20,20]:
        return 'm'
    elif nodeSplit == [30,30,30,30]:
        return 'y'
    elif nodeSplit == [40,40,40,40]:
        return 'b'
    elif nodeSplit == [50,50,50,50]:
        return 'g'

def chooseNameNS(nodeSplit):
    if nodeSplit == [10,10,10,10]:
        return '10 clients per app'
    elif nodeSplit == [20,20,20,20]:
        return '20 clients per app'
    elif nodeSplit == [30,30,30,30]:
        return '30 clients per app'
    elif nodeSplit == [40,40,40,40]:
        return '40 clients per app'
    elif nodeSplit == [50,50,50,50]:
        return '50 clients per app'

def plotMeanDataTypeCdfMultiRun(testName, nodeTypes, nodeSplits, dataIdent, folderName, nodeTypesToPlot):
    fig, ax1 = partialCDFBegin(1)
    maxValue = 0
    for nodeSplit in nodeSplits:
        numCLI = sum(nodeSplit)
        df = importDF(testName, numCLI, nodeTypes, nodeSplit, folderName)
        for nodeType,numNodes in zip(nodeTypes,nodeSplit):
            if nodeType in nodeTypesToPlot:
                tempValue = []
                for nodeNum in range(numNodes):
                    colName = makeNodeIdentifier(nodeType, nodeNum) + " " + dataIdent + " Val"
                    data = df[colName].dropna().tolist()
                    if len(data) > 0: 
                        tempValue.append(statistics.mean(data))
                # print(tempValue)
                if maxValue < max(tempValue):
                    maxValue = max(tempValue)
                partialCDFPlotDataNoColor(fig, ax1, tempValue, nodeSplit, '-o')
    if dataIdent == 'Mos':
        ax1.set_xlim(0.95,5.05)
    else:
        ax1.set_xlim(0,1.01*maxValue)
    if not os.path.exists('../exports/plots/'+makeFullScenarioName(testName, 0, nodeTypes, [0,0,0,0])):
        os.makedirs('../exports/plots/'+makeFullScenarioName(testName, 0, nodeTypes, [0,0,0,0]))
    partialCDFEnd(fig,ax1,'', 'Mean Client ' + dataIdent + ' Value', '../exports/plots/'+makeFullScenarioName(testName, 0, nodeTypes, [0,0,0,0])+'/'+str(globalCounter)+'_meanCdf' + dataIdent + str(nodeTypesToPlot) + '.pdf')

def plotMultiTest(testName, nodeTypes, nodeSplits):
    for nodeType in nodeTypes:
        plotMeanDataTypeCdfMultiRun(testName, nodeTypes, nodeSplits, 'Mos', 'mos', [nodeType])
    plotMeanDataTypeCdfMultiRun(testName, nodeTypes, nodeSplits, 'RTT', 'rtt', ['hostSSH'])
    plotMeanDataTypeCdfMultiRun(testName, nodeTypes, nodeSplits, 'E2ED', 'e2ed', ['hostVIP'])
    plotMeanDataTypeCdfMultiRun(testName, nodeTypes, nodeSplits, 'PkLR', 'pklr', ['hostVIP'])

# plotMultiTest('baselineTestV3', ['hostVID', 'hostFDO', 'hostSSH', 'hostVIP'], [[10,10,10,10], [20,20,20,20], [30,30,30,30], [40,40,40,40], [50,50,50,50]])

# plotMeanDataTypeCdfMultiRun('singleAppTest_Video', ['hostVID', 'hostFDO', 'hostSSH', 'hostVIP'], [[i, 0, 0, 0] for i in range(1,14,1)], 'Mos', 'mos', ['hostVID'])
# plotMeanDataTypeCdfMultiRun('singleAppTest_SSH', ['hostVID', 'hostFDO', 'hostSSH', 'hostVIP'], [[0, 0, i, 0] for i in [1,5,10,15,20,25,30,35,40,45,50,55,60]], 'Mos', 'mos', ['hostSSH'])
# plotMeanDataTypeCdfMultiRun('singleAppTest_SSH', ['hostVID', 'hostFDO', 'hostSSH', 'hostVIP'], [[0, 0, i, 0] for i in [1,5,10,15,20,25,30,35,40,45,50,55,60]], 'RTT', 'rtt', ['hostSSH'])

def plotMosBaseSliComp(testNameBaseline, testName2sli, testName5sli, numCLI, nodeTypes, nodeSplit, cliType):
    matplotlib.rc('lines', linewidth=3.0)
    matplotlib.rc('lines', markersize=8)
    folderName = 'mos'
    dataIdent = 'Mos'
    df = importDF(testNameBaseline, numCLI, nodeTypes, nodeSplit, folderName)
    df2 = importDF(testName2sli, numCLI, nodeTypes, nodeSplit, folderName)
    df5 = importDF(testName5sli, numCLI, nodeTypes, nodeSplit, folderName)
    fig, ax = partialCDFBegin(1)
    maxValue = 0
    for nodeType,numNodes in zip(nodeTypes,nodeSplit):
        if nodeType == cliType:
            tempValue = []
            tempValue2 = []
            tempValue5 = []
            for nodeNum in range(numNodes):
                colName = makeNodeIdentifier(nodeType, nodeNum) + " " + dataIdent + " Val"
                tempValue.extend([normalizeQoE(nodeType, x) for x in df[colName].dropna().tolist()])
                tempValue2.extend([normalizeQoE(nodeType, x) for x in df2[colName].dropna().tolist()])
                tempValue5.extend([normalizeQoE(nodeType, x) for x in df5[colName].dropna().tolist()])
            # print(tempValue)
            if len(tempValue) > 0:
                if maxValue < max(tempValue):
                    maxValue = max(tempValue)
                if len(tempValue2) > 0:
                    if maxValue < max(tempValue2):
                        maxValue = max(tempValue2)
                partialCDFPlotData(fig, ax, tempValue, 'Baseline', '-', 'red')
                print(np.sort(tempValue)[(np.abs(np.linspace(0, 1, len(tempValue), endpoint=True) - 0.4)).argmin()])
                partialCDFPlotData(fig, ax, tempValue2, '2 Slices', '-', 'blue')
                ax.arrow(np.sort(tempValue)[(np.abs(np.linspace(0, 1, len(tempValue), endpoint=True) - 0.4)).argmin()], 0.4, np.sort(tempValue2)[(np.abs(np.linspace(0, 1, len(tempValue2), endpoint=True) - 0.4)).argmin()] - np.sort(tempValue)[(np.abs(np.linspace(0, 1, len(tempValue), endpoint=True) - 0.4)).argmin()], 0, width=0.008, head_width=0.04, head_length=0.08, color='blue', length_includes_head=True, overhang=0.2)
                partialCDFPlotData(fig, ax, tempValue5, '5 Slices', '--', 'green')
                ax.arrow(np.sort(tempValue)[(np.abs(np.linspace(0, 1, len(tempValue), endpoint=True) - 0.6)).argmin()], 0.6, np.sort(tempValue5)[(np.abs(np.linspace(0, 1, len(tempValue5), endpoint=True) - 0.6)).argmin()] - np.sort(tempValue)[(np.abs(np.linspace(0, 1, len(tempValue), endpoint=True) - 0.6)).argmin()], 0, width=0.008, head_width=0.04, head_length=0.08, color='green', length_includes_head=True, overhang=0.2)
    if dataIdent == 'Mos':
        ax.set_xlim(0.95,5.05)
    else:
        ax[0].set_xlim(0,1.01*maxValue)
    prePath = '../exports/plots/baseSlicingComps/'
    if not os.path.exists(prePath):
        os.makedirs(prePath)
    partialCDFEnd(fig,ax,'', 'Utility', prePath+str(globalCounter)+'_cdf_' + testNameBaseline + '_' + dataIdent + '_' + str(cliType) + '_compWith' + str(testName2sli) + '_and_' + testName5sli + '.pdf')
    partialCDFEndPNG(fig,ax,chooseName(cliType), 'Utility', prePath+str(globalCounter)+'_cdf_' + testNameBaseline + '_' + dataIdent + '_' + str(cliType) + '_compWith' + str(testName2sli) + '_and_' + testName5sli + '.png')

# plotMosBaseSliComp('baselineTest', 'baselineTestNS_2sli_LVD-BWS_AlgoTest_alpha05', 'baselineTestNS_5sli_AlgoTest_alpha05', 250, ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [50 for x in range(5)], 'hostVID')
# plotMosBaseSliComp('baselineTest', 'baselineTestNS_2sli_LVD-BWS_AlgoTest_alpha05', 'baselineTestNS_5sli_AlgoTest_alpha05', 250, ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [50 for x in range(5)], 'hostLVD')
# plotMosBaseSliComp('baselineTest', 'baselineTestNS_2sli_LVD-BWS_AlgoTest_alpha05', 'baselineTestNS_5sli_AlgoTest_alpha05', 250, ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [50 for x in range(5)], 'hostFDO')
# plotMosBaseSliComp('baselineTest', 'baselineTestNS_2sli_LVD-BWS_AlgoTest_alpha05', 'baselineTestNS_5sli_AlgoTest_alpha05', 250, ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [50 for x in range(5)], 'hostSSH')
# plotMosBaseSliComp('baselineTest', 'baselineTestNS_2sli_LVD-BWS_AlgoTest_alpha05', 'baselineTestNS_5sli_AlgoTest_alpha05', 250, ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [50 for x in range(5)], 'hostVIP')

# def makeFullRunName(testIdent, ls, tarQoE)

def plotMosVsNumUsers(testPrefix, linkSpeed, ceil):
    prePath = '../exports/extracted/mos2/'
    filenames = glob.glob(prePath+testPrefix+'*')

    numCLIs = {}
    meanMOSs = {}
    targetQoEs = {}
    runIdents = []

    # print(filenames)
    for filename in filenames:
        if '_R'+str(linkSpeed) in filename and '_C'+str(ceil) in filename:
            runName = filename.split('/')[-1].split('.')[0]
            print('Run:', runName)
            tarQoE = float(filename.split('_Q')[1].split('_')[0])/10
            print('\tTarget QoE:', tarQoE)
            numCliRun = int(filename.split('_VID')[0].split('_')[-1])
            print('\tNumber of clients:', numCliRun)
            runIdent = runName.split('_R')[0]
            if runIdent not in runIdents:
                numCLIs[runIdent] = []
                meanMOSs[runIdent] = []
                targetQoEs[runIdent] = []
                runIdents.append(runIdent)
            numCLIs[runIdent].append(numCliRun)
            targetQoEs[runIdent].append(tarQoE)
            runDF = pd.read_csv(filename)
            mosValDF = filterDFType(runDF, 'Val').dropna()
            mosValVidDF = filterDFType(mosValDF, 'VID').dropna()
            mosValLvdDF = filterDFType(mosValDF, 'LVD').dropna()
            mosValFdoDF = filterDFType(mosValDF, 'FDO').dropna()
            mosValSshDF = filterDFType(mosValDF, 'SSH').dropna()
            mosValVipDF = filterDFType(mosValDF, 'VIP').dropna()
            meanCliMOS = []
            meanVIDmos = []
            meanLVDmos = []
            meanFDOmos = []
            meanSSHmos = []
            meanVIPmos = []
            for col in mosValDF:
                meanCliMOS.append(statistics.mean(mosValDF[col].dropna().tolist()))
            for col in mosValVidDF:
                meanVIDmos.append(statistics.mean(mosValVidDF[col].dropna().tolist()))
            for col in mosValLvdDF:
                meanLVDmos.append(statistics.mean(mosValLvdDF[col].dropna().tolist()))
            for col in mosValFdoDF:
                meanFDOmos.append(statistics.mean(mosValFdoDF[col].dropna().tolist()))
            for col in mosValSshDF:
                meanSSHmos.append(statistics.mean(mosValSshDF[col].dropna().tolist()))
            for col in mosValVipDF:
                meanVIPmos.append(statistics.mean(mosValVipDF[col].dropna().tolist()))
            
            print('\tMean run MOS:', statistics.mean(meanCliMOS))
            meanMOSs[runIdent].append(statistics.mean(meanCliMOS))
            print('\tMean run VID MOS:', statistics.mean(meanVIDmos))
            print('\tMean run LVD MOS:', statistics.mean(meanLVDmos))
            print('\tMean run FDO MOS:', statistics.mean(meanFDOmos))
            print('\tMean run SSH MOS:', statistics.mean(meanSSHmos))
            print('\tMean run VIP MOS:', statistics.mean(meanVIPmos))
            # break
    print(numCLIs)
    print(targetQoEs)
    print(meanMOSs)

    fig, ax = plt.subplots(1, figsize=(16,12))
    for runIdent in runIdents:
        ax.plot(numCLIs[runIdent], meanMOSs[runIdent], 's-', label=runIdent)
    ax.plot(numCLIs[runIdent], targetQoEs[runIdent], 'D-', label='Target QoE')

    preOutPath = '../exports/plots/mosConf/'
    if not os.path.exists(preOutPath):
        os.makedirs(preOutPath)
    ax.set_ylim(1,5)
    plt.legend()
    plt.xlabel('Number of clients')
    plt.ylabel("QoE")
    outPath = preOutPath+'mos_R'+str(linkSpeed)+'_C'+str(ceil)+'.png'
    fig.savefig(outPath, dpi=100, bbox_inches='tight', format='png')
    plt.close('all')

def plot3DMosVsNumUsers(testPrefix, linkSpeed, ceil):
    prePath = '../exports/extracted/mos2/'
    filenames = glob.glob(prePath+testPrefix+'*')

    numCLIs = {}
    meanMOSs = {}
    meanMOSsVID = {}
    meanMOSsLVD = {}
    meanMOSsFDO = {}
    meanMOSsSSH = {}
    meanMOSsVIP = {}
    targetQoEs = {}
    runIdents = []

    # print(filenames)
    for filename in filenames:
        if '_R'+str(linkSpeed) in filename and '_C'+str(ceil) in filename:
            runName = filename.split('/')[-1].split('.')[0]
            print('Run:', runName)
            tarQoE = float(filename.split('_Q')[1].split('_')[0])/10
            print('\tTarget QoE:', tarQoE)
            numCliRun = int(filename.split('_VID')[0].split('_')[-1])
            print('\tNumber of clients:', numCliRun)
            runIdent = runName.split('_R')[0]
            if runIdent not in runIdents:
                numCLIs[runIdent] = []
                meanMOSs[runIdent] = []
                meanMOSsVID[runIdent] = []
                meanMOSsLVD[runIdent] = []
                meanMOSsFDO[runIdent] = []
                meanMOSsSSH[runIdent] = []
                meanMOSsVIP[runIdent] = []
                targetQoEs[runIdent] = []
                runIdents.append(runIdent)
            numCLIs[runIdent].append(numCliRun)
            targetQoEs[runIdent].append(tarQoE)
            runDF = pd.read_csv(filename)
            mosValDF = filterDFType(runDF, 'Val').dropna()
            mosValVidDF = filterDFType(mosValDF, 'VID').dropna()
            mosValLvdDF = filterDFType(mosValDF, 'LVD').dropna()
            mosValFdoDF = filterDFType(mosValDF, 'FDO').dropna()
            mosValSshDF = filterDFType(mosValDF, 'SSH').dropna()
            mosValVipDF = filterDFType(mosValDF, 'VIP').dropna()
            meanCliMOS = []
            meanVIDmos = []
            meanLVDmos = []
            meanFDOmos = []
            meanSSHmos = []
            meanVIPmos = []
            for col in mosValDF:
                meanCliMOS.append(statistics.mean(mosValDF[col].dropna().tolist()))
            for col in mosValVidDF:
                meanVIDmos.append(statistics.mean(mosValVidDF[col].dropna().tolist()))
            for col in mosValLvdDF:
                meanLVDmos.append(statistics.mean(mosValLvdDF[col].dropna().tolist()))
            for col in mosValFdoDF:
                meanFDOmos.append(statistics.mean(mosValFdoDF[col].dropna().tolist()))
            for col in mosValSshDF:
                meanSSHmos.append(statistics.mean(mosValSshDF[col].dropna().tolist()))
            for col in mosValVipDF:
                meanVIPmos.append(statistics.mean(mosValVipDF[col].dropna().tolist()))
            
            print('\tMean run MOS:', statistics.mean(meanCliMOS))
            meanMOSs[runIdent].append(statistics.mean(meanCliMOS))
            print('\tMean run VID MOS:', statistics.mean(meanVIDmos))
            meanMOSsVID[runIdent].append(statistics.mean(meanVIDmos))
            print('\tMean run LVD MOS:', statistics.mean(meanLVDmos))
            meanMOSsLVD[runIdent].append(statistics.mean(meanLVDmos))
            print('\tMean run FDO MOS:', statistics.mean(meanFDOmos))
            meanMOSsFDO[runIdent].append(statistics.mean(meanFDOmos))
            print('\tMean run SSH MOS:', statistics.mean(meanSSHmos))
            meanMOSsSSH[runIdent].append(statistics.mean(meanSSHmos))
            print('\tMean run VIP MOS:', statistics.mean(meanVIPmos))
            meanMOSsVIP[runIdent].append(statistics.mean(meanVIPmos))
            # break
    print(numCLIs)
    print(targetQoEs)
    print(meanMOSs)

    fig = plt.figure(figsize=(16,12))
    ax = fig.add_subplot(111, projection='3d')
    for runIdent in runIdents:
        numSli = 1
        if 'sli' in runIdent:
            numSli = int(runIdent.split('_')[1].split('sli')[0])
            if numSli == 5:
                numSli = 3
        ax.plot(numCLIs[runIdent], [numSli for _ in numCLIs[runIdent]], meanMOSs[runIdent], 's-', color='black', label='Mean QoE' if numSli == 1 else '')
        ax.plot(numCLIs[runIdent], [numSli for _ in numCLIs[runIdent]], targetQoEs[runIdent], 'D-', color='orange', label='Target QoE' if numSli == 1 else '')
        ax.plot(numCLIs[runIdent], [numSli for _ in numCLIs[runIdent]], meanMOSsVID[runIdent], 'o--', color=colorMapping['VID'], label='VoD' if numSli == 1 else '')
        ax.plot(numCLIs[runIdent], [numSli for _ in numCLIs[runIdent]], meanMOSsLVD[runIdent], 'o--', color=colorMapping['LVD'], label='Live' if numSli == 1 else '')
        ax.plot(numCLIs[runIdent], [numSli for _ in numCLIs[runIdent]], meanMOSsFDO[runIdent], 'o--', color=colorMapping['FDO'], label='Download' if numSli == 1 else '')
        ax.plot(numCLIs[runIdent], [numSli for _ in numCLIs[runIdent]], meanMOSsSSH[runIdent], 'o--', color=colorMapping['SSH'], label='SSH' if numSli == 1 else '')
        ax.plot(numCLIs[runIdent], [numSli for _ in numCLIs[runIdent]], meanMOSsVIP[runIdent], 'o--', color=colorMapping['VIP'], label='VoIP' if numSli == 1 else '')
        for numCli in numCLIs[runIdent]:
            ax.plot([numCli, numCli], [numSli, numSli], [1,5], '-', color='grey', alpha=0.8)

    preOutPath = '../exports/plots/mosConf/'
    if not os.path.exists(preOutPath):
        os.makedirs(preOutPath)
    ax.set_zlim(1,5)
    plt.legend(bbox_to_anchor=(1.2, 1), loc='upper right')
    ax.xaxis.labelpad=30
    ax.yaxis.labelpad=30
    ax.zaxis.labelpad=30
    ax.dist = 13
    ax.set_xlabel('Number of clients')
    ax.set_ylabel("Number of slices")
    ticks = [1, 2, 3]
    labels = ['1', '2', '5']
    plt.yticks(ticks, labels)
    ax.set_zlabel("QoE")
    ax.view_init(25, 30)
    outPath = preOutPath+'mos3D_R'+str(linkSpeed)+'_C'+str(ceil)+'.png'
    fig.savefig(outPath, dpi=100, bbox_inches='tight', format='png')
    plt.close('all')

colorPlt = ['white','green', 'blue', 'grey', 'grey', 'orange']

def plot3DMosVsNumUsersCeil(testPrefix, linkSpeed, ceils):
    prePath = '../exports/extracted/mos2/'
    filenames = glob.glob(prePath+testPrefix+'*')

    fig = plt.figure(figsize=(16,12))
    ax = fig.add_subplot(111, projection='3d')

    for ceil in ceils:
        numCLIs = {}
        meanMOSs = {}
        targetQoEs = {}
        runIdents = []

        # print(filenames)
        for filename in filenames:
            if '_R'+str(linkSpeed) in filename and '_C'+str(ceil) in filename:
                runName = filename.split('/')[-1].split('.')[0]
                print('Run:', runName)
                tarQoE = float(filename.split('_Q')[1].split('_')[0])/10
                print('\tTarget QoE:', tarQoE)
                numCliRun = int(filename.split('_VID')[0].split('_')[-1])
                print('\tNumber of clients:', numCliRun)
                runIdent = runName.split('_R')[0]
                if runIdent not in runIdents:
                    numCLIs[runIdent] = []
                    meanMOSs[runIdent] = []
                    targetQoEs[runIdent] = []
                    runIdents.append(runIdent)
                numCLIs[runIdent].append(numCliRun)
                targetQoEs[runIdent].append(tarQoE)
                runDF = pd.read_csv(filename)
                mosValDF = filterDFType(runDF, 'Val').dropna()
                meanCliMOS = []
                for col in mosValDF:
                    meanCliMOS.append(statistics.mean(mosValDF[col].dropna().tolist()))
                
                print('\tMean run MOS:', statistics.mean(meanCliMOS))
                meanMOSs[runIdent].append(statistics.mean(meanCliMOS))
                # break
        print(numCLIs)
        print(targetQoEs)
        print(meanMOSs)

        for runIdent in runIdents:
            numSli = 1
            if 'sli' in runIdent:
                numSli = int(runIdent.split('_')[1].split('sli')[0])
            ax.plot(numCLIs[runIdent], [ceils.index(ceil)+1 for _ in numCLIs[runIdent]], meanMOSs[runIdent], 's-', color=colorPlt[numSli], label=str(numSli)+' slices'if ceil == 100 else '')
            ax.plot(numCLIs[runIdent], [ceils.index(ceil)+1 for _ in numCLIs[runIdent]], targetQoEs[runIdent], 'D-', color='red', label='Target QoE' if numSli == 1 and ceil == 100 else '')
            for numCli in numCLIs[runIdent]:
                ax.plot([numCli, numCli], [ceils.index(ceil)+1, ceils.index(ceil)+1], [1,5], '-', color='grey', alpha=0.8)

    preOutPath = '../exports/plots/mosConf/'
    if not os.path.exists(preOutPath):
        os.makedirs(preOutPath)
    ax.set_zlim(1,5)
    plt.legend(bbox_to_anchor=(1.2, 1), loc='upper right')
    ax.xaxis.labelpad=30
    ax.yaxis.labelpad=30
    ax.zaxis.labelpad=30
    ax.dist = 13
    ax.set_xlabel('Number of clients')
    ax.set_ylabel('Set ceiling rate in % of assured rate')
    ticks = [1, 2, 3, 4]
    labels = ceils
    plt.yticks(ticks, labels)
    ax.set_zlabel("QoE")
    ax.view_init(25, 30)
    outPath = preOutPath+'mosCeil3D_R'+str(linkSpeed)+'.png'
    fig.savefig(outPath, dpi=100, bbox_inches='tight', format='png')
    plt.close('all')

qoeCl = {'3.0' : 'green',
         '3.5' : 'blue',
         '4.0' : 'orange'}
        
qoeLs = {'3.0' : 'solid',
         '3.5' : 'dashed',
         '4.0' : 'dotted'}

def plotMosVsCeil(testPrefix, linkSpeed, ceils):
    prePath = '../exports/extracted/mos2/'
    filenames = glob.glob(prePath+testPrefix+'*')

    fig, ax = plt.subplots(1, figsize=(16,12))
    
    curveIdents = []
    mosPlotVals = {}

    # print(filenames)
    for ceil in ceils:
        numCLIs = {}
        meanMOSs = {}
        targetQoEs = {}
        runIdents = []
        for filename in filenames:
            if '_R'+str(linkSpeed) in filename and '_C'+str(ceil) in filename:
                runName = filename.split('/')[-1].split('.')[0]
                print('Run:', runName)
                tarQoE = float(filename.split('_Q')[1].split('_')[0])/10
                print('\tTarget QoE:', tarQoE)
                numCliRun = int(filename.split('_VID')[0].split('_')[-1])
                print('\tNumber of clients:', numCliRun)
                runIdent = runName.split('_R')[0]
                if runIdent not in runIdents:
                    numCLIs[runIdent] = []
                    meanMOSs[runIdent] = []
                    targetQoEs[runIdent] = []
                    runIdents.append(runIdent)
                numCLIs[runIdent].append(numCliRun)
                targetQoEs[runIdent].append(tarQoE)
                runDF = pd.read_csv(filename)
                mosValDF = filterDFType(runDF, 'Val').dropna()
                meanCliMOS = []
                for col in mosValDF:
                    meanCliMOS.append(statistics.mean(mosValDF[col].dropna().tolist()))

                curveIdent = runIdent + '_Q' + str(tarQoE)
                if curveIdent not in curveIdents:
                    curveIdents.append(curveIdent)
                    mosPlotVals[curveIdent] = []
                mosPlotVals[curveIdent].append(statistics.mean(meanCliMOS))


                print('\tMean run MOS:', statistics.mean(meanCliMOS))
                meanMOSs[runIdent].append(statistics.mean(meanCliMOS))
            # break
        print(numCLIs)
        print(targetQoEs)
        print(meanMOSs)

    for curveIdent in curveIdents:
        sli = 'Base'
        ls = 'solid'
        cl = 'green'
        if 'sli' in curveIdent:
            sli = str(curveIdent.split('_')[1].split('sli')[0]) + ' Slices'
            if sli == '2 Slices':
                ls = 'dashed'
                cl = 'blue'
            if sli == '5 Slices':
                ls = 'dotted'
                cl = 'orange'


        tarQoE = str(curveIdent.split('_Q')[1])
        lbl = 'Target QoE: ' + tarQoE + '; ' + sli

        ax.plot(ceils, mosPlotVals[curveIdent], marker='s', linestyle=qoeLs[tarQoE], color=cl, label=lbl)
    # ax.plot(numCLIs[runIdent], targetQoEs[runIdent], 'D-', label='Target QoE')

    preOutPath = '../exports/plots/mosConf/'
    if not os.path.exists(preOutPath):
        os.makedirs(preOutPath)
    # ax.set_ylim(1,5)
    plt.legend(fontsize=20)
    plt.xlabel('Ceil rate in % of Assured Rate')
    plt.ylabel("QoE")
    outPath = preOutPath+'meanMosVsCeil_R'+str(linkSpeed)+'.png'
    fig.savefig(outPath, dpi=100, bbox_inches='tight', format='png')
    plt.close('all')

def plotMosVsNumCli(testPrefix, linkSpeed, ceils):
    prePath = '../exports/extracted/mos2/'
    filenames = glob.glob(prePath+testPrefix+'*')

    fig, ax = plt.subplots(1, figsize=(16,12))
    
    curveIdents = []
    mosPlotVals = {}

    # print(filenames)
    # for ceil in ceils:
    numCLIs = {}
    meanMOSs = {}
    targetQoEs = {}
    runIdents = []
    for ceil in ceils:
        for filename in filenames:
            # print(filename)
            if '_R'+str(linkSpeed) in filename and '_C'+str(ceil) in filename:
                runName = filename.split('/')[-1].split('.')[0]
                print('Run:', runName)
                tarQoE = float(filename.split('_Q')[1].split('_')[0])/10
                print('\tTarget QoE:', tarQoE)
                numCliRun = int(filename.split('_VID')[0].split('_')[-1])
                print('\tNumber of clients:', numCliRun)
                runIdent = runName.split('_R')[0]+'_C'+str(ceil)
                if runIdent not in runIdents:
                    numCLIs[runIdent] = []
                    meanMOSs[runIdent] = []
                    targetQoEs[runIdent] = []
                    runIdents.append(runIdent)
                numCLIs[runIdent].append(numCliRun)
                targetQoEs[runIdent].append(tarQoE)
                runDF = pd.read_csv(filename)
                mosValDF = filterDFType(runDF, 'Val').dropna()
                meanCliMOS = []
                for col in mosValDF:
                    meanCliMOS.append(statistics.mean(mosValDF[col].dropna().tolist()))

                # curveIdent = runIdent + '_Q' + str(tarQoE)
                # if curveIdent not in curveIdents:
                #     curveIdents.append(curveIdent)
                #     mosPlotVals[curveIdent] = []
                # mosPlotVals[curveIdent].append(statistics.mean(meanCliMOS))


                print('\tMean run MOS:', statistics.mean(meanCliMOS))
                meanMOSs[runIdent].append(statistics.mean(meanCliMOS))
                # break
    print(numCLIs)
    print(targetQoEs)
    print(meanMOSs)

    for runIdent in runIdents:
        sli = 'Base'
        cl = 'green'
        if 'sli' in runIdent:
            sli = str(runIdent.split('_')[1].split('sli')[0]) + ' Slices'
            if sli == '2 Slices':
                cl = 'blue'
            if sli == '5 Slices':
                cl = 'orange'

        ceil1 = str(runIdent.split('_C')[1])
        lbl = 'Ceil of: ' + ceil1 + '%; ' + sli
        ls = 'solid'
        if ceil1 == '110':
            ls = 'dashed'
        if ceil1 == '125':
            ls = 'dashdot'
        if ceil1 == '140':
            ls = 'dotted'
        ax.plot(numCLIs[runIdent], meanMOSs[runIdent], 's-', marker='s', linestyle=ls, color=cl, label=lbl)
    ax.plot(numCLIs[runIdent], targetQoEs[runIdent], 'D-', color='red', label='Target QoE')

    preOutPath = '../exports/plots/mosConf/'
    if not os.path.exists(preOutPath):
        os.makedirs(preOutPath)
    # ax.set_ylim(1,5)
    plt.legend(fontsize=20)
    plt.xlabel('Number of clients')
    plt.ylabel("QoE")
    outPath = preOutPath+'meanMosVsCliNum_R'+str(linkSpeed)+'.png'
    fig.savefig(outPath, dpi=100, bbox_inches='tight', format='png')
    plt.close('all')


def plotMosVsTarget(testPrefix, linkSpeed, ceils):
    prePath = '../exports/extracted/mos2/'
    filenames = glob.glob(prePath+testPrefix+'*')

    fig, ax = plt.subplots(1, figsize=(16,12))
    
    curveIdents = []
    mosPlotVals = {}

    # print(filenames)
    # for ceil in ceils:
    numCLIs = {}
    meanMOSs = {}
    targetQoEs = {}
    runIdents = []
    for ceil in ceils:
        for filename in filenames:
            # print(filename)
            if '_R'+str(linkSpeed) in filename and '_C'+str(ceil) in filename:
                runName = filename.split('/')[-1].split('.')[0]
                print('Run:', runName)
                tarQoE = float(filename.split('_Q')[1].split('_')[0])/10
                print('\tTarget QoE:', tarQoE)
                numCliRun = int(filename.split('_VID')[0].split('_')[-1])
                print('\tNumber of clients:', numCliRun)
                runIdent = runName.split('_R')[0]+'_C'+str(ceil)
                if runIdent not in runIdents:
                    numCLIs[runIdent] = []
                    meanMOSs[runIdent] = []
                    targetQoEs[runIdent] = []
                    runIdents.append(runIdent)
                numCLIs[runIdent].append(numCliRun)
                targetQoEs[runIdent].append(tarQoE)
                runDF = pd.read_csv(filename)
                mosValDF = filterDFType(runDF, 'Val').dropna()
                meanCliMOS = []
                for col in mosValDF:
                    meanCliMOS.append(statistics.mean(mosValDF[col].dropna().tolist()))

                # curveIdent = runIdent + '_Q' + str(tarQoE)
                # if curveIdent not in curveIdents:
                #     curveIdents.append(curveIdent)
                #     mosPlotVals[curveIdent] = []
                # mosPlotVals[curveIdent].append(statistics.mean(meanCliMOS))


                print('\tMean run MOS:', statistics.mean(meanCliMOS))
                meanMOSs[runIdent].append(statistics.mean(meanCliMOS))
                # break
    print(numCLIs)
    print(targetQoEs)
    print(meanMOSs)

    for runIdent in runIdents:
        sli = 'Base'
        cl = 'green'
        if 'sli' in runIdent:
            sli = str(runIdent.split('_')[1].split('sli')[0]) + ' Slices'
            if sli == '2 Slices':
                cl = 'blue'
            if sli == '5 Slices':
                cl = 'orange'

        ceil1 = str(runIdent.split('_C')[1])
        lbl = 'Ceil of: ' + ceil1 + '%; ' + sli
        ls = 'solid'
        if ceil1 == '110':
            ls = 'dashed'
        if ceil1 == '125':
            ls = 'dashdot'
        if ceil1 == '140':
            ls = 'dotted'
        ax.plot(targetQoEs[runIdent], meanMOSs[runIdent], 's-', marker='s', linestyle=ls, color=cl, label=lbl)
    # ax.plot(numCLIs[runIdent], targetQoEs[runIdent], 'D-', color='red', label='Target QoE')

    preOutPath = '../exports/plots/mosConf/'
    if not os.path.exists(preOutPath):
        os.makedirs(preOutPath)
    # ax.set_ylim(1,5)
    plt.legend(fontsize=20)
    plt.xlabel('Target QoE')
    plt.ylabel("QoE")
    outPath = preOutPath+'meanMosVsTargetQoE_R'+str(linkSpeed)+'.png'
    fig.savefig(outPath, dpi=100, bbox_inches='tight', format='png')
    plt.close('all')


def plotMosVsSlices(testPrefix, linkSpeed, ceils, qs):
    prePath = '../exports/extracted/mos2/'
    filenames = glob.glob(prePath+testPrefix+'*')

    fig, ax = plt.subplots(1, figsize=(16,12))

    numCLIs = {}
    meanMOSs = {}
    targetQoEs = {}
    numSlices = {}
    runIdents = []
    
    for ceil in ceils:
        for q in qs:
            for filename in filenames:
                # print(filename)
                if '_R'+str(linkSpeed) in filename and '_Q'+str(q) in filename and '_C'+str(ceil) in filename:
                    runName = filename.split('/')[-1].split('.')[0]
                    print('Run:', runName)
                    numSli = 1
                    if 'sli' in runName:
                        numSli = int(runName.split('sli')[0].split('_')[1])
                    tarQoE = float(filename.split('_Q')[1].split('_')[0])/10
                    print('\tTarget QoE:', tarQoE)
                    numCliRun = int(filename.split('_VID')[0].split('_')[-1])
                    print('\tNumber of clients:', numCliRun)
                    runIdent = 'C'+str(ceil)+'_Q'+str(q)
                    if runIdent not in runIdents:
                        numCLIs[runIdent] = []
                        meanMOSs[runIdent] = []
                        targetQoEs[runIdent] = []
                        numSlices[runIdent] = []
                        runIdents.append(runIdent)
                    numCLIs[runIdent].append(numCliRun)
                    targetQoEs[runIdent].append(tarQoE)
                    numSlices[runIdent].append(numSli)
                    runDF = pd.read_csv(filename)
                    mosValDF = filterDFType(runDF, 'Val').dropna()
                    meanCliMOS = []
                    for col in mosValDF:
                        meanCliMOS.append(statistics.mean(mosValDF[col].dropna().tolist()))

                    # curveIdent = runIdent + '_Q' + str(tarQoE)
                    # if curveIdent not in curveIdents:
                    #     curveIdents.append(curveIdent)
                    #     mosPlotVals[curveIdent] = []
                    # mosPlotVals[curveIdent].append(statistics.mean(meanCliMOS))


                    print('\tMean run MOS:', statistics.mean(meanCliMOS))
                    meanMOSs[runIdent].append(statistics.mean(meanCliMOS))
                    # break
    print(numCLIs)
    print(targetQoEs)
    print(meanMOSs)
    print(numSlices)

    for runIdent in runIdents:
        # print(runIdent)
        ceil1 = str(runIdent.split('C')[1].split('_Q')[0])
        cl = 'black'
        if ceil1 == '110':
            cl = 'green'
        if ceil1 == '125':
            cl = 'blue'
        if ceil1 == '140':
            cl = 'orange'
        tqoe = str(runIdent.split('_Q')[1])
        ls = 'solid'
        if tqoe == '35':
            ls = 'dashed'
        if tqoe == '40':
            ls = 'dotted'

        lbl = 'Ceil of: ' + ceil1 + '%; Target QoE:' + str(float(tqoe)/10)
        

        arrNumSli = [1,2,3]
        arrMeanMos = [x for _,x in sorted(zip(numSlices[runIdent],meanMOSs[runIdent]))]

        ax.plot(arrNumSli, arrMeanMos, 's-', marker='s', linestyle=ls, color=cl, label=lbl)
    # # ax.plot(numCLIs[runIdent], targetQoEs[runIdent], 'D-', color='red', label='Target QoE')

    preOutPath = '../exports/plots/mosConf/'
    if not os.path.exists(preOutPath):
        os.makedirs(preOutPath)
    ax.set_ylim(3.3,4.3)
    ticks = [1, 2, 3]
    labels = [1,2,5]
    plt.xticks(ticks, labels)
    plt.legend(fontsize=20)
    plt.xlabel('Number of Slices')
    plt.ylabel("QoE")
    outPath = preOutPath+'meanMosVsNumSlices_R'+str(linkSpeed)+'.png'
    fig.savefig(outPath, dpi=100, bbox_inches='tight', format='png')
    plt.close('all')


def plotMosVsSlicesSplit(testPrefix, linkSpeed, ceils, qs):
    prePath = '../exports/extracted/mos2/'
    filenames = glob.glob(prePath+testPrefix+'*')

    
    for ceil in ceils:
        fig, ax = plt.subplots(1, figsize=(16,12))

        numCLIs = {}
        meanMOSs = {}
        targetQoEs = {}
        numSlices = {}
        runIdents = []
        for q in qs:
            for filename in filenames:
                # print(filename)
                if '_R'+str(linkSpeed) in filename and '_Q'+str(q) in filename and '_C'+str(ceil) in filename:
                    runName = filename.split('/')[-1].split('.')[0]
                    print('Run:', runName)
                    numSli = 1
                    if 'sli' in runName:
                        numSli = int(runName.split('sli')[0].split('_')[1])
                    tarQoE = float(filename.split('_Q')[1].split('_')[0])/10
                    print('\tTarget QoE:', tarQoE)
                    numCliRun = int(filename.split('_VID')[0].split('_')[-1])
                    print('\tNumber of clients:', numCliRun)
                    runIdent = 'C'+str(ceil)+'_Q'+str(q)
                    if runIdent not in runIdents:
                        numCLIs[runIdent] = []
                        meanMOSs[runIdent] = []
                        targetQoEs[runIdent] = []
                        numSlices[runIdent] = []
                        runIdents.append(runIdent)
                    numCLIs[runIdent].append(numCliRun)
                    targetQoEs[runIdent].append(tarQoE)
                    numSlices[runIdent].append(numSli)
                    runDF = pd.read_csv(filename)
                    mosValDF = filterDFType(runDF, 'Val').dropna()
                    meanCliMOS = []
                    for col in mosValDF:
                        meanCliMOS.append(statistics.mean(mosValDF[col].dropna().tolist()))

                    # curveIdent = runIdent + '_Q' + str(tarQoE)
                    # if curveIdent not in curveIdents:
                    #     curveIdents.append(curveIdent)
                    #     mosPlotVals[curveIdent] = []
                    # mosPlotVals[curveIdent].append(statistics.mean(meanCliMOS))


                    print('\tMean run MOS:', statistics.mean(meanCliMOS))
                    meanMOSs[runIdent].append(statistics.mean(meanCliMOS))
                    # break
        print(numCLIs)
        print(targetQoEs)
        print(meanMOSs)
        print(numSlices)

        for runIdent in runIdents:
            # print(runIdent)
            ceil1 = str(runIdent.split('C')[1].split('_Q')[0])
            cl = 'black'
            if ceil1 == '110':
                cl = 'green'
            if ceil1 == '125':
                cl = 'blue'
            if ceil1 == '140':
                cl = 'orange'
            tqoe = str(runIdent.split('_Q')[1])
            ls = 'solid'
            if tqoe == '35':
                ls = 'dashed'
            if tqoe == '40':
                ls = 'dotted'

            lbl = 'Ceil of: ' + ceil1 + '%; Target QoE:' + str(float(tqoe)/10)
            

            arrNumSli = [1,2,3]
            arrMeanMos = [x for _,x in sorted(zip(numSlices[runIdent],meanMOSs[runIdent]))]

            ax.plot(arrNumSli, arrMeanMos, 's-', marker='s', linestyle=ls, color=cl, label=lbl)
        # # ax.plot(numCLIs[runIdent], targetQoEs[runIdent], 'D-', color='red', label='Target QoE')

        preOutPath = '../exports/plots/mosConf/'
        if not os.path.exists(preOutPath):
            os.makedirs(preOutPath)
        ax.set_ylim(3.3,4.3)
        ticks = [1, 2, 3]
        labels = [1,2,5]
        plt.xticks(ticks, labels)
        plt.legend(fontsize=20)
        plt.xlabel('Number of Slices')
        plt.ylabel("QoE")
        outPath = preOutPath+'meanMosVsNumSlices_R'+str(linkSpeed)+'_C'+str(ceil)+'.png'
        fig.savefig(outPath, dpi=100, bbox_inches='tight', format='png')
        plt.close('all')


def plotAvgTPVsNumCli(testPrefix, linkSpeed, ceils, simTime):
    prePath = '../exports/extracted/throughputs/'
    filenames = glob.glob(prePath+testPrefix+'*Downlink*')

    fig, ax = plt.subplots(1, figsize=(16,12))
    
    curveIdents = []
    mosPlotVals = {}

    # print(filenames)
    # for ceil in ceils:
    numCLIs = {}
    meanTPs = {}
    targetQoEs = {}
    runIdents = []
    for ceil in ceils:
        for filename in filenames:
            # print(filename)
            if '_R'+str(linkSpeed) in filename and '_C'+str(ceil) in filename:
                runName = filename.split('/')[-1].split('.')[0]
                print('Run:', runName)
                tarQoE = float(filename.split('_Q')[1].split('_')[0])/10
                print('\tTarget QoE:', tarQoE)
                numCliRun = int(filename.split('_VID')[0].split('_')[-1])
                print('\tNumber of clients:', numCliRun)
                runIdent = runName.split('_R')[0]+'_C'+str(ceil)
                if runIdent not in runIdents:
                    numCLIs[runIdent] = []
                    meanTPs[runIdent] = []
                    targetQoEs[runIdent] = []
                    runIdents.append(runIdent)
                numCLIs[runIdent].append(numCliRun)
                targetQoEs[runIdent].append(tarQoE)
                runDF = pd.read_csv(filename)
                mosValDF = filterDFType(runDF, 'resAllocLink0').dropna()
                print('Average Throughput:',mosValDF['Downlink Throughput resAllocLink0'].sum()/simTime, 'kbps')
                meanTPs[runIdent].append(mosValDF['Downlink Throughput resAllocLink0'].sum()/simTime)
                # print('Average Resource Utilization:',mosValDF['Downlink Throughput resAllocLink0'].sum()/(simTime*linkSpeed*10), '%')

    print(numCLIs)
    print(targetQoEs)
    print(meanTPs)

    for runIdent in runIdents:
        sli = 'Base'
        cl = 'green'
        if 'sli' in runIdent:
            sli = str(runIdent.split('_')[1].split('sli')[0]) + ' Slices'
            if sli == '2 Slices':
                cl = 'blue'
            if sli == '5 Slices':
                cl = 'orange'

        ceil1 = str(runIdent.split('_C')[1])
        lbl = 'Ceil of: ' + ceil1 + '%; ' + sli
        ls = 'solid'
        if ceil1 == '110':
            ls = 'dashed'
        if ceil1 == '125':
            ls = 'dashdot'
        if ceil1 == '140':
            ls = 'dotted'
        ax.plot(numCLIs[runIdent], meanTPs[runIdent], 's-', marker='s', linestyle=ls, color=cl, label=lbl)
    ax.plot(numCLIs[runIdent], [linkSpeed*1000 for _ in numCLIs[runIdent]], 'D-', color='red', label='System capacity')

    preOutPath = '../exports/plots/tpConf/'
    if not os.path.exists(preOutPath):
        os.makedirs(preOutPath)
    # ax.set_ylim(1,5)
    plt.legend(fontsize=20)
    plt.xlabel('Number of clients')
    plt.ylabel("Average System Throughput [kbps]")
    outPath = preOutPath+'meanTPVsCliNum_R'+str(linkSpeed)+'.png'
    fig.savefig(outPath, dpi=100, bbox_inches='tight', format='png')
    plt.close('all')



def plotUtilVsSlices(testPrefix, linkSpeed, ceils, qs, simTime):
    prePath = '../exports/extracted/throughputs/'
    filenames = glob.glob(prePath+testPrefix+'*Downlink*')

    fig, ax = plt.subplots(1, figsize=(16,12))

    numCLIs = {}
    meanUtils = {}
    targetQoEs = {}
    numSlices = {}
    runIdents = []
    
    for ceil in ceils:
        for q in qs:
            for filename in filenames:
                # print(filename)
                if '_R'+str(linkSpeed) in filename and '_Q'+str(q) in filename and '_C'+str(ceil) in filename:
                    runName = filename.split('/')[-1].split('.')[0]
                    print('Run:', runName)
                    numSli = 1
                    if 'sli' in runName:
                        numSli = int(runName.split('sli')[0].split('_')[1])
                    tarQoE = float(filename.split('_Q')[1].split('_')[0])/10
                    print('\tTarget QoE:', tarQoE)
                    numCliRun = int(filename.split('_VID')[0].split('_')[-1])
                    print('\tNumber of clients:', numCliRun)
                    runIdent = 'C'+str(ceil)+'_Q'+str(q)
                    if runIdent not in runIdents:
                        numCLIs[runIdent] = []
                        meanUtils[runIdent] = []
                        targetQoEs[runIdent] = []
                        numSlices[runIdent] = []
                        runIdents.append(runIdent)
                    numCLIs[runIdent].append(numCliRun)
                    targetQoEs[runIdent].append(tarQoE)
                    numSlices[runIdent].append(numSli)
                    runDF = pd.read_csv(filename)
                    mosValDF = filterDFType(runDF, 'resAllocLink0').dropna()
                    # meanCliMOS = []
                    
                    # for col in mosValDF:
                    #     meanCliMOS.append(statistics.mean(mosValDF[col].dropna().tolist()))

                    # curveIdent = runIdent + '_Q' + str(tarQoE)
                    # if curveIdent not in curveIdents:
                    #     curveIdents.append(curveIdent)
                    #     mosPlotVals[curveIdent] = []
                    # mosPlotVals[curveIdent].append(statistics.mean(meanCliMOS))
                    meanUtils[runIdent].append(mosValDF['Downlink Throughput resAllocLink0'].sum()/(simTime*linkSpeed*10))
                    # break
    print(numCLIs)
    print(targetQoEs)
    print(meanUtils)
    print(numSlices)

    for runIdent in runIdents:
        # print(runIdent)
        ceil1 = str(runIdent.split('C')[1].split('_Q')[0])
        cl = 'black'
        if ceil1 == '110':
            cl = 'green'
        if ceil1 == '125':
            cl = 'blue'
        if ceil1 == '140':
            cl = 'orange'
        tqoe = str(runIdent.split('_Q')[1])
        ls = 'solid'
        if tqoe == '35':
            ls = 'dashed'
        if tqoe == '40':
            ls = 'dotted'

        lbl = 'Ceil of: ' + ceil1 + '%; Target QoE:' + str(float(tqoe)/10)
        

        arrNumSli = [1,2,3]
        arrMeanMos = [x for _,x in sorted(zip(numSlices[runIdent],meanUtils[runIdent]))]

        ax.plot(arrNumSli, arrMeanMos, 's-', marker='s', linestyle=ls, color=cl, label=lbl)

    preOutPath = '../exports/plots/tpConf/'
    if not os.path.exists(preOutPath):
        os.makedirs(preOutPath)
    ax.set_ylim(65,90)
    ticks = [1, 2, 3]
    labels = [1,2,5]
    plt.xticks(ticks, labels)
    plt.legend(fontsize=20)
    plt.xlabel('Number of Slices')
    plt.ylabel("System Utilization [%]")
    outPath = preOutPath+'meanUtilVsNumSlices_R'+str(linkSpeed)+'.png'
    fig.savefig(outPath, dpi=100, bbox_inches='tight', format='png')
    plt.close('all')

def plotUtilVsSlicesSplit(testPrefix, linkSpeed, ceils, qs, simTime):
    prePath = '../exports/extracted/throughputs/'
    filenames = glob.glob(prePath+testPrefix+'*Downlink*')

    
    for ceil in ceils:
        fig, ax = plt.subplots(1, figsize=(16,12))

        numCLIs = {}
        meanUtils = {}
        targetQoEs = {}
        numSlices = {}
        runIdents = []
        for q in qs:
            for filename in filenames:
                # print(filename)
                if '_R'+str(linkSpeed) in filename and '_Q'+str(q) in filename and '_C'+str(ceil) in filename:
                    runName = filename.split('/')[-1].split('.')[0]
                    print('Run:', runName)
                    numSli = 1
                    if 'sli' in runName:
                        numSli = int(runName.split('sli')[0].split('_')[1])
                    tarQoE = float(filename.split('_Q')[1].split('_')[0])/10
                    print('\tTarget QoE:', tarQoE)
                    numCliRun = int(filename.split('_VID')[0].split('_')[-1])
                    print('\tNumber of clients:', numCliRun)
                    runIdent = 'C'+str(ceil)+'_Q'+str(q)
                    if runIdent not in runIdents:
                        numCLIs[runIdent] = []
                        meanUtils[runIdent] = []
                        targetQoEs[runIdent] = []
                        numSlices[runIdent] = []
                        runIdents.append(runIdent)
                    numCLIs[runIdent].append(numCliRun)
                    targetQoEs[runIdent].append(tarQoE)
                    numSlices[runIdent].append(numSli)
                    runDF = pd.read_csv(filename)
                    mosValDF = filterDFType(runDF, 'resAllocLink0').dropna()
                    # meanCliMOS = []
                    
                    # for col in mosValDF:
                    #     meanCliMOS.append(statistics.mean(mosValDF[col].dropna().tolist()))

                    # curveIdent = runIdent + '_Q' + str(tarQoE)
                    # if curveIdent not in curveIdents:
                    #     curveIdents.append(curveIdent)
                    #     mosPlotVals[curveIdent] = []
                    # mosPlotVals[curveIdent].append(statistics.mean(meanCliMOS))
                    meanUtils[runIdent].append(mosValDF['Downlink Throughput resAllocLink0'].sum()/(simTime*linkSpeed*10))
                    # break
        print(numCLIs)
        print(targetQoEs)
        print(meanUtils)
        print(numSlices)

        for runIdent in runIdents:
            # print(runIdent)
            ceil1 = str(runIdent.split('C')[1].split('_Q')[0])
            cl = 'black'
            if ceil1 == '110':
                cl = 'green'
            if ceil1 == '125':
                cl = 'blue'
            if ceil1 == '140':
                cl = 'orange'
            tqoe = str(runIdent.split('_Q')[1])
            ls = 'solid'
            if tqoe == '35':
                ls = 'dashed'
            if tqoe == '40':
                ls = 'dotted'

            lbl = 'Ceil of: ' + ceil1 + '%; Target QoE:' + str(float(tqoe)/10)
            

            arrNumSli = [1,2,3]
            arrMeanMos = [x for _,x in sorted(zip(numSlices[runIdent],meanUtils[runIdent]))]

            ax.plot(arrNumSli, arrMeanMos, 's-', marker='s', linestyle=ls, color=cl, label=lbl)

        preOutPath = '../exports/plots/tpConf/'
        if not os.path.exists(preOutPath):
            os.makedirs(preOutPath)
        ax.set_ylim(65,90)
        ticks = [1, 2, 3]
        labels = [1,2,5]
        plt.xticks(ticks, labels)
        plt.legend(fontsize=20)
        plt.xlabel('Number of Slices')
        plt.ylabel("System Utilization [%]")
        outPath = preOutPath+'meanUtilVsNumSlices_R'+str(linkSpeed)+'_C'+str(ceil)+'.png'
        fig.savefig(outPath, dpi=100, bbox_inches='tight', format='png')
        plt.close('all')


linkSpeeds = [100, 200]
ceil = [100, 110, 125, 140]
qs = [30, 35, 40]
for ls in linkSpeeds:
    # plotMosVsNumCli('liteChtb', ls, ceil)
    # plotMosVsTarget('liteChtb', ls, ceil)
    # plot3DMosVsNumUsersCeil('liteChtb', ls, ceil)
    # plotMosVsCeil('liteChtb', ls, ceil)
    # for c in ceil:
    #     plotMosVsNumUsers('liteChtb', ls, c)
    #     plot3DMosVsNumUsers('liteChtb', ls, c)
    # plotMosVsSlices('liteChtb', ls, ceil, qs)
    # plotMosVsSlicesSplit('liteChtb', ls, ceil, qs)
    # plotUtilVsSlicesSplit('liteChtb', ls, ceil, qs, 400)
    plotUtilVsSlices('liteChtb', ls, ceil, qs, 400)
    # plotAvgTPVsNumCli('liteChtb', ls, ceil, 400)