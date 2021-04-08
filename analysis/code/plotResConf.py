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
# print(colormap)
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
    'rtt' : 'Round Trip Time [s]',
    'rto' : 'Retransmission Timeout [???]'
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


def plotMosVsSlicesSplit(testPrefix, linkSpeed, ceils, qs, prio):
    prePath = '../exports/extracted/mos2/'
    filenames = glob.glob(prePath+testPrefix+'*')
    # print(filenames)
    
    for ceil in ceils:
        fig, ax = plt.subplots(1, figsize=(16,12))

        numCLIs = {}
        meanMOSs = {}
        targetQoEs = {}
        numSlices = {}
        runIdents = []
        for q in qs:
            print(q)
            for filename in filenames:
                print(filename)
                print('_R'+str(linkSpeed), '_Q'+str(q), '_C'+str(ceil))
                if '_R'+str(linkSpeed) in filename and '_Q'+str(q) in filename and '_C'+str(ceil) in filename and '_P'+str(prio) in filename:
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
        outPath = preOutPath+'meanMosVsNumSlices_'+testPrefix+'_R'+str(linkSpeed)+'_C'+str(ceil)+'_P'+str(prio)+'.png'
        fig.savefig(outPath, dpi=100, bbox_inches='tight', format='png')
        plt.close('all')


def plotMosVsSlicesSplitAppType(testPrefix, linkSpeed, ceils, qs, prio, appTypes):
    prePath = '../exports/extracted/mos2/'
    filenames = glob.glob(prePath+testPrefix+'*')
    # print(filenames)
    
    for ceil in ceils:
        for app in appTypes:
            fig, ax = plt.subplots(1, figsize=(16,12))

            numCLIs = {}
            meanMOSs = {}
            targetQoEs = {}
            numSlices = {}
            runIdents = []
            for q in qs:
                print(q)
                for filename in filenames:
                    print(filename)
                    print('_R'+str(linkSpeed), '_Q'+str(q), '_C'+str(ceil))
                    if '_R'+str(linkSpeed) in filename and '_Q'+str(q) in filename and '_C'+str(ceil) in filename and '_P'+str(prio) in filename:
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
                        mosValDF = filterDFType(filterDFType(runDF, app), 'Val').dropna()
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
            ax.set_ylim(2.0,5.0)
            ticks = [1, 2, 3]
            labels = [1,2,5]
            plt.xticks(ticks, labels)
            plt.legend(fontsize=20)
            plt.xlabel('Number of Slices')
            plt.ylabel("QoE")
            outPath = preOutPath+'meanMosVsNumSlices_'+testPrefix+'_R'+str(linkSpeed)+'_C'+str(ceil)+'_P'+str(prio)+'_'+app+'.png'
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

def plotUtilVsSlicesSplit(testPrefix, linkSpeed, ceils, qs, simTime, prio):
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
            print(q)
            for filename in filenames:
                print(filename)
                if '_R'+str(linkSpeed) in filename and '_Q'+str(q) in filename and '_C'+str(ceil) in filename and '_P'+str(prio) in filename:
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
        ax.set_ylim(80,100)
        ticks = [1, 2, 3]
        labels = [1,2,5]
        plt.xticks(ticks, labels)
        plt.legend(fontsize=20)
        plt.xlabel('Number of Slices')
        plt.ylabel("System Utilization [%]")
        outPath = preOutPath+'meanUtilVsNumSlices_'+testPrefix+'_R'+str(linkSpeed)+'_C'+str(ceil)+'_P'+str(prio)+'.png'
        fig.savefig(outPath, dpi=100, bbox_inches='tight', format='png')
        plt.close('all')

assuredRatesOld = {'Q30' : {'VID' : 480,
                         'LVD' : 1250,
                         'FDO' : 440,
                         'SSH' : 5,
                         'VIP' : 30},
                'Q35' : {'VID' : 640,
                         'LVD' : 1250,
                         'FDO' : 580,
                         'SSH' : 10,
                         'VIP' : 30},
                'Q40' : {'VID' : 1000,
                         'LVD' : 2150,
                         'FDO' : 800,
                         'SSH' : 10,
                         'VIP' : 30}}

assuredRatesOld2 = {'Q35' : {'VID' : 1120,
                         'LVD' : 1800,
                         'FDO' : 2220,
                         'SSH' : 10,
                         'VIP' : 30}}

assuredRates = {'Q30' : {'VID' : 530,
                         'LVD' : 640,
                         'FDO' : 1660,
                         'SSH' : 10,
                         'VIP' : 30},
                'Q35' : {'VID' : 1120,
                         'LVD' : 1800,
                         'FDO' : 2220,
                         'SSH' : 10,
                         'VIP' : 30},
                'Q40' : {'VID' : 2220,
                         'LVD' : 1820,
                         'FDO' : 3000,
                         'SSH' : 20,
                         'VIP' : 30},
                'Q60' : {'VID' : 1732.5,
                         'LVD' : 1890,
                         'FDO' : 1300,
                         'SSH' : 10,
                         'VIP' : 30}
                         }

