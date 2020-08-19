import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import csv
import math
import statistics
from scipy import stats
import os

font = {'weight' : 'normal',
        'size'   : 40}

matplotlib.rc('font', **font)
matplotlib.rc('lines', linewidth=2.0)
matplotlib.rc('lines', markersize=8)

downlink = ['Downlink', 'rxPkOk:vector(packetBytes)']
uplink = ['Uplink', 'txPk:vector(packetBytes)']
maxSimTime = 400

globalCounter = 0

niceTestName = {
    'baselineTest' : 'Baseline',
    'baselineTestNS_2sli_LVD-DES' : '2 Slices, Live Video in Delay Slice',
    'baselineTestNS_2sli_LVD-BWS' : '2 Slices, Live Video in Bandwidth Slice',
    'baselineTestNS_2sliSingle_LVD-DES' : '2 Slices + Single Link, Live Video in Delay Slice',
    'baselineTestNS_2sliSingle_LVD-BWS' : '2 Slices + Single Link, Live Video in Bandwidth Slice',
    'baselineTestNS_2sliSingle2sli_LVD-DES' : '2 Slices + Single Link + 2 Slices, Live Video in Delay Slice',
    'baselineTestNS_2sliSingle2sli_LVD-BWS' : '2 Slices + Single Link + 2 Slices, Live Video in Bandwidth Slice',
    'baselineTestNS_2sliDouble_LVD-DES' : 'Directional 2 Slices + Single Link, Live Video in Delay Slice',
    'baselineTestNS_2sliDouble_LVD-BWS' : 'Directional 2 Slices + Single Link, Live Video in Bandwidth Slice',
    'baselineTestNS_5sli' : '5 Slices',
    'baselineTestNS_5sliSingle' : '5 Slices + Single Link',
    'baselineTestNS_5sliSingle5sli' : '5 Slices + Single Link + 5 Slices',
    'baselineTestNS_5sliDouble' : 'Directional 5 Slices + Single Link'
}

testNameTestNum = {
    'baselineTest' : 1,
    'baselineTestNS_2sli_LVD-DES' : 2,
    'baselineTestNS_2sli_LVD-BWS' : 3,
    'baselineTestNS_2sliSingle_LVD-DES' : 4,
    'baselineTestNS_2sliSingle_LVD-BWS' : 5,
    'baselineTestNS_2sliSingle2sli_LVD-DES' : 6,
    'baselineTestNS_2sliSingle2sli_LVD-BWS' : 7,
    'baselineTestNS_2sliDouble_LVD-DES' : 8,
    'baselineTestNS_2sliDouble_LVD-BWS' : 9,
    'baselineTestNS_5sli' : 10,
    'baselineTestNS_5sliSingle' : 11,
    'baselineTestNS_5sliSingle5sli' : 12,
    'baselineTestNS_5sliDouble' : 13
}


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

def chooseColor(dataName):
    if dataName == 'hostVID':
        return 'y'
    elif dataName == 'hostFDO':
        return 'g'
    elif dataName == 'hostSSH':
        return 'r'
    elif dataName == 'hostVIP':
        return 'b'
    if dataName == 'hostLVD':
        return 'm'
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