def plotSlicesForCeilQsSplit(testPrefix, appTypes, dataType, linkSpeed, ceil, qs):
    prePath = '../exports/extracted/'+dataType+'/'
    filenames = glob.glob(prePath+testPrefix+'*')
    # print(filenames)
    fig, ax = plt.subplots(1, figsize=(16,12))

    filterName = ''
    yAxName = ''
    outName = 'plotSlicesForCeilQsSplit_'+testPrefix+'_R'+str(linkSpeed)+'_C'+str(ceil)+'_Q'+str(qs)
    if dataType == 'throughputs':
        filterName = 'Throughput'
        yAxName = 'Mean Clients Thorughput [kbps]'
        outName += '_TP'
    elif dataType == 'mos2':
        filterName = 'Val'
        yAxName = 'Mean Clients QoE'
        outName += '_QoE'
    else:
        print('Invalid data type!!')
        return

    numCLIs = {}
    meanClassVals = {}
    meanValsCI = {}
    # meanValsCIhi = {}
    numSlices = {}
    runIdents = []
    for filename in filenames:
        if 'Uplink' in filename: # Ignore uplink if throughputs
            continue
        print(filename)
        print('_R'+str(linkSpeed), '_Q'+str(qs), '_C'+str(ceil))
        if '_R'+str(linkSpeed) in filename and '_Q'+str(qs) in filename and '_C'+str(ceil) in filename:
            runName = filename.split('/')[-1].split('.')[0]
            print('Run:', runName)
            numSli = 1
            if 'sli' in runName:
                numSli = int(runName.split('sli')[0].split('_')[1])
            numCliRun = int(filename.split('_VID')[0].split('_')[-1])
            print('\tNumber of clients:', numCliRun)
            for appType in appTypes:
                runIdent = 'C'+str(ceil)+'_Q'+str(qs)+'_'+appType
                if runIdent not in runIdents:
                    numCLIs[runIdent] = []
                    meanClassVals[runIdent] = []
                    meanValsCI[runIdent] = []
                    # meanValsCIhi[runIdent] = []
                    numSlices[runIdent] = []
                    runIdents.append(runIdent)
                numCLIs[runIdent].append(numCliRun)
                numSlices[runIdent].append(numSli)
                runDF = pd.read_csv(filename)
                valDF = filterDFType(filterDFType(runDF, filterName), appType).dropna()
                meanCliValues = []
                for col in valDF:
                    meanCliValues.append(statistics.mean(valDF[col].dropna().tolist()))

                li, hi = stats.t.interval(0.95, len(meanCliValues)-1, loc=np.mean(meanCliValues), scale=stats.sem(meanCliValues))
                print('\tMean run', dataType, appType, ':', statistics.mean(meanCliValues),'; LowCI:',li,'; HiCI:',hi)
                meanClassVals[runIdent].append(statistics.mean(meanCliValues))
                meanValsCI[runIdent].append(hi - statistics.mean(meanCliValues))
            # break
    print(runIdents)
    # print(numCLIs)
    # print(targetQoEs)
    # print(meanMOSs)
    print(numSlices)

    counter = 0

    if dataType == 'mos2':
        ax.hlines(qs/10,xmin=-1,xmax=17, color='black', linestyle='--', label='Target QoE')
    elif dataType == 'throughputs':
        ax.hlines(-5,xmin=-20,xmax=-15, color='black', linestyle='--', label='Assured Rate')
        ax.hlines(-5,xmin=-20,xmax=-15, color='black', linestyle='dotted', label='Ceil Rate')


    for runIdent in runIdents:
        color = colorMapping[runIdent.split('_')[-1]]

        arrNumSli = [counter + 6*x for x in [x for _,x in sorted(zip(numSlices[runIdent],[0,1,2]))]]
        arrMeanVals = [x for _,x in sorted(zip(numSlices[runIdent],meanClassVals[runIdent]))]
        arrYerrs = [x for _,x in sorted(zip(numSlices[runIdent],meanValsCI[runIdent]))]

        ax.errorbar(arrNumSli, arrMeanVals, yerr=arrYerrs, capsize=20.0, marker='o', linestyle='', color=color, label=chooseName('host'+runIdent.split('_')[-1]))

        if dataType == 'throughputs':
            exmin = [-0.4 + x for x in arrNumSli]
            exmax = [0.4 + x for x in arrNumSli]
            assured = assuredRates[runIdent.split('_')[1]][runIdent.split('_')[-1]]
            ax.hlines([assured for _ in arrNumSli],xmin=exmin,xmax=exmax, color=color, linestyle='--')
            ax.hlines([assured*ceil/100 for _ in arrNumSli],xmin=exmin,xmax=exmax, color=color, linestyle='dotted')


        counter += 1
    # # ax.plot(numCLIs[runIdent], targetQoEs[runIdent], 'D-', color='red', label='Target QoE')

    # ax.vlines([5,11])

    preOutPath = '../exports/plots/sliceConf/'
    if not os.path.exists(preOutPath):
        os.makedirs(preOutPath)

    if dataType == 'throughputs':
        ax.set_ylim(0,4500)
    elif dataType == 'mos2':
        ax.set_ylim(2.0,4.4)
    ax.vlines([5,11], ymin=0, ymax=5000, color='grey')
    ticks = [2+x*6 for x in [0,1,2]]
    labels = [1,2,5]
    ax.set_xlim(-0.5,16.5)
    plt.xticks(ticks, labels)
    plt.legend(fontsize=20)
    plt.xlabel('Number of Slices')
    plt.ylabel(yAxName)
    outPath = preOutPath+outName+'.png'
    fig.savefig(outPath, dpi=100, bbox_inches='tight', format='png')
    plt.close('all')


def plotSlicesBoxForCeilQsSplit(testPrefix, appTypes, dataType, linkSpeed, ceil, qs, tpMean):
    prePath = '../exports/extracted/'+dataType+'/'
    filenames = glob.glob(prePath+testPrefix+'*')
    print(filenames)
    fig, ax = plt.subplots(1, figsize=(16,12))

    filterName = ''
    yAxName = ''
    outName = 'plotSlicesForCeilQsSplit_'+testPrefix+'_R'+str(linkSpeed)+'_C'+str(ceil)+'_Q'+str(qs)
    if dataType == 'throughputs':
        filterName = 'Throughput'
        yAxName = 'Client Thorughput [kbps]'
        outName += '_TPbox'
    elif dataType == 'mos2':
        filterName = 'Val'
        yAxName = 'Mean Client QoE'
        outName += '_QoEbox'
    else:
        print('Invalid data type!!')
        return

    numCLIs = {}
    meanClassVals = {}
    meanValsCI = {}
    # meanValsCIhi = {}
    numSlices = {}
    runIdents = []
    for filename in filenames:
        if 'Uplink' in filename: # Ignore uplink if throughputs
            continue
        print(filename)
        print('_R'+str(linkSpeed), '_Q'+str(qs), '_C'+str(ceil))
        if '_R'+str(linkSpeed) in filename and '_Q'+str(qs) in filename and '_C'+str(ceil) in filename:
            runName = filename.split('/')[-1].split('.')[0]
            print('Run:', runName)
            numSli = 1
            if 'sli' in runName:
                numSli = int(runName.split('sli')[0].split('_')[1])
            numCliRun = int(filename.split('_VID')[0].split('_')[-1])
            print('\tNumber of clients:', numCliRun)
            for appType in appTypes:
                runIdent = 'C'+str(ceil)+'_Q'+str(qs)+'_'+appType
                if runIdent not in runIdents:
                    numCLIs[runIdent] = []
                    meanClassVals[runIdent] = []
                    meanValsCI[runIdent] = []
                    # meanValsCIhi[runIdent] = []
                    numSlices[runIdent] = []
                    runIdents.append(runIdent)
                numCLIs[runIdent].append(numCliRun)
                numSlices[runIdent].append(numSli)
                runDF = pd.read_csv(filename)
                valDF = filterDFType(filterDFType(runDF, filterName), appType).dropna()
                meanCliValues = []
                for col in valDF:
                    if dataType == 'throughputs' and tpMean == False:
                        meanCliValues.extend(valDF[col].dropna().tolist())
                    if dataType == 'throughputs' and tpMean == True:
                        meanCliValues.append(statistics.mean(valDF[col].dropna().tolist()))
                    elif dataType == 'mos2':
                        if len(valDF[col].dropna().tolist()) > 0:
                            meanCliValues.append(statistics.mean(valDF[col].dropna().tolist()))
                        else:
                            meanCliValues.append(-1)
                li, hi = stats.t.interval(0.95, len(meanCliValues)-1, loc=np.mean(meanCliValues), scale=stats.sem(meanCliValues))
                print('\tMean run', dataType, appType, ':', statistics.mean(meanCliValues),'; LowCI:',li,'; HiCI:',hi)
                meanClassVals[runIdent].append(meanCliValues)
                meanValsCI[runIdent].append(hi - statistics.mean(meanCliValues))
            # break
    print(runIdents)
    # print(numCLIs)
    # print(targetQoEs)
    # print(meanMOSs)
    print(numSlices)

    counter = 0

    bps = []
    lbls = []

    if dataType == 'mos2':
        one = ax.hlines(qs/10,xmin=-1,xmax=17, color='black', linestyle='--', label='Target QoE')
        bps.append(one)
        lbls.append('Target QoE')

    elif dataType == 'throughputs':
        one = ax.hlines(-5,xmin=-20,xmax=-15, color='black', linestyle='--', label='Assured Rate')
        two = ax.hlines(-5,xmin=-20,xmax=-15, color='black', linestyle='dotted', label='Ceil Rate')
        bps.append(one)
        lbls.append('Assured Rate')
        bps.append(two)
        lbls.append('Ceil Rate')

    for runIdent in runIdents:
        color = colorMapping[runIdent.split('_')[-1]]

        arrNumSli = [counter + 6*x for x in [x for _,x in sorted(zip(numSlices[runIdent],[0,1,2]))]]
        arrMeanVals = [x for _,x in sorted(zip(numSlices[runIdent],meanClassVals[runIdent]))]
        arrYerrs = [x for _,x in sorted(zip(numSlices[runIdent],meanValsCI[runIdent]))]

        bp1 = ax.boxplot(arrMeanVals, positions=arrNumSli, notch=False, patch_artist=False,
            boxprops=dict(color=color),
            capprops=dict(color=color),
            whiskerprops=dict(color=color),
            flierprops=dict(color=color, markeredgecolor=color))
        
        bps.append(bp1)
        lbls.append(chooseName('host'+runIdent.split('_')[-1]))
        

        # ax.errorbar(arrNumSli, arrMeanVals, yerr=arrYerrs, capsize=20.0, marker='o', linestyle='', color=color, label=chooseName('host'+runIdent.split('_')[-1]))

        if dataType == 'throughputs':
            exmin = [-0.4 + x for x in arrNumSli]
            exmax = [0.4 + x for x in arrNumSli]
            assured = assuredRates[runIdent.split('_')[1]][runIdent.split('_')[-1]]
            ax.hlines([assured for _ in arrNumSli],xmin=exmin,xmax=exmax, color=color, linestyle='--')
            if runIdent.split('_')[-1] != 'FDO': ax.hlines([assured*ceil/100 for _ in arrNumSli],xmin=exmin,xmax=exmax, color=color, linestyle='dotted')


        counter += 1
    # # ax.plot(numCLIs[runIdent], targetQoEs[runIdent], 'D-', color='red', label='Target QoE')

    # ax.vlines([5,11])

    preOutPath = '../exports/plots/sliceConf/'
    if not os.path.exists(preOutPath):
        os.makedirs(preOutPath)
    
    if tpMean == True:
        preOutPath += 'meanCLI'

    temp=[]
    if dataType == 'throughputs':
        ax.set_ylim(0,4500)
        temp = [bps[0], bps[1]]
        temp.extend([element["boxes"][0] for element in bps[2:]])
    elif dataType == 'mos2':
        ax.set_ylim(1.0,5.0)
        temp = [bps[0]]
        temp.extend([element["boxes"][0] for element in bps[1:]])
    ax.vlines([5,11], ymin=0, ymax=5000, color='grey')
    ticks = [2+x*6 for x in [0,1,2]]
    labels = [1,2,5]
    ax.set_xlim(-0.5,16.5)
    plt.xticks(ticks, labels)
    ax.legend(temp, lbls, fontsize='x-small')
    # plt.legend(fontsize=20)
    ax.grid(axis='y')
    plt.xlabel('Number of Slices')
    plt.ylabel(yAxName)
    outPath = preOutPath+outName+'.png'
    fig.savefig(outPath, dpi=100, bbox_inches='tight', format='png')
    plt.close('all')