# Mean of means per client
def plotMeanClientMeanQoeAppClass(testNames, numCLI, nodeTypes, nodeSplit, dataIdent, folderName, nodeTypesToPlot):
    fig, ax = plt.subplots(1, figsize=(20,15))
    for testName in testNames:
        df = importDF(testName, numCLI, nodeTypes, nodeSplit, folderName)
        tempTest = []
        for nodeType,numNodes in zip(nodeTypes,nodeSplit):
            print(nodeType)
            if nodeType in nodeTypesToPlot:
                tempValue = []
                for nodeNum in range(numNodes):
                    colName = makeNodeIdentifier(nodeType, nodeNum) + " " + dataIdent + " Val"
                    data = df[colName].dropna().tolist()
                    if len(data) > 0:
                        tempValue.append(statistics.mean(data))
                        tempTest.append(statistics.mean(data))
                if len(tempValue) > 0:
                    if testNames.index(testName) == 0:
                        ax.plot(str(testNameTestNum[testName]), statistics.mean(tempValue), 'o', color=chooseColor(nodeType), label=chooseName(nodeType))
                        ax.plot([str(testNameTestNum[tN]) for tN in testNames], [statistics.mean(tempValue) for x in range(len(testNames))], '--', color=chooseColor(nodeType))
                    else:
                        ax.plot(str(testNameTestNum[testName]), statistics.mean(tempValue), 'o', color=chooseColor(nodeType))
        if testNames.index(testName) == 0:
            ax.plot(str(testNameTestNum[testName]), statistics.mean(tempTest), 'D', color='k', label='All Clients')
            ax.plot([str(testNameTestNum[tN]) for tN in testNames], [statistics.mean(tempTest) for x in range(len(testNames))], '--', color='k')
        else:
            ax.plot(str(testNameTestNum[testName]), statistics.mean(tempTest), 'D', color='k')

    ax.set_ylim(0.95,5.05)
    plt.xlabel('Experiment Number')
    plt.ylabel("Mean of Client Mean MOS Value")
    plt.legend(bbox_to_anchor=(0.99, 1.03))
    plt.grid(b=None, which='major', axis='both')
    fig.savefig('../exports/plots/mosMetrics/all'+str(len(testNames))+'tests_meanClientMeanQoeAppClass.png', dpi=100, bbox_inches='tight', format='png')
    fig.savefig('../exports/plots/mosMetrics/all'+str(len(testNames))+'tests_meanClientMeanQoeAppClass.pdf', dpi=100, bbox_inches='tight', format='pdf')
    plt.close('all')

def plotMeanQoeAppClass(testNames, numCLI, nodeTypes, nodeSplit, dataIdent, folderName, nodeTypesToPlot):
    fig, ax = plt.subplots(1, figsize=(20,15))
    for testName in testNames:
        df = importDF(testName, numCLI, nodeTypes, nodeSplit, folderName)
        tempTest = []
        for nodeType,numNodes in zip(nodeTypes,nodeSplit):
            print(nodeType)
            if nodeType in nodeTypesToPlot:
                tempValue = []
                for nodeNum in range(numNodes):
                    colName = makeNodeIdentifier(nodeType, nodeNum) + " " + dataIdent + " Val"
                    data = df[colName].dropna().tolist()
                    if len(data) > 0:
                        tempValue.extend(data)
                        tempTest.extend(data)
                if len(tempValue) > 0:
                    if testNames.index(testName) == 0:
                        ax.plot(str(testNameTestNum[testName]), statistics.mean(tempValue), 'o', color=chooseColor(nodeType), label=chooseName(nodeType))
                        ax.plot([str(testNameTestNum[tN]) for tN in testNames], [statistics.mean(tempValue) for x in range(len(testNames))], '--', color=chooseColor(nodeType))
                    else:
                        ax.plot(str(testNameTestNum[testName]), statistics.mean(tempValue), 'o', color=chooseColor(nodeType))
        if testNames.index(testName) == 0:
            ax.plot(str(testNameTestNum[testName]), statistics.mean(tempTest), 'D', color='k', label='All Clients')
            ax.plot([str(testNameTestNum[tN]) for tN in testNames], [statistics.mean(tempTest) for x in range(len(testNames))], '--', color='k')
        else:
            ax.plot(str(testNameTestNum[testName]), statistics.mean(tempTest), 'D', color='k')

    ax.set_ylim(0.95,5.05)
    plt.xlabel('Experiment Number')
    plt.ylabel("Mean MOS Value")
    plt.legend(bbox_to_anchor=(0.99, 1.03))
    plt.grid(b=None, which='major', axis='both')
    fig.savefig('../exports/plots/mosMetrics/all'+str(len(testNames))+'tests_meanQoeAppClass.png', dpi=100, bbox_inches='tight', format='png')
    fig.savefig('../exports/plots/mosMetrics/all'+str(len(testNames))+'tests_meanQoeAppClass.pdf', dpi=100, bbox_inches='tight', format='pdf')
    plt.close('all')