def plotClassSlicesBoxForCeilQsSplit(testPrefix, appTypes, dataType, linkSpeed, ceil, qs, tpMean):
    prePath = '../exports/extracted/'+dataType+'/'
    filenames = glob.glob(prePath+testPrefix+'*')
    print(filenames)
    fig, ax = plt.subplots(1, figsize=(16,12))

    filterName = ''
    yAxName = ''
    outName = 'plotClassSlicesForCeilQsSplit_'+testPrefix+'_R'+str(linkSpeed)+'_C'+str(ceil)+'_Q'+str(qs)
    if dataType == 'throughputs':
        filterName = 'Throughput'
        yAxName = 'Client Thorughput [kbps]'
        outName += '_TPbox'
    elif dataType == 'mos2':
        filterName = 'Val'
        yAxName = 'Mean Client QoE'
        outName += '_QoEbox'
    else:
        print('Invalid data type!!')
        return

    numCLIs = {}
    meanClassVals = {}
    meanValsCI = {}
    # meanValsCIhi = {}
    numSlices = {}
    runIdents = []
    numCLIsRunIdent = {}
    for filename in filenames:
        if 'Uplink' in filename: # Ignore uplink if throughputs
            continue
        print(filename)
        print('_R'+str(linkSpeed), '_Q'+str(qs), '_C'+str(ceil))
        if '_R'+str(linkSpeed) in filename and '_Q'+str(qs) in filename and '_C'+str(ceil) in filename:
            runName = filename.split('/')[-1].split('.')[0]
            print('Run:', runName)
            numSli = 1
            if 'sli' in runName:
                numSli = int(runName.split('sli')[0].split('_')[1])
            numCliRun = int(filename.split('_VID')[0].split('_')[-1])
            print('\tNumber of clients:', numCliRun)
            for appType in appTypes:
                runIdent = 'C'+str(ceil)+'_Q'+str(qs)+'_'+appType
                temp = filename
                if appType == 'VID':
                    temp = temp.split('VID')[1]
                    numVID = int(temp.split('_')[0])
                    numCLIsRunIdent[runIdent] = numVID
                elif appType == 'LVD':
                    temp = temp.split('LVD')[1]
                    numLVD = int(temp.split('_')[0])
                    numCLIsRunIdent[runIdent] = numLVD
                elif appType == 'FDO':
                    temp = temp.split('FDO')[1]
                    numFDO = int(temp.split('_')[0])
                    numCLIsRunIdent[runIdent] = numFDO
                elif appType == 'SSH':
                    temp = temp.split('SSH')[1]
                    numSSH = int(temp.split('_')[0])
                    numCLIsRunIdent[runIdent] = numSSH
                elif appType == 'VIP':
                    temp = temp.split('VIP')[1]
                    numVIP = int(temp.split('_')[0])
                    numCLIsRunIdent[runIdent] = numVIP
                
                if runIdent not in runIdents:
                    numCLIs[runIdent] = []
                    meanClassVals[runIdent] = []
                    meanValsCI[runIdent] = []
                    # meanValsCIhi[runIdent] = []
                    numSlices[runIdent] = []
                    runIdents.append(runIdent)
                numCLIs[runIdent].append(numCliRun)
                numSlices[runIdent].append(numSli)
                runDF = pd.read_csv(filename)
                valDF = filterDFType(filterDFType(runDF, filterName), appType).dropna()
                meanCliValues = [0 for _ in range(maxSimTime)]
                for col in valDF:
                    if dataType == 'throughputs' and tpMean == False:
                        meanCliValues = [sum(x) for x in zip(valDF[col].dropna().tolist(), meanCliValues)]
                    if dataType == 'throughputs' and tpMean == True:
                        meanCliValues.append(statistics.mean(valDF[col].dropna().tolist()))
                    elif dataType == 'mos2':
                        if len(valDF[col].dropna().tolist()) > 0:
                            meanCliValues.append(statistics.mean(valDF[col].dropna().tolist()))
                        else:
                            meanCliValues.append(-1)
                li, hi = stats.t.interval(0.95, len(meanCliValues)-1, loc=np.mean(meanCliValues), scale=stats.sem(meanCliValues))
                print('\tMean run', dataType, appType, ':', statistics.mean(meanCliValues),'; LowCI:',li,'; HiCI:',hi)
                meanClassVals[runIdent].append(meanCliValues)
                meanValsCI[runIdent].append(hi - statistics.mean(meanCliValues))
            # break
    print(runIdents)
    # print(numCLIs)
    # print(targetQoEs)
    # print(meanMOSs)
    print(numSlices)

    counter = 0

    bps = []
    lbls = []

    if dataType == 'mos2':
        one = ax.hlines(qs/10,xmin=-1,xmax=17, color='black', linestyle='--', label='Target QoE')
        bps.append(one)
        lbls.append('Target QoE')

    elif dataType == 'throughputs':
        one = ax.hlines(-5,xmin=-20,xmax=-15, color='black', linestyle='--', label='Sum of Assured Rates')
        if ceil != 100: two = ax.hlines(-5,xmin=-20,xmax=-15, color='black', linestyle='dotted', label='Sum of Ceil Rates')
        bps.append(one)
        lbls.append('Sum of Assured Rates')
        if ceil != 100: bps.append(two)
        if ceil != 100: lbls.append('Sum of Ceil Rates')

    for runIdent in runIdents:
        color = colorMapping[runIdent.split('_')[-1]]

        arrNumSli = [counter + 6*x for x in [x for _,x in sorted(zip(numSlices[runIdent],[0,1,2]))]]
        arrMeanVals = [x for _,x in sorted(zip(numSlices[runIdent],meanClassVals[runIdent]))]
        arrYerrs = [x for _,x in sorted(zip(numSlices[runIdent],meanValsCI[runIdent]))]

        bp1 = ax.boxplot(arrMeanVals, positions=arrNumSli, notch=False, patch_artist=False,
            boxprops=dict(color=color),
            capprops=dict(color=color),
            whiskerprops=dict(color=color),
            flierprops=dict(color=color, markeredgecolor=color))
        
        bps.append(bp1)
        lbls.append(chooseName('host'+runIdent.split('_')[-1]))
        

        # ax.errorbar(arrNumSli, arrMeanVals, yerr=arrYerrs, capsize=20.0, marker='o', linestyle='', color=color, label=chooseName('host'+runIdent.split('_')[-1]))

        if dataType == 'throughputs':
            exmin = [-0.4 + x for x in arrNumSli]
            exmax = [0.4 + x for x in arrNumSli]
            assured = assuredRates[runIdent.split('_')[1]][runIdent.split('_')[-1]]*numCLIsRunIdent[runIdent]
            ax.hlines([assured for _ in arrNumSli],xmin=exmin,xmax=exmax, color=color, linestyle='--')
            if runIdent.split('_')[-1] != 'FDO': ax.hlines([assured*ceil/100 for _ in arrNumSli],xmin=exmin,xmax=exmax, color=color, linestyle='dotted')


        counter += 1
    # # ax.plot(numCLIs[runIdent], targetQoEs[runIdent], 'D-', color='red', label='Target QoE')

    # ax.vlines([5,11])

    preOutPath = '../exports/plots/sliceConf/'
    if not os.path.exists(preOutPath):
        os.makedirs(preOutPath)
    
    if tpMean == True:
        preOutPath += 'meanCLI'

    temp=[]
    if dataType == 'throughputs':
        ax.set_ylim(0,60000)
        temp = [bps[0], bps[1]]
        temp.extend([element["boxes"][0] for element in bps[2:]])
    elif dataType == 'mos2':
        ax.set_ylim(1.0,5.0)
        temp = [bps[0]]
        temp.extend([element["boxes"][0] for element in bps[1:]])
    ax.vlines([5,11], ymin=0, ymax=5000, color='grey')
    ticks = [2+x*6 for x in [0,1,2]]
    labels = [1,2,5]
    ax.set_xlim(-0.5,16.5)
    plt.xticks(ticks, labels)
    ax.legend(temp, lbls, fontsize='x-small')
    # plt.legend(fontsize=20)
    ax.grid(axis='y')
    plt.xlabel('Number of Slices')
    plt.ylabel(yAxName)
    outPath = preOutPath+outName+'.png'
    fig.savefig(outPath, dpi=100, bbox_inches='tight', format='png')
    plt.close('all')


def plotQueueLengthCDF(testName, dataType, metric):
    prePath = '../'+dataType+'/scalars/'
    # print(prePath)
    filenames = glob.glob(prePath+testName+'*')
    # print(filenames)
    for filename in filenames:
        print(filename)
        temp = filename.split('VID')[1]
        numVID = int(temp.split('_')[0])
        temp = temp.split('LVD')[1]
        numLVD = int(temp.split('_')[0])
        temp = temp.split('FDO')[1]
        numFDO = int(temp.split('_')[0])
        temp = temp.split('SSH')[1]
        numSSH = int(temp.split('_')[0])
        temp = temp.split('VIP')[1]
        numVIP = int(temp.split('_')[0])
        # print('Video:',numVID)
        # print('Live:',numLVD)
        # print('Download:',numFDO)
        # print('VoIP:',numVIP)
        # print('SSH:',numSSH)
        # Results order: VID, LVD, FDO, VIP, SSH
        runDF = pd.read_csv(filename, comment='*')
        qI = 0
        vidQ = []
        lvdQ = []
        fdoQ = []
        vipQ = []
        sshQ = []
        while True:
            queueDF = runDF[runDF['Module'].str.contains('queue\['+str(qI)+'\]')]
            if queueDF.empty: break
            value = queueDF[queueDF['Name'].str.contains('queue') & queueDF['Name'].str.contains(metric)].iloc[-1,-1]
            # print(value)
            # break
            if qI >= 0 and qI < numVID:
                vidQ.append(value)
            elif qI >= numVID and qI < numVID + numLVD:
                lvdQ.append(value)
            elif qI >= numVID + numLVD and qI < numVID + numLVD + numFDO:
                fdoQ.append(value)
            elif qI >= numVID + numLVD + numFDO and qI < numVID + numLVD + numFDO + numVIP:
                vipQ.append(value)
            elif qI >= numVID + numLVD + numFDO + numVIP and qI < numVID + numLVD + numFDO + numVIP + numSSH:
                sshQ.append(value)
            qI+=1
        print('Video',len(vidQ), vidQ)
        print('Live',len(lvdQ), lvdQ)
        print('Download',len(fdoQ), fdoQ)
        print('VoIP',len(vipQ), vipQ)
        print('SSH',len(sshQ), sshQ)
    
        fig, ax1 = plt.subplots(1, figsize=(16,12))

        partialCDFPlotData(fig, ax1, vidQ, chooseName('hostVID'), '-o', chooseColor('hostVID'))
        partialCDFPlotData(fig, ax1, lvdQ, chooseName('hostLVD'), '-o', chooseColor('hostLVD'))
        partialCDFPlotData(fig, ax1, fdoQ, chooseName('hostFDO'), '-o', chooseColor('hostFDO'))
        partialCDFPlotData(fig, ax1, vipQ, chooseName('hostVIP'), '-o', chooseColor('hostVIP'))
        partialCDFPlotData(fig, ax1, sshQ, chooseName('hostSSH'), '-o', chooseColor('hostSSH'))



        partialCDFEnd(fig,ax1,'', 'Queue Length ' + metric, '../exports/plots/queueLen/'+ filename.split('/')[-1].split('_sca')[0] +'_cdfQueueLen' + metric + '.pdf')
        partialCDFEndPNG(fig,ax1,'', 'Queue Length ' + metric, '../exports/plots/queueLen/'+ filename.split('/')[-1].split('_sca')[0] +'_cdfQueueLen' + metric + '.png')

    

# plotQueueLengthCDF('qoeAdmissionAutoNo1','routerSCA')
# plotQueueLengthCDF('qoeAdmission4-3xDelNo2_2sli','routerSCA', 'timeavg')
# plotQueueLengthCDF('qoeAdmission4-3xDelNo2_2sli','routerSCA', 'max')

# plotQueueLengthCDF('qoeAdmissionAutoNo1Base','routerSCA', 'timeavg')
# plotQueueLengthCDF('qoeAdmissionAutoNo1Base','routerSCA', 'max')