def plotMedianQoeAppClass(testNames, numCLI, nodeTypes, nodeSplit, dataIdent, folderName, nodeTypesToPlot):
    fig, ax = plt.subplots(1, figsize=(20,15))
    for testName in testNames:
        df = importDF(testName, numCLI, nodeTypes, nodeSplit, folderName)
        tempTest = []
        for nodeType,numNodes in zip(nodeTypes,nodeSplit):
            print(nodeType)
            if nodeType in nodeTypesToPlot:
                tempValue = []
                for nodeNum in range(numNodes):
                    colName = makeNodeIdentifier(nodeType, nodeNum) + " " + dataIdent + " Val"
                    data = df[colName].dropna().tolist()
                    if len(data) > 0:
                        tempValue.extend(data)
                        tempTest.extend(data)
                if len(tempValue) > 0:
                    if testNames.index(testName) == 0:
                        ax.plot(str(testNameTestNum[testName]), statistics.median(tempValue), 'o', color=chooseColor(nodeType), label=chooseName(nodeType))
                        ax.plot([str(testNameTestNum[tN]) for tN in testNames], [statistics.median(tempValue) for x in range(len(testNames))], '--', color=chooseColor(nodeType))
                    else:
                        ax.plot(str(testNameTestNum[testName]), statistics.median(tempValue), 'o', color=chooseColor(nodeType))
                print(statistics.median(tempValue), end=', mean = ')
                print(statistics.mean(tempValue))
        if testNames.index(testName) == 0:
            ax.plot(str(testNameTestNum[testName]), statistics.median(tempTest), 'D', color='k', label='All Clients')
            ax.plot([str(testNameTestNum[tN]) for tN in testNames], [statistics.median(tempTest) for x in range(len(testNames))], '--', color='k')
        else:
            ax.plot(str(testNameTestNum[testName]), statistics.median(tempTest), 'D', color='k')

    ax.set_ylim(0.95,5.05)
    plt.xlabel('Experiment Number')
    plt.ylabel("Median MOS Value")
    plt.legend(bbox_to_anchor=(0.99, 1.03))
    plt.grid(b=None, which='major', axis='both')
    fig.savefig('../exports/plots/mosMetrics/all'+str(len(testNames))+'tests_medianQoeAppClass.png', dpi=100, bbox_inches='tight', format='png')
    fig.savefig('../exports/plots/mosMetrics/all'+str(len(testNames))+'tests_medianQoeAppClass.pdf', dpi=100, bbox_inches='tight', format='pdf')
    plt.close('all')

def calcQoeFairness(qoeVals):
    qoeStdDev = statistics.stdev(qoeVals)
    lowBound = 1
    highBound = 5
    fairness = 1 - ((2*qoeStdDev)/(highBound-lowBound))
    return fairness

def plotFairnessQoeAppClass(testNames, numCLI, nodeTypes, nodeSplit, dataIdent, folderName, nodeTypesToPlot):
    fig, ax = plt.subplots(1, figsize=(20,15))
    for testName in testNames:
        df = importDF(testName, numCLI, nodeTypes, nodeSplit, folderName)
        tempTest = []
        for nodeType,numNodes in zip(nodeTypes,nodeSplit):
            print(nodeType)
            if nodeType in nodeTypesToPlot:
                tempValue = []
                for nodeNum in range(numNodes):
                    colName = makeNodeIdentifier(nodeType, nodeNum) + " " + dataIdent + " Val"
                    data = df[colName].dropna().tolist()
                    if len(data) > 0:
                        tempValue.extend(data)
                        tempTest.append(statistics.mean(data))
                if len(tempValue) > 0:
                    if testNames.index(testName) == 0:
                        ax.plot(str(testNameTestNum[testName]), calcQoeFairness(tempValue), 'o', color=chooseColor(nodeType), label=chooseName(nodeType))
                        ax.plot([str(testNameTestNum[tN]) for tN in testNames], [calcQoeFairness(tempValue) for x in range(len(testNames))], '--', color=chooseColor(nodeType))
                    else:
                        ax.plot(str(testNameTestNum[testName]), calcQoeFairness(tempValue), 'o', color=chooseColor(nodeType))
                    
        if testNames.index(testName) == 0:
            ax.plot(str(testNameTestNum[testName]), calcQoeFairness(tempTest), 'D', color='k', label='All Clients')
            ax.plot([str(testNameTestNum[tN]) for tN in testNames], [calcQoeFairness(tempTest) for x in range(len(testNames))], '--', color='k')
        else:
            ax.plot(str(testNameTestNum[testName]), calcQoeFairness(tempTest), 'D', color='k')

    ax.set_ylim(-0.01,1.01)
    plt.xlabel('Experiment Number')
    plt.ylabel("QoE Fairness")
    plt.legend(bbox_to_anchor=(0.99, 1.03))
    plt.grid(b=None, which='major', axis='both')
    fig.savefig('../exports/plots/mosMetrics/all'+str(len(testNames))+'tests_fairnessQoeAppClass.png', dpi=100, bbox_inches='tight', format='png')
    fig.savefig('../exports/plots/mosMetrics/all'+str(len(testNames))+'tests_fairnessQoeAppClass.pdf', dpi=100, bbox_inches='tight', format='pdf')
    plt.close('all')