# plotQueueLengthCDF('qoeAdmissionAutoNo2_2sli','routerSCA', 'timeavg')
# plotQueueLengthCDF('qoeAdmissionAutoNo2_2sli','routerSCA', 'max')

# plotQueueLengthCDF('qoeAdmissionAutoNo3_5sli','routerSCA', 'timeavg')
# plotQueueLengthCDF('qoeAdmissionAutoNo3_5sli','routerSCA', 'max')

# plotQueueLengthCDF('qoeAdmission3-4delBandNo','routerSCA', 'timeavg')
# plotQueueLengthCDF('qoeAdmission3-4delBandNo','routerSCA', 'max')


def plotClassTPSbarDirection(testNamePrefixes, dataType, direction, hostConfigToPlot, groupNames, simTime):
    prePath = '../exports/extracted/'+dataType+'/'
    # print(prePath)
    filenames = []
    outName = ''
    for testName in testNamePrefixes:
        outName += testName
        filenames.extend([x for x in glob.glob(prePath+testName+'*') if direction[0] in x])
    
    
    # print(filenames)
    
    barSpacing = len(filenames)
    cmap = matplotlib.cm.get_cmap('Set1')
    ivals = np.linspace(0, 1, barSpacing)
    colors = [cmap(x) for x in ivals]
    print(colors)
    
    groupNum = 0
    for group,name in zip(hostConfigToPlot,groupNames):
        fig, ax1 = partialCDFBegin(1)
        testNum = 0
        for filename in filenames:
            print(filename)
            # temp = filename.split('VID')[1]
            # numVID = int(temp.split('_')[0])
            # temp = temp.split('LVD')[1]
            # numLVD = int(temp.split('_')[0])
            # temp = temp.split('FDO')[1]
            # numFDO = int(temp.split('_')[0])
            # temp = temp.split('SSH')[1]
            # numSSH = int(temp.split('_')[0])
            # temp = temp.split('VIP')[1]
            # numVIP = int(temp.split('_')[0])
            runDF = pd.read_csv(filename, comment='*')
            groupKbitsSum = 0
            for hostType in group:
                groupKbitsSum += runDF.filter(like=hostType).to_numpy().sum()
            print(groupKbitsSum/(simTime*1000))
            ax1.bar(filename.split('_R')[0].split('Admission')[-1], groupKbitsSum/(simTime*1000), width=1, color=colors[testNum])
            groupNum += 1
            testNum += 1

        preOutPath = '../exports/plots/groupTPs/'
        if not os.path.exists(preOutPath):
            os.makedirs(preOutPath)
        # ax1.legend()
        # plt.legend(fontsize=20)
        ax1.grid()
        plt.xticks(rotation=90)
        plt.xlabel('Test Name')
        plt.ylabel('Average ' + direction[0] + ' Throughput [mbps]')
        outPath = preOutPath+outName+name+'.png'
        fig.savefig(outPath, dpi=100, bbox_inches='tight', format='png')
        plt.close('all')

    # df = importDFextended(testName, numCLI, nodeTypes, nodeSplit, 'throughputs', '_' + direction[0])
    # fig, ax1 = partialCDFBegin(1)
    # maxTPS = 0
    # for nodeType,numNodes in zip(nodeTypes,nodeSplit):
    #     tempTPSall = []
    #     for nodeNum in range(numNodes):
    #         colName = direction[0] + " Throughput " + makeNodeIdentifier(nodeType, nodeNum)
    #         tempTPSall.append(statistics.mean([x/1000 for x in df[colName].tolist()[:int(cutoff)+1]]))
    #     if maxTPS < max(tempTPSall):
    #         maxTPS = max(tempTPSall)
    #     partialCDFPlotData(fig, ax1, tempTPSall, chooseName(nodeType), '-o', chooseColor(nodeType))

    # ax1.set_xlim(0,1.01*maxTPS)
    # partialCDFEnd(fig,ax1,'', 'Mean Client Throughput [mbps]', '../exports/plots/'+makeFullScenarioName(testName, numCLI, nodeTypes, nodeSplit)+'/'+str(globalCounter)+'_cdfMean'+direction[0]+'ThroughputsCutoff'+ str(cutoff) + str(nodeTypes) + '.pdf')
    # partialCDFEndPNG(fig,ax1,'', 'Mean Client Throughput [mbps]', '../exports/plots/'+makeFullScenarioName(testName, numCLI, nodeTypes, nodeSplit)+'/'+str(globalCounter)+'_cdfMean'+direction[0]+'ThroughputsCutoff'+ str(cutoff) + str(nodeTypes) + '.png')

# plotClassTPSbarDirection(['qoeAdmissionAutoNo', 'qoeAdmission3-4delBandNo'], 'throughputs', downlink, [['VIP'],['SSH'], ['VID'], ['LVD'], ['FDO']], ['VoIP', 'SSH', 'VoD', 'Live', 'Download'], 400)
# plotClassTPSbarDirection(['qoeAdmissionAutoNo', 'qoeAdmission3-4delBandNo'], 'throughputs', downlink, [['VIP','SSH'], ['VID', 'LVD', 'FDO']], ['Delay', 'Bandwidth'], 400)

def plotCliTPdirection(testNamePrefix, direction, simTime):
    # print(prePath)
    prePath = '../exports/extracted/throughputs/'
    filenames = [x for x in glob.glob(prePath+testNamePrefix+'*') if direction[0] in x]

    times = range(1,simTime+1,1)
    index = 0
    for filename in filenames:
        preOutPath = '../exports/plots/TPs/'+testNamePrefix+str(index)+'/'
        if not os.path.exists(preOutPath):
            os.makedirs(preOutPath)
        print(filename)
        # temp = filename.split('VID')[1]
        # numVID = int(temp.split('_')[0])
        # temp = temp.split('LVD')[1]
        # numLVD = int(temp.split('_')[0])
        # temp = temp.split('FDO')[1]
        # numFDO = int(temp.split('_')[0])
        # temp = temp.split('SSH')[1]
        # numSSH = int(temp.split('_')[0])
        # temp = temp.split('VIP')[1]
        # numVIP = int(temp.split('_')[0])
        runDF = pd.read_csv(filename, comment='*')
        groupKbitsSum = 0
        for hostType in ['VIP','SSH', 'VID', 'LVD', 'FDO']:
            # tpList = runDF.filter(like=hostType).sum(axis=1).tolist()
            dfType = runDF.filter(like=hostType)
            for column in dfType.columns:
                tpList = dfType[column].tolist()
                fig, ax1 = plt.subplots(1, figsize=(16,12))
                ax1.plot(times, tpList, label=column, marker='o', ls='-')
                plt.legend(fontsize=20)
                ax1.grid()
                ax1.set_xlim(0,100)
                if hostType == 'VIP':
                    ax1.set_ylim(0,150)
                else:    
                    ax1.set_ylim(0,3100)
                plt.xlabel('Time [s]')
                plt.ylabel(direction[0] + ' Throughput [kbps]')
                outName = 'TP ' + column + direction[0]
                outPath = preOutPath+outName+'.png'
                fig.savefig(outPath, dpi=100, bbox_inches='tight', format='png')
                plt.close('all')
        index += 1


# plotCliTPdirection('qoeAdmissionAutoNo1Base', downlink, 400)
# testNames = ['qoeAdmissionAutoNo1Base', 'qoeAdmissionAutoNo2_2sli', 'qoeAdmissionAutoNo3_5sli', 'qoeAdmission3-4delBandNo1Base', 'qoeAdmission3-4delBandNo2_2sli', 'qoeAdmission3-4delBandNo3_5sli']
# testNames = ['qoeAdmissionAutoNo2_2sli', 'qoeAdmission3-4delBandNo2_2sli', 'qoeAdmissionAuto40msNo2_2sli', 'qoeAdmission3-4delBand40msNo2_2sli']
# for testName in testNames:
#     plotCliTPdirection(testName, downlink, 400)


def plotClassTPdirection(testNamePrefix, direction, simTime):
    # print(prePath)
    prePath = '../exports/extracted/throughputs/'
    filenames = [x for x in glob.glob(prePath+testNamePrefix+'*') if direction[0] in x]

    times = range(1,simTime+1,1)
    index = 0
    for filename in filenames:
        preOutPath = '../exports/plots/TPs/'+testNamePrefix+str(index)+'/'
        if not os.path.exists(preOutPath):
            os.makedirs(preOutPath)
        print(filename)
        # temp = filename.split('VID')[1]
        # numVID = int(temp.split('_')[0])
        # temp = temp.split('LVD')[1]
        # numLVD = int(temp.split('_')[0])
        # temp = temp.split('FDO')[1]
        # numFDO = int(temp.split('_')[0])
        # temp = temp.split('SSH')[1]
        # numSSH = int(temp.split('_')[0])
        # temp = temp.split('VIP')[1]
        # numVIP = int(temp.split('_')[0])
        runDF = pd.read_csv(filename, comment='*')
        groupKbitsSum = 0
        fig, ax1 = plt.subplots(1, figsize=(16,12))
        for hostType in ['VIP','SSH', 'VID', 'LVD', 'FDO']:
            tpList = runDF.filter(like=hostType).sum(axis=1).tolist()
            ax1.plot(times, [x/1000 for x in tpList], label=hostType + 'class', marker='o', ls='-')
            
        plt.legend(fontsize=20)
        ax1.grid()
        plt.xlabel('Time [s]')
        plt.ylabel(direction[0] + ' Throughput [mbps]')
        outName = 'TPclass ' + direction[0]
        outPath = preOutPath+outName+'.png'
        fig.savefig(outPath, dpi=100, bbox_inches='tight', format='png')
        plt.close('all')
        index += 1

# plotClassTPdirection('qoeAdmissionAutoNo1Base', downlink, 400)
# testNames = ['qoeAdmissionAutoNo1Base', 'qoeAdmissionAutoNo2_2sli', 'qoeAdmissionAutoNo3_5sli', 'qoeAdmission3-4delBandNo1Base', 'qoeAdmission3-4delBandNo2_2sli', 'qoeAdmission3-4delBandNo3_5sli']
# for testName in testNames:
#     plotClassTPdirection(testName, downlink, 400)


# linkSpeeds = [100, 200]
# ceil = [100, 110, 125, 140]
# qs = [30, 35, 40]
# for ls in linkSpeeds:
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
    # plotUtilVsSlices('liteChtb', ls, ceil, qs, 400)
    # plotAvgTPVsNumCli('liteChtb', ls, ceil, 400)

# plotMosVsSlicesSplit('qoeAdm', 100, [140], [30,35,40], False)
# plotMosVsSlicesSplit('qoeAdm', 100, [140], [30,35,40], True)

# plotMosVsSlicesSplit('qosAdm', 100, [140], [35], False)
# plotMosVsSlicesSplit('qosAdm', 100, [140], [35], True)

# plotUtilVsSlicesSplit('qoeAdm', 100, [140], [30,35,40], 400, False)
# plotUtilVsSlicesSplit('qoeAdm', 100, [140], [30,35,40], 400, True)

# plotUtilVsSlicesSplit('qosAdm', 100, [140], [35], 400, False)
# plotUtilVsSlicesSplit('qosAdm', 100, [140], [35], 400, True)

# plotMosVsSlicesSplitAppType('qoeAdm', 100, [140], [30,35,40], False, ['VID', 'LVD', 'FDO', 'VIP', 'SSH'])

# plotSlicesForCeilQsSplit('liteChtb', ['VID', 'LVD', 'FDO', 'VIP', 'SSH'], 'mos2', 100, 100, 30)
# plotSlicesForCeilQsSplit('liteChtb', ['VID', 'LVD', 'FDO', 'VIP', 'SSH'], 'throughputs', 100, 100, 30)
# plotSlicesForCeilQsSplit('liteChtb', ['VID', 'LVD', 'FDO', 'VIP', 'SSH'], 'throughputs', 100, 140, 40)
# plotSlicesForCeilQsSplit('liteChtb', ['VID', 'LVD', 'FDO', 'VIP', 'SSH'], 'mos2', 100, 140, 40)