def plotBoxAllQoE(testNames, numCLI, nodeTypes, nodeSplit, dataIdent, folderName, nodeTypesToPlot):
    for nodeType,numNodes in zip(nodeTypes,nodeSplit):
        print(nodeType)
        if nodeType in nodeTypesToPlot:
            fig, ax = plt.subplots(1, figsize=(20,15))
            tempNode = []
            for testName in testNames:
                df = importDF(testName, numCLI, nodeTypes, nodeSplit, folderName)
                tempValue = []
                for nodeNum in range(numNodes):
                    colName = makeNodeIdentifier(nodeType, nodeNum) + " " + dataIdent + " Val"
                    data = df[colName].dropna().tolist()
                    if len(data) > 0:
                        tempValue.extend(data)
                tempNode.append(tempValue)
                
            ax.boxplot(tempNode)
            
            ax.set_ylim(0.95,5.05)
            plt.xlabel('Experiment Number')
            plt.ylabel("QoE")
            # plt.legend(bbox_to_anchor=(0.99, 1.03))
            plt.grid(b=None, which='major', axis='both')
            plt.title(chooseName(nodeType))
            fig.savefig('../exports/plots/mosMetrics/all'+str(len(testNames))+'tests_boxQoE_' + nodeType + '.png', dpi=100, bbox_inches='tight', format='png')
            fig.savefig('../exports/plots/mosMetrics/all'+str(len(testNames))+'tests_boxQoE_' + nodeType + '.pdf', dpi=100, bbox_inches='tight', format='pdf')
            plt.close('all')

def plotBoxTestAllQoE(testNames, numCLI, nodeTypes, nodeSplit, dataIdent, folderName, nodeTypesToPlot):
    tempTest = []
    for testName in testNames:
        df = importDF(testName, numCLI, nodeTypes, nodeSplit, folderName)
        tempValue = []
        fig, ax = plt.subplots(1, figsize=(20,15))
        for nodeType,numNodes in zip(nodeTypes,nodeSplit):
            print(nodeType)
            if nodeType in nodeTypesToPlot:
                for nodeNum in range(numNodes):
                    colName = makeNodeIdentifier(nodeType, nodeNum) + " " + dataIdent + " Val"
                    data = df[colName].dropna().tolist()
                    if len(data) > 0:
                        tempValue.extend(data)
        tempTest.append(tempValue)
                
    ax.boxplot(tempTest)
        
    ax.set_ylim(0.95,5.05)
    plt.xlabel('Experiment Number')
    plt.ylabel("QoE")
    # plt.legend(bbox_to_anchor=(0.99, 1.03))
    plt.grid(b=None, which='major', axis='both')
    plt.title('All')
    fig.savefig('../exports/plots/mosMetrics/all'+str(len(testNames))+'tests_boxQoE_all.png', dpi=100, bbox_inches='tight', format='png')
    fig.savefig('../exports/plots/mosMetrics/all'+str(len(testNames))+'tests_boxQoE_all.pdf', dpi=100, bbox_inches='tight', format='pdf')
    plt.close('all')
            

plotMeanQoeAppClass([x for x in testNameTestNum], 250, ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [50 for x in range(5)], 'Mos', 'mos', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'])
plotMeanClientMeanQoeAppClass([x for x in testNameTestNum], 250, ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [50 for x in range(5)], 'Mos', 'mos', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'])
plotMedianQoeAppClass([x for x in testNameTestNum], 250, ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [50 for x in range(5)], 'Mos', 'mos', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'])
plotFairnessQoeAppClass([x for x in testNameTestNum], 250, ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [50 for x in range(5)], 'Mos', 'mos', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'])
plotBoxAllQoE([x for x in testNameTestNum], 250, ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [50 for x in range(5)], 'Mos', 'mos', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'])
plotBoxTestAllQoE([x for x in testNameTestNum], 250, ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [50 for x in range(5)], 'Mos', 'mos', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'])