# for q in [30, 35, 40]:
#     for ceil in [100, 110, 125, 140]:
#         plotSlicesForCeilQsSplit('liteChtb', ['VID', 'LVD', 'FDO', 'VIP', 'SSH'], 'mos2', 100, ceil, q)
#         plotSlicesForCeilQsSplit('liteChtb', ['VID', 'LVD', 'FDO', 'VIP', 'SSH'], 'throughputs', 100, ceil, q)

# for q in [35]:
#     for ceil in [200]:
#         # plotSlicesForCeilQsSplit('newHmsQoeAdm', ['VID', 'LVD', 'FDO', 'VIP', 'SSH'], 'mos2', 100, ceil, q)
#         # plotSlicesForCeilQsSplit('newHmsQoeAdm', ['VID', 'LVD', 'FDO', 'VIP', 'SSH'], 'throughputs', 100, ceil, q)
#         plotSlicesBoxForCeilQsSplit('qoeAdmissionAuto', ['VID', 'LVD', 'FDO', 'VIP', 'SSH'], 'throughputs', 100, ceil, q, False)
#         plotSlicesBoxForCeilQsSplit('qoeAdmissionAuto', ['VID', 'LVD', 'FDO', 'VIP', 'SSH'], 'mos2', 100, ceil, q, False)
#         plotSlicesBoxForCeilQsSplit('qoeAdmissionAuto', ['VID', 'LVD', 'FDO', 'VIP', 'SSH'], 'throughputs', 100, ceil, q, True)
#         plotSlicesBoxForCeilQsSplit('qoeAdmissionAuto', ['VID', 'LVD', 'FDO', 'VIP', 'SSH'], 'mos2', 100, ceil, q, True)
#         plotUtilVsSlicesSplit('qoeAdmissionAuto', 100, [ceil], [q], 400, False)


# for q in [35]:
#     for ceil in [200]:
#         plotSlicesBoxForCeilQsSplit('qoeAdmission4-3xDel', ['VID', 'LVD', 'FDO', 'VIP', 'SSH'], 'throughputs', 100, ceil, q, False)
#         plotSlicesBoxForCeilQsSplit('qoeAdmission4-3xDel', ['VID', 'LVD', 'FDO', 'VIP', 'SSH'], 'mos2', 100, ceil, q, False)
#         plotSlicesBoxForCeilQsSplit('qoeAdmission4-3xDel', ['VID', 'LVD', 'FDO', 'VIP', 'SSH'], 'throughputs', 100, ceil, q, True)
#         plotSlicesBoxForCeilQsSplit('qoeAdmission4-3xDel', ['VID', 'LVD', 'FDO', 'VIP', 'SSH'], 'mos2', 100, ceil, q, True)
# #         # plotUtilVsSlicesSplit(testPrefix, linkSpeed, ceils, qs, simTime, prio)
#         plotUtilVsSlicesSplit('qoeAdmission4-3xDel', 100, [ceil], [q], 400, False)
# #         plotUtilVsSlicesSplit('newHmsQoeAdm4-3xDelLC', 100, [ceil], [q], 400, False)
# #         plotSlicesBoxForCeilQsSplit('newHmsQoeAdm4-3xDelLC', ['VID', 'LVD', 'FDO', 'VIP', 'SSH'], 'throughputs', 100, ceil, q)
# #         plotSlicesBoxForCeilQsSplit('newHmsQoeAdm4-3xDelLC', ['VID', 'LVD', 'FDO', 'VIP', 'SSH'], 'mos2', 100, ceil, q)
        # plotSlicesBoxForCeilQsSplit('qoeAdmission3-4delBand', ['VID', 'LVD', 'FDO', 'VIP', 'SSH'], 'throughputs', 100, ceil, q, False)
        # plotSlicesBoxForCeilQsSplit('qoeAdmission3-4delBand', ['VID', 'LVD', 'FDO', 'VIP', 'SSH'], 'mos2', 100, ceil, q, False)
        # plotSlicesBoxForCeilQsSplit('qoeAdmission3-4delBand', ['VID', 'LVD', 'FDO', 'VIP', 'SSH'], 'throughputs', 100, ceil, q, True)
        # plotSlicesBoxForCeilQsSplit('qoeAdmission3-4delBand', ['VID', 'LVD', 'FDO', 'VIP', 'SSH'], 'mos2', 100, ceil, q, True)
        # plotUtilVsSlicesSplit('qoeAdmission3-4delBand', 100, [ceil], [q], 400, False)

for q in [30,35,40]:
    for ceil in [100,120,140]:
#         plotSlicesBoxForCeilQsSplit('expQoeAdmission40ms', ['VID', 'LVD', 'FDO', 'VIP', 'SSH'], 'throughputs', 100, ceil, q, False)
#         plotSlicesBoxForCeilQsSplit('expQoeAdmission40ms', ['VID', 'LVD', 'FDO', 'VIP', 'SSH'], 'mos2', 100, ceil, q, False)
        plotClassSlicesBoxForCeilQsSplit('expQoeAdmission40ms', ['VID', 'LVD', 'FDO', 'VIP', 'SSH'], 'throughputs', 100, ceil, q, False)

for q in [60]:
    for ceil in [100,120,140]:
        # plotSlicesBoxForCeilQsSplit('expQosAdmissionNewDL40ms', ['VID', 'LVD', 'FDO', 'VIP', 'SSH'], 'throughputs', 100, ceil, q, False)
        # plotSlicesBoxForCeilQsSplit('expQosAdmissionNewDL40ms', ['VID', 'LVD', 'FDO', 'VIP', 'SSH'], 'mos2', 100, ceil, q, False)
        plotClassSlicesBoxForCeilQsSplit('expQosAdmissionNewDL40ms', ['VID', 'LVD', 'FDO', 'VIP', 'SSH'], 'throughputs', 100, ceil, q, False)
# print([100+x*20 for x in range(226)])