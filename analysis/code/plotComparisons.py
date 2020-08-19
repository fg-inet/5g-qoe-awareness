import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import csv
import math
import statistics
from scipy import stats
import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(os.path.dirname(currentdir))
print(parentdir)
sys.path.insert(0,parentdir) 
from algorithm import algorithm as algo

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

def getMeanDataTypeAppClass(testName, numCLI, nodeTypes, nodeSplit, dataIdent, folderName, nodeTypesToPlot, sliceConfig):
    df = importDF(testName, numCLI, nodeTypes, nodeSplit, folderName)
    dfRtt = importDF(testName, numCLI, nodeTypes, nodeSplit, 'rtt')
    dfE2ed = importDF(testName, numCLI, nodeTypes, nodeSplit, 'endToEndDelay')
    meanMosFromExperiment = {}
    mosFairnessFromExperiment = {}
    minMosValFromExperiment = {}
    maxMosValFromExperiment = {}
    allData = []
    allDataRtt = []
    allDataE2ed = []

    initBandAss = {}
    for sli in list(sliceConfig):
        initBandAss[sli] = 100/len(list(sliceConfig))
    algoRes = algo.algorithm(sliceConfig, initBandAss, 1000, 0.33, 0.33, 1000, 50, False)
    # print(algoRes)

    algoMeanMos = {}
    algoMeanDelay = {}
    for sli in list(algoRes[8]):
        for cli in list(algoRes[8][sli]):
            # print(sli, cli,algoRes[8][sli][cli])
            algoMeanMos[cli] = algoRes[8][sli][cli]
            algoMeanDelay[cli] = algoRes[7][sli][cli]

    for nodeType,numNodes in zip(nodeTypes,nodeSplit):
        if nodeType in nodeTypesToPlot:
            tempValue = []
            tempValueRtt = []
            tempValueE2ed = []
            for nodeNum in range(numNodes):
                colName = makeNodeIdentifier(nodeType, nodeNum) + " " + dataIdent + " Val"
                data = df[colName].dropna().tolist()
                if len(data) > 0:
                    # normalizedQoEdata = [normalizeQoE(nodeType, x) for x in data]
                    tempValue.append(normalizeQoE(nodeType,statistics.mean(data)))
                    allData.append(normalizeQoE(nodeType,statistics.mean(data)))
                if nodeType != 'hostVIP':
                    colName = makeNodeIdentifier(nodeType, nodeNum) + " rtt Val"
                    data = dfRtt[colName].dropna().tolist()
                    if len(data) > 0:
                        tempValueRtt.append(statistics.mean(data))
                        allDataRtt.append(statistics.mean(data))
                else:
                    colName = makeNodeIdentifier(nodeType, nodeNum) + " E2ED Val"
                    data = dfE2ed[colName].dropna().tolist()
                    if len(data) > 0:
                        tempValueE2ed.append(statistics.mean(data))
                        allDataE2ed.append(statistics.mean(data))

            # print(tempValue)
            print(nodeType + ':')
            meanMosFromExperiment[nodeType] = statistics.mean(tempValue)
            print('\tMean ' + dataIdent + ' of clients: ' + str(statistics.mean(tempValue)) + '; vs. predicted mean: ' + str(algoMeanMos[nodeType]))
            minMosValFromExperiment[nodeType] = min(tempValue)
            print('\tMin ' + dataIdent + ' of clients: ' + str(min(tempValue)))
            maxMosValFromExperiment[nodeType] = max(tempValue)
            print('\tMax ' + dataIdent + ' of clients: ' + str(max(tempValue)))
            mosFairnessFromExperiment[nodeType] = 1 - (2*statistics.stdev(tempValue))/(5.0-1.0)
            print('\tFairness ' + dataIdent + ' of clients: ' + str(1 - (2*statistics.stdev(tempValue))/(5.0-1.0)))
            if nodeType != 'hostVIP':
                print('\tMean delay of clients: ' + str(statistics.mean([x*1000/2 for x in tempValueRtt])) + '; vs. predicted mean: ' + str(algoMeanDelay[nodeType]))
                print('\tMin delay of clients: ' + str(min(tempValueRtt)*1000/2))
                print('\tMax delay of clients: ' + str(max(tempValueRtt)*1000/2))
            else:
                print('\tMean delay of clients: ' + str(statistics.mean([x*1000 for x in tempValueE2ed])) + '; vs. predicted mean: ' + str(algoMeanDelay[nodeType]))
                print('\tMin delay of clients: ' + str(min(tempValueE2ed)*1000))
                print('\tMax delay of clients: ' + str(max(tempValueE2ed)*1000))
            # allData.extend(tempValue)
    print(len(allData))
    print('Mean ' + dataIdent + ' of all clients: ' + str(statistics.mean(allData)) + '; vs. predicted mean: ' + str(algoRes[4]))
    print('Min ' + dataIdent + ' of all clients: ' + str(min(allData)) + '; vs. predicted min: ' + str(algoRes[2][2]))
    print('Max ' + dataIdent + ' of all clients: ' + str(max(allData)) + '; vs. predicted max: ' + str(algoRes[3][2]))
    print('Fairness ' + dataIdent + ' of all clients: ' + str(1 - (2*statistics.stdev(allData))/(5.0-1.0)) + '; vs. predicted fairness: ' + str(algoRes[5]))


def prepConfigName(overallTestName, cliConfig, sliConfig, alpha, metric, minMax):
    numSlices = len(list(sliConfig))
    configName = overallTestName + '_' + str(numSlices) + 'sli_' + str(int(alpha*10)) + 'alpha_'
    for sli in cliConfig:
        for cli in cliConfig[sli]:
            configName += cli[-3:]+str(cliConfig[sli][cli])
    configName += '_'
    for sli in sliConfig:
        configName += 's'+sli[-3:]+str(int(sliConfig[sli]))
    configName += '_' + metric + '_' + minMax

    # if not os.path.exists('genConfigNames/'):
    #     os.makedirs('genConfigNames/')
    # with open('genConfigNames/configNames.txt', mode='a') as writeFile:
    #     writeFile.write(configName+'\n')

    return configName
    
# colorMapping = {
#     'VID' : 'red',
#     'LVD' : 'green', 
#     'FDO' : 'orange', 
#     'SSH' : 'blue', 
#     'VIP' : 'purple',
#     'all' : 'black'
# }
colormap = plt.get_cmap('tab10').colors
print(colormap)
colorMapping = {
    'VID' : colormap[0],
    'LVD' : colormap[1], 
    'FDO' : colormap[2], 
    'SSH' : colormap[3], 
    'VIP' : colormap[4],
    'all' : colormap[5]
}

markerMapping = {
    'VID' : 's',
    'LVD' : 'D', 
    'FDO' : 'o', 
    'SSH' : 'P', 
    'VIP' : 'X',
    'all' : '*'
}

nameMapping = {
    'VID' : 'VoD',
    'LVD' : 'Live', 
    'FDO' : 'Download', 
    'SSH' : 'SSH', 
    'VIP' : 'VoIP',
    'all' : 'All'
}

def plotChosenAssignments(algoResName, algoType, alphas, metrics, minMaxes):
    chosenAlphaList = []
    chosenMetric = []
    chosenMinMax = []
    chosenCliConfigs = []
    chosenAssignments = []
    chosenObjFunc = []
    chosenMinMos = []
    chosenMaxMos = []
    chosenAvgMos = []
    chosenMosFairness = []
    chosenMeanBandSlice = []
    chosenEstimDelaySlice = []
    chosenEstMosSlice = []

    testNumbers = []
    testNumbersAlpha = []
    prettyTestNames = []
    prettyTestNamesAlpha = []
    
    for metric in metrics:
        for minMax in minMaxes:
            file_to_read = '../../algorithm/selectedConfigsRes/'+algoResName + algoType + 'alphas' + str(alphas)+metric+minMax+'.csv'
            with open(file_to_read, mode='r') as readFile:
                csv_reader = csv.reader(readFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
                line_count = 0
                for row in csv_reader:
                    if line_count == 0:
                        chosenAlphaList.extend(row)
                    elif line_count == 1:
                        chosenMetric.extend(row)
                    elif line_count == 2:
                        chosenMinMax.extend(row)
                    elif line_count == 3:
                        chosenCliConfigs.extend([eval(x) for x in row])
                    elif line_count == 4:
                        chosenAssignments.extend([eval(x) for x in row])
                    elif line_count == 5:
                        chosenObjFunc.extend(row)
                    elif line_count == 6:
                        chosenMinMos.extend([eval(x) for x in row])
                    elif line_count == 7:
                        chosenMaxMos.extend([eval(x) for x in row])
                    elif line_count == 8:
                        chosenAvgMos.extend(row)
                    elif line_count == 9:
                        chosenMosFairness.extend(row)
                    elif line_count == 10:
                        chosenMeanBandSlice.extend([eval(x) for x in row])
                    elif line_count == 11:
                        chosenEstimDelaySlice.extend([eval(x) for x in row])
                    elif line_count == 12:
                        chosenEstMosSlice.extend([eval(x) for x in row])
                    line_count += 1
    for i in range(len(chosenAlphaList)):
        testNumbers.append('C' + str(i+1))
        testNumbersAlpha.append('C' + str(i+1) + '; \u03B1 = ' + str(float(chosenAlphaList[i])))
        prettyTestNames.append('Config ' + str(i+1))
        prettyTestNamesAlpha.append('Config ' + str(i+1) + '; \u03B1 = ' + str(float(chosenAlphaList[i])))
        # prettyTestNames.append(str(float(chosenAlphaList[i])/10) + '-' + chosenMetric[i]+'-'+chosenMinMax[i])
    # print(prettyTestNames)
    
    fig, ax1 = plt.subplots(1, figsize=(16,12))
    for x in chosenCliConfigs[0]:
        # print(x)
        cliXnum = []
        for i in range(len(chosenCliConfigs)):
            cliXnum.append(chosenCliConfigs[i][x]['host'+x[-3:]])
            # print(chosenCliConfigs[i][x]['host'+x[-3:]])
        ax1.plot(testNumbers, cliXnum, label=nameMapping[x[-3:]] + ' Client', marker=markerMapping[x[-3:]], ls='', color=colorMapping[x[-3:]])
    ax1.set_ylim(0,105)
    ax1.set_ylabel('Number of clients')
    ax1.set_xlabel('Client Configuration')
    plt.xticks(rotation=90)
    plt.legend()
    ax1.legend(bbox_to_anchor=(0.4, -0.45))
    plt.grid(True)
    if not os.path.exists('compPlots/variousCliNumTests/'+algoResName+'/'):
        os.makedirs('compPlots/variousCliNumTests/'+algoResName+'/')
    outPath = 'compPlots/variousCliNumTests/'+algoResName+'/clientNumbers.pdf'
    fig.savefig(outPath, dpi=100, bbox_inches='tight')
    outPath = 'compPlots/variousCliNumTests/'+algoResName+'/clientNumbers.png'
    fig.savefig(outPath, dpi=100, bbox_inches='tight')
    plt.close('all')

    fig, ax1 = plt.subplots(1, figsize=(16,12))
    for x in chosenAssignments[0]:
        sliceXass = []
        for ass in chosenAssignments:
            sliceXass.append(ass[x])
        ax1.plot(testNumbersAlpha, sliceXass, label=nameMapping[x[-3:]] + ' Slice', marker=markerMapping[x[-3:]], ls='', color=colorMapping[x[-3:]])
    ax1.set_ylim(0,60)
    ax1.set_ylabel('Number of Assigned Resource Blocks')
    ax1.set_xlabel('Configuration')
    plt.xticks(rotation=90)
    plt.legend()
    ax1.legend(bbox_to_anchor=(0.4, -0.45))
    plt.grid(True)
    outPath = 'compPlots/variousCliNumTests/'+algoResName+'/rbAssignment.pdf'
    fig.savefig(outPath, dpi=100, bbox_inches='tight')
    outPath = 'compPlots/variousCliNumTests/'+algoResName+'/rbAssignment.png'
    fig.savefig(outPath, dpi=100, bbox_inches='tight')
    plt.close('all')

    
    
    extractedMeanMos = {}
    extractedDelay = {}
    extractedFairness = {}
    extractedMinMos = []
    extractedMaxMos = []

    nodeTypes = ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP']
    for nT in nodeTypes:
        extractedMeanMos[nT] = []
        extractedDelay[nT] = []
        extractedFairness[nT] = []
    extractedMeanMos['overall'] = []
    extractedDelay['overall'] = []
    extractedFairness['overall'] = []

    for i in range(len(chosenAlphaList)):
        print('Importing Simulation Results: Test Case', i+1, 'out of', len(chosenAlphaList))
        testName = prepConfigName('optimizationAlgo'+algoType, chosenCliConfigs[i], chosenAssignments[i], chosenAlphaList[i], chosenMetric[i], chosenMinMax[i])
        tempCliConfs = {}
        for x in chosenCliConfigs[i]:
            for y in chosenCliConfigs[i][x]:
                tempCliConfs[y] = chosenCliConfigs[i][x][y]
        
        nodeSplit = []
        for x in nodeTypes:
            nodeSplit.append(tempCliConfs[x])
        df = importDF(testName, sum(nodeSplit), nodeTypes, nodeSplit, 'mos')
        dfRtt = importDF(testName, sum(nodeSplit), nodeTypes, nodeSplit, 'rtt')
        dfE2ed = importDF(testName, sum(nodeSplit), nodeTypes, nodeSplit, 'endToEndDelay')
        allData = []
        allDataRtt = []
        allDataE2ed = []
        for nodeType,numNodes in zip(nodeTypes,nodeSplit):
            tempValue = []
            tempValueRtt = []
            tempValueE2ed = []
            for nodeNum in range(numNodes):
                colName = makeNodeIdentifier(nodeType, nodeNum) + " Mos Val"
                data = df[colName].dropna().tolist()
                if len(data) > 0:
                    # normalizedQoEdata = [normalizeQoE(nodeType, x) for x in data]
                    tempValue.append(normalizeQoE(nodeType,statistics.mean(data)))
                    allData.append(normalizeQoE(nodeType,statistics.mean(data)))
                if nodeType != 'hostVIP':
                    colName = makeNodeIdentifier(nodeType, nodeNum) + " rtt Val"
                    data = dfRtt[colName].dropna().tolist()
                    if len(data) > 0:
                        tempValueRtt.append(statistics.mean(data))
                        allDataRtt.append(statistics.mean(data))
                else:
                    colName = makeNodeIdentifier(nodeType, nodeNum) + " E2ED Val"
                    data = dfE2ed[colName].dropna().tolist()
                    if len(data) > 0:
                        tempValueE2ed.append(statistics.mean(data))
                        allDataE2ed.append(statistics.mean(data))
            if len(tempValue) > 0: extractedMeanMos[nodeType].append(statistics.mean(tempValue))
            else: extractedMeanMos[nodeType].append(-1.0)
            if nodeType != 'hostVIP':
                extractedDelay[nodeType].append(statistics.mean([x*1000/2 for x in tempValueRtt]))
            else:
                extractedDelay[nodeType].append(statistics.mean([x*1000 for x in tempValueE2ed]))
            
            if len(tempValue) > 1: extractedFairness[nodeType].append(1 - (2*statistics.stdev(tempValue))/(5.0-1.0))
            else: extractedFairness[nodeType].append(-1.0)
        
        extractedMeanMos['overall'].append(statistics.mean(allData))
        extractedMinMos.append(min(allData))
        extractedMaxMos.append(max(allData))
        if nodeType != 'hostVIP':
            extractedDelay['overall'].append(statistics.mean([x*1000/2 for x in allDataRtt]))
        else:
            extractedDelay['overall'].append(statistics.mean([x*1000 for x in allDataE2ed]))
        extractedFairness['overall'].append(1 - (2*statistics.stdev(allData))/(5.0-1.0))
    
    print(extractedMeanMos, extractedDelay, extractedFairness)
    
    fig, ax1 = plt.subplots(1, figsize=(16,12))
    ax1.plot(prettyTestNames, [x[2] for x in chosenMinMos], label='Estimated Minimal Utility', marker='+', ls='--', color='red')
    ax1.plot(prettyTestNames, [x[2] for x in chosenMaxMos], label='Estimated Maximal Utility', marker='+', ls='--', color='green')
    ax1.plot(prettyTestNames, chosenAvgMos, label='Estimated Mean Utility', marker='+', ls='--', color='blue')
    ax1.plot(prettyTestNames, extractedMinMos, label='Actual Minimal Utility', marker='o', ls='-', color='red')
    ax1.plot(prettyTestNames, extractedMaxMos, label='Actual Maximal Utility', marker='o', ls='-', color='green')
    ax1.plot(prettyTestNames, extractedMeanMos['overall'], label='Actual Mean Utility', marker='o', ls='-', color='blue')
    ax1.set_ylim(0.95,5.05)
    ax1.set_ylabel('Utility')
    ax1.set_xlabel('Test Identifier')
    plt.xticks(rotation=90)
    plt.legend()
    ax1.legend(bbox_to_anchor=(0.4, -0.45))
    plt.grid(True)
    outPath = 'compPlots/variousCliNumTests/'+algoResName+'/mos.pdf'
    fig.savefig(outPath, dpi=100, bbox_inches='tight')
    outPath = 'compPlots/variousCliNumTests/'+algoResName+'/mos.png'
    fig.savefig(outPath, dpi=100, bbox_inches='tight')
    plt.close('all')

    fig, ax1 = plt.subplots(1, figsize=(16,12))
    for x in chosenEstMosSlice[0]:
        cliXnum = []
        for i in range(len(chosenEstMosSlice)):
            cliXnum.append(chosenEstMosSlice[i][x]['host'+x[-3:]])
        ax1.plot(prettyTestNames, cliXnum, label='Estimated Client ' + x[-3:], marker='+', ls='--', color=colorMapping[x[-3:]])
        plotVals = np.array(extractedMeanMos['host'+x[-3:]])
        ax1.plot(np.array(prettyTestNames)[plotVals >= 1.0], plotVals[plotVals >= 1.0], label='Actual Client ' + x[-3:], marker='o', ls='-', color=colorMapping[x[-3:]])
    # ax1.plot(testNum, avgMos, label='Mean Utility', marker='o', ls='-')
    ax1.set_ylim(0.95,5.05)
    ax1.set_ylabel('Utility')
    ax1.set_xlabel('Test Identifier')
    plt.xticks(rotation=90)
    plt.legend()
    ax1.legend(bbox_to_anchor=(0.4, -0.45))
    plt.grid(True)
    outPath = 'compPlots/variousCliNumTests/'+algoResName+'/meanCliTypeMos.pdf'
    fig.savefig(outPath, dpi=100, bbox_inches='tight')
    outPath = 'compPlots/variousCliNumTests/'+algoResName+'/meanCliTypeMos.png'
    fig.savefig(outPath, dpi=100, bbox_inches='tight')
    plt.close('all')

    fig, ax1 = plt.subplots(1, figsize=(16,12))
    for x in chosenEstimDelaySlice[0]:
        cliXnum = []
        for i in range(len(chosenEstimDelaySlice)):
            cliXnum.append(chosenEstimDelaySlice[i][x]['host'+x[-3:]])
        ax1.plot(prettyTestNames, cliXnum, label='Estimated Client ' + x[-3:], marker='+', ls='--', color=colorMapping[x[-3:]])
        ax1.plot(prettyTestNames, extractedDelay['host'+x[-3:]], label='Actual Client ' + x[-3:], marker='o', ls='-', color=colorMapping[x[-3:]])
    # ax1.plot(testNum, avgMos, label='Mean Utility', marker='o', ls='-')
    ax1.set_ylim(0,1000)
    ax1.set_ylabel('Delay [ms]')
    ax1.set_xlabel('Test Identifier')
    plt.xticks(rotation=90)
    plt.legend()
    ax1.legend(bbox_to_anchor=(0.4, -0.45))
    plt.grid(True)
    outPath = 'compPlots/variousCliNumTests/'+algoResName+'/cliTypeDelay.pdf'
    fig.savefig(outPath, dpi=100, bbox_inches='tight')
    outPath = 'compPlots/variousCliNumTests/'+algoResName+'/cliTypeDelay.png'
    fig.savefig(outPath, dpi=100, bbox_inches='tight')
    plt.close('all')

    fig, ax1 = plt.subplots(1, figsize=(16,12))
    ax1.plot(prettyTestNames, chosenMosFairness, label='Estimated Overall', marker='+', ls='--', color='brown')
    ax1.plot(prettyTestNames, extractedFairness['overall'], label='Actual Overall', marker='o', ls='-', color='brown')
    for nT in nodeTypes:
        plotVals = np.array(extractedFairness[nT])
        ax1.plot(np.array(prettyTestNames)[plotVals >= 0.0], plotVals[plotVals >= 0.0], label='Actual Client ' + nT[-3:], marker='o', ls='-', color=colorMapping[nT[-3:]])
    ax1.set_ylim(-0.01,1.01)
    ax1.set_ylabel('Fairness')
    ax1.set_xlabel('Test Identifier')
    plt.xticks(rotation=90)
    plt.legend()
    ax1.legend(bbox_to_anchor=(0.4, -0.45))
    plt.grid(True)
    outPath = 'compPlots/variousCliNumTests/'+algoResName+'/fairness.pdf'
    fig.savefig(outPath, dpi=100, bbox_inches='tight')
    outPath = 'compPlots/variousCliNumTests/'+algoResName+'/fairness.png'
    fig.savefig(outPath, dpi=100, bbox_inches='tight')
    plt.close('all')

# plotChosenAssignments('5sliTestVariousCliNums[5-20-50-75-100]', 'Fairness1', [0.0, 0.5, 1.0], ['fairness', 'min', 'mean'], ['max', 'min'])


def extractTestInfo(testName, nodeTypes, nodeSplit, alpha):
    # print('Importing Simulation Results: Test Case', i+1, 'out of', len(chosenAlphaList))
    # testName = prepConfigName('optimizationAlgo'+algoType, chosenCliConfigs[i], chosenAssignments[i], chosenAlphaList[i], chosenMetric[i], chosenMinMax[i])
    df = importDF(testName, sum(nodeSplit), nodeTypes, nodeSplit, 'mos')
    dfRtt = importDF(testName, sum(nodeSplit), nodeTypes, nodeSplit, 'rtt')
    dfE2ed = importDF(testName, sum(nodeSplit), nodeTypes, nodeSplit, 'endToEndDelay')
    extractedMeanMos = {}
    extractedDelay = {}
    extractedFairness = {}
    allData = []
    allDataRtt = []
    allDataE2ed = []
    for nodeType,numNodes in zip(nodeTypes,nodeSplit):
        tempValue = []
        tempValueRtt = []
        tempValueE2ed = []
        for nodeNum in range(numNodes):
            colName = makeNodeIdentifier(nodeType, nodeNum) + " Mos Val"
            data = df[colName].dropna().tolist()
            if len(data) > 0:
                # normalizedQoEdata = [normalizeQoE(nodeType, x) for x in data]
                tempValue.append(normalizeQoE(nodeType,statistics.mean(data)))
                allData.append(normalizeQoE(nodeType,statistics.mean(data)))
            else:
                tempValue.append(1.0)
                allData.append(1.0)
            if nodeType != 'hostVIP':
                colName = makeNodeIdentifier(nodeType, nodeNum) + " rtt Val"
                data = dfRtt[colName].dropna().tolist()
                if len(data) > 0:
                    tempValueRtt.append(statistics.mean(data))
                    allDataRtt.append(statistics.mean(data))
            else:
                colName = makeNodeIdentifier(nodeType, nodeNum) + " E2ED Val"
                data = dfE2ed[colName].dropna().tolist()
                if len(data) > 0:
                    tempValueE2ed.append(statistics.mean(data))
                    allDataE2ed.append(statistics.mean(data))
        if len(tempValue) > 0: extractedMeanMos[nodeType] = statistics.mean(tempValue)
        else: extractedMeanMos[nodeType] = -1.0
        if nodeType != 'hostVIP':
            if len(tempValueRtt) > 0: extractedDelay[nodeType] = statistics.mean([x*1000/2 for x in tempValueRtt])
            else: extractedDelay[nodeType] = -1
        else:
            extractedDelay[nodeType] = statistics.mean([x*1000 for x in tempValueE2ed])
        
        if len(tempValue) > 1: extractedFairness[nodeType] = 1 - (2*statistics.stdev(tempValue))/(5.0-1.0)
        else: extractedFairness[nodeType] = -1.0
    
    extractedMeanMos['overall'] = statistics.mean(allData)
    extractedMinMos = min(allData)
    extractedMaxMos = max(allData)
    tempDelay = [x*1000 for x in allDataE2ed]
    tempDelay.extend([x*1000/2 for x in allDataRtt])
    extractedDelay['overall'] = statistics.mean(tempDelay)
    extractedFairness['overall'] = 1 - (2*statistics.stdev(allData))/(5.0-1.0)
    # print(testName)
    # print(nodeTypes)
    # print(nodeSplit)
    # print(alpha)
    # print(extractedMinMos)
    # print(extractedMaxMos)
    # print(extractedMeanMos)
    # print(extractedDelay)
    # print(extractedFairness)
    if not os.path.exists('../exports/compExports/'):
        os.makedirs('../exports/compExports/')
    with open('../exports/compExports/' + testName + '.csv', mode='w') as writeFile:
            fw = csv.writer(writeFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
            fw.writerow([testName])
            fw.writerow(nodeTypes)
            fw.writerow(nodeSplit)
            fw.writerow([alpha])
            fw.writerow([extractedMinMos])
            fw.writerow([extractedMaxMos])
            fw.writerow([extractedMeanMos])
            fw.writerow([extractedDelay])
            fw.writerow([extractedFairness])

testNames5sli = ['optimizationAlgoFairness1_5sli_0alpha_SSH100VIP75VID20LVD5FDO50_sSSH3sVIP44sVID14sLVD2sFDO37_fairness_max', 
'optimizationAlgoFairness1_5sli_5alpha_SSH100VIP20VID75LVD5FDO50_sSSH1sVIP12sVID51sLVD6sFDO30_fairness_max', 
'optimizationAlgoFairness1_5sli_10alpha_SSH100VIP20VID75LVD5FDO50_sSSH1sVIP12sVID51sLVD6sFDO30_fairness_max', 
'optimizationAlgoFairness1_5sli_0alpha_SSH100VIP20VID50LVD5FDO75_sSSH4sVIP12sVID35sLVD6sFDO43_min_max', 
'optimizationAlgoFairness1_5sli_5alpha_SSH100VIP50VID20LVD5FDO75_sSSH1sVIP29sVID15sLVD6sFDO49_min_max', 
'optimizationAlgoFairness1_5sli_10alpha_SSH100VIP50VID20LVD5FDO75_sSSH1sVIP29sVID15sLVD6sFDO49_min_max', 
'optimizationAlgoFairness1_5sli_0alpha_SSH100VIP75VID20LVD5FDO50_sSSH3sVIP44sVID14sLVD2sFDO37_mean_max', 
'optimizationAlgoFairness1_5sli_5alpha_SSH100VIP75VID50LVD5FDO20_sSSH2sVIP44sVID34sLVD6sFDO14_mean_max', 
'optimizationAlgoFairness1_5sli_10alpha_SSH100VIP75VID50LVD5FDO20_sSSH1sVIP44sVID34sLVD6sFDO15_mean_max', 
'optimizationAlgoFairness1_5sli_0alpha_SSH50VIP75VID100LVD5FDO20_sSSH7sVIP45sVID20sLVD7sFDO21_fairness_min', 
'optimizationAlgoFairness1_5sli_5alpha_SSH20VIP100VID75LVD5FDO50_sSSH1sVIP58sVID37sLVD3sFDO1_fairness_min', 
'optimizationAlgoFairness1_5sli_10alpha_SSH50VIP100VID5LVD20FDO75_sSSH1sVIP36sVID20sLVD20sFDO23_fairness_min', 
'optimizationAlgoFairness1_5sli_0alpha_SSH5VIP75VID100LVD20FDO50_sSSH1sVIP44sVID48sLVD6sFDO1_min_min', 
'optimizationAlgoFairness1_5sli_5alpha_SSH20VIP100VID75LVD5FDO50_sSSH1sVIP58sVID37sLVD3sFDO1_min_min', 
'optimizationAlgoFairness1_5sli_10alpha_SSH5VIP50VID75LVD100FDO20_sSSH18sVIP28sVID29sLVD22sFDO3_min_min', 
'optimizationAlgoFairness1_5sli_0alpha_SSH5VIP100VID50LVD75FDO20_sSSH1sVIP1sVID50sLVD22sFDO26_mean_min', 
'optimizationAlgoFairness1_5sli_5alpha_SSH5VIP100VID75LVD20FDO50_sSSH25sVIP26sVID32sLVD6sFDO11_mean_min', 
'optimizationAlgoFairness1_5sli_10alpha_SSH5VIP75VID50LVD100FDO20_sSSH15sVIP42sVID18sLVD22sFDO3_mean_min']
testNamesBaseline = ['baselineTestVCD_SSH100VIP75VID20LVD5FDO50', 
'baselineTestVCD_SSH100VIP20VID75LVD5FDO50', 
'baselineTestVCD_SSH50VIP75VID100LVD5FDO20', 
'baselineTestVCD_SSH20VIP100VID75LVD5FDO50', 
'baselineTestVCD_SSH50VIP100VID5LVD20FDO75', 
'baselineTestVCD_SSH100VIP20VID50LVD5FDO75', 
'baselineTestVCD_SSH100VIP50VID20LVD5FDO75', 
'baselineTestVCD_SSH5VIP75VID100LVD20FDO50', 
'baselineTestVCD_SSH5VIP50VID75LVD100FDO20', 
'baselineTestVCD_SSH100VIP75VID50LVD5FDO20', 
'baselineTestVCD_SSH5VIP100VID50LVD75FDO20', 
'baselineTestVCD_SSH5VIP100VID75LVD20FDO50', 
'baselineTestVCD_SSH5VIP75VID50LVD100FDO20']
testNames2sli = ['optimizationAlgoFairness1_2sli_LVD-BWS_0alpha_SSH100VIP75VID20LVD5FDO50_sDES46sBWS54_ndf_ndf', 
'optimizationAlgoFairness1_2sli_LVD-BWS_5alpha_SSH100VIP20VID75LVD5FDO50_sDES14sBWS86_ndf_ndf', 
'optimizationAlgoFairness1_2sli_LVD-BWS_10alpha_SSH100VIP20VID75LVD5FDO50_sDES14sBWS86_ndf_ndf', 
'optimizationAlgoFairness1_2sli_LVD-BWS_0alpha_SSH50VIP75VID100LVD5FDO20_sDES46sBWS54_ndf_ndf', 
'optimizationAlgoFairness1_2sli_LVD-BWS_5alpha_SSH20VIP100VID75LVD5FDO50_sDES58sBWS42_ndf_ndf', 
'optimizationAlgoFairness1_2sli_LVD-BWS_10alpha_SSH50VIP100VID5LVD20FDO75_sDES59sBWS41_ndf_ndf', 
'optimizationAlgoFairness1_2sli_LVD-BWS_0alpha_SSH100VIP20VID50LVD5FDO75_sDES15sBWS85_ndf_ndf', 
'optimizationAlgoFairness1_2sli_LVD-BWS_5alpha_SSH100VIP50VID20LVD5FDO75_sDES31sBWS69_ndf_ndf', 
'optimizationAlgoFairness1_2sli_LVD-BWS_10alpha_SSH100VIP50VID20LVD5FDO75_sDES31sBWS69_ndf_ndf', 
'optimizationAlgoFairness1_2sli_LVD-BWS_0alpha_SSH5VIP75VID100LVD20FDO50_sDES47sBWS53_ndf_ndf', 
'optimizationAlgoFairness1_2sli_LVD-BWS_5alpha_SSH20VIP100VID75LVD5FDO50_sDES58sBWS42_ndf_ndf', 
'optimizationAlgoFairness1_2sli_LVD-BWS_10alpha_SSH5VIP50VID75LVD100FDO20_sDES18sBWS82_ndf_ndf', 
'optimizationAlgoFairness1_2sli_LVD-BWS_0alpha_SSH100VIP75VID20LVD5FDO50_sDES46sBWS54_ndf_ndf', 
'optimizationAlgoFairness1_2sli_LVD-BWS_5alpha_SSH100VIP75VID50LVD5FDO20_sDES46sBWS54_ndf_ndf', 
'optimizationAlgoFairness1_2sli_LVD-BWS_10alpha_SSH100VIP75VID50LVD5FDO20_sDES46sBWS54_ndf_ndf', 
'optimizationAlgoFairness1_2sli_LVD-BWS_0alpha_SSH5VIP100VID50LVD75FDO20_sDES60sBWS40_ndf_ndf', 
'optimizationAlgoFairness1_2sli_LVD-BWS_5alpha_SSH5VIP100VID75LVD20FDO50_sDES57sBWS43_ndf_ndf', 
'optimizationAlgoFairness1_2sli_LVD-BWS_10alpha_SSH5VIP75VID50LVD100FDO20_sDES43sBWS57_ndf_ndf']
alphas2or5sli = [0.0, 0.5, 1.0, 0.0, 0.5, 1.0, 0.0, 0.5, 1.0, 0.0, 0.5, 1.0, 0.0, 0.5, 1.0, 0.0, 0.5, 1.0]
alphasBaseline = [-1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0]
nodeSplits = [[20,5,50,100,75],
[75,5,50,100,20], 
[75,5,50,100,20], 
[50,5,75,100,20], 
[20,5,75,100,50], 
[20,5,75,100,50], 
[20,5,50,100,75], 
[50,5,20,100,75], 
[50,5,20,100,75], 
[100,5,20,50,75], 
[75,5,50,20,100], 
[5,20,75,50,100], 
[100,20,50,5,75], 
[75,5,50,20,100], 
[75,100,20,5,50], 
[50,75,20,5,100], 
[75,20,50,5,100], 
[50,100,20,5,75]]

for i in range(len(alphas2or5sli)):
    # print('Exporting experiment ' + str(i+1) + ' out of 56: ' + testNames5sli[i])
    tempSSH = testNames5sli[i].split('_SSH')[1].split('VIP')
    tempVIP = tempSSH[1].split('VID')
    tempVID = tempVIP[1].split('LVD')
    tempLVD = tempVID[1].split('FDO')
    tempFDO = tempLVD[1].split('_sSSH')
    nSplit = [int(tempVID[0]), int(tempLVD[0]), int(tempFDO[0]), int(tempSSH[0]), int(tempVIP[0])]
    print('C'+str(i+1), alphas2or5sli[i], nSplit)
    # extractTestInfo(testNames5sli[i], ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], nSplit, alphas2or5sli[i])
# for i in range(len(alphas2or5sli)):
#     print('Exporting experiment ' + str(i+19) + ' out of 56: ' + testNames2sli[i])
#     tempSSH = testNames2sli[i].split('_SSH')[1].split('VIP')
#     tempVIP = tempSSH[1].split('VID')
#     tempVID = tempVIP[1].split('LVD')
#     tempLVD = tempVID[1].split('FDO')
#     tempFDO = tempLVD[1].split('_sDES')
#     nSplit = [int(tempVID[0]), int(tempLVD[0]), int(tempFDO[0]), int(tempSSH[0]), int(tempVIP[0])]
#     extractTestInfo(testNames2sli[i], ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], nSplit, alphas2or5sli[i])

# for i in range(len(alphasBaseline)):
#     print('Exporting experiment ' + str(i+37) + ' out of 56: ' + testNamesBaseline[i])
#     # print('\tlil: ', int(tempVID[0]), int(tempLVD[0]), int(tempFDO), int(tempSSH[0]), int(tempVIP[0]))
#     tempSSH = testNamesBaseline[i].split('_SSH')[1].split('VIP')
#     tempVIP = tempSSH[1].split('VID')
#     tempVID = tempVIP[1].split('LVD')
#     tempLVD = tempVID[1].split('FDO')
#     tempFDO = tempLVD[1]
#     nSplit = [int(tempVID[0]), int(tempLVD[0]), int(tempFDO), int(tempSSH[0]), int(tempVIP[0])]
#     extractTestInfo(testNamesBaseline[i], ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], nSplit, alphasBaseline[i])
    

# extractTestInfo('baselineTestVCD_SSH100VIP75VID20LVD5FDO50', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [20, 5, 50, 100, 75], -1.0)
# print('Exporting experiment 50 out of 56: ' + 'baselineTest')
# extractTestInfo('baselineTest', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [50 for _ in range(5)], -1.0)
# print('Exporting experiment 51 out of 56: ' + 'baselineTestNS_5sli_AlgoTest_alpha00')
# extractTestInfo('baselineTestNS_5sli_AlgoTest_alpha00', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [50 for _ in range(5)], 0.0)
# print('Exporting experiment 52 out of 56: ' + 'baselineTestNS_5sli_AlgoTest_alpha05')
# extractTestInfo('baselineTestNS_5sli_AlgoTest_alpha05', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [50 for _ in range(5)], 0.5)
# print('Exporting experiment 53 out of 56: ' + 'baselineTestNS_5sli_AlgoTest_alpha10')
# extractTestInfo('baselineTestNS_5sli_AlgoTest_alpha10', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [50 for _ in range(5)], 1.0)
# print('Exporting experiment 54 out of 56: ' + 'baselineTestNS_2sli_LVD-BWS_AlgoTest_alpha00')
# extractTestInfo('baselineTestNS_2sli_LVD-BWS_AlgoTest_alpha00', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [50 for _ in range(5)], 0.0)
# print('Exporting experiment 55 out of 56: ' + 'baselineTestNS_2sli_LVD-BWS_AlgoTest_alpha05')
# extractTestInfo('baselineTestNS_2sli_LVD-BWS_AlgoTest_alpha05', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [50 for _ in range(5)], 0.5)
# print('Exporting experiment 56 out of 56: ' + 'baselineTestNS_2sli_LVD-BWS_AlgoTest_alpha10')
# extractTestInfo('baselineTestNS_2sli_LVD-BWS_AlgoTest_alpha10', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [50 for _ in range(5)], 1.0)
# print('\nFinished!\n\nTotal number of exported files should be: 54 (Due to two doubled optimizationAlgoFairness1_2sli_LVD-BWS experiments)')


def importResCompExports(testName):
    # print(testName.split('_')[4])
    fileToImport = '../exports/compExports/' + testName + '.csv'
    minMos = []
    maxMos = []
    avgMos = []
    delays = []
    fairness = []
    with open(fileToImport, mode='r') as readFile:
        csv_reader = csv.reader(readFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
        line_count = 0
        for row in csv_reader:
            if line_count == 4:
                minMos = row[0]
            elif line_count == 5:
                maxMos = row[0]
            elif line_count == 6:
                avgMos = eval(row[0])
            elif line_count == 7:
                delays = eval(row[0])
            elif line_count == 8:
                fairness = eval(row[0])
            line_count += 1
    # print(minMos, maxMos, avgMos, delays, fairness)
    return minMos, maxMos, avgMos, delays, fairness

def import5sliPredictions(importName, testName, alpha):
    # print(testName)
    # importName = '5sliTestVariousCliNums[5-20-50-75-100]Fairness1alphas[0.0, 0.5, 1.0]'+testName.split('_')[-2]+testName.split('_')[-1]
    fileToImport = '../../algorithm/selectedConfigsRes/' + importName + '.csv'
    
    with open(fileToImport, mode='r') as readFile:
        csv_reader = csv.reader(readFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                chosenAlphaList = row
                # print(chosenAlphaList)
            elif line_count == 1:
                chosenMetric = row
                # print(chosenMetric)
            elif line_count == 2:
                chosenMinMax = row
            elif line_count == 3:
                chosenCliConfigs = row
            elif line_count == 4:
                chosenAssignments = row
            elif line_count == 5:
                chosenObjFunc = row
            elif line_count == 6:
                chosenMinMos = row
            elif line_count == 7:
                chosenMaxMos = row
            elif line_count == 8:
                chosenAvgMos = row
            elif line_count == 9:
                chosenMosFairness = row
            elif line_count == 10:
                chosenMeanBandSlice = row
            elif line_count == 11:
                chosenEstimDelaySlice = row
            elif line_count == 12:
                chosenEstMosSlice = row
            line_count += 1
    # print(chosenMinMos)
    minMos = eval(chosenMinMos[chosenAlphaList.index(alpha)])[2]
    maxMos = eval(chosenMaxMos[chosenAlphaList.index(alpha)])[2]
    avgMosTemp = eval(chosenEstMosSlice[chosenAlphaList.index(alpha)])
    avgMos = {}
    for sli in avgMosTemp:
        for cli in avgMosTemp[sli]:
            avgMos[cli] = avgMosTemp[sli][cli]
    avgMos['overall'] = chosenAvgMos[chosenAlphaList.index(alpha)]
    delaysTemp = eval(chosenEstimDelaySlice[chosenAlphaList.index(alpha)])
    delays = {}
    sumDelays = 0
    for sli in delaysTemp:
        for cli in delaysTemp[sli]:
            delays[cli] = delaysTemp[sli][cli]
            sumDelays = delaysTemp[sli][cli] * eval(chosenCliConfigs[chosenAlphaList.index(alpha)])[sli][cli]
    delays['overall'] = sumDelays / 250
    fairness = {}
    fairness['overall'] = chosenMosFairness[chosenAlphaList.index(alpha)]
    # print(minMos, maxMos, avgMos, delays, fairness)
    return minMos, maxMos, avgMos, delays, fairness

def import2sliPredictions(importName, testName, alpha, i):
    # print(testName)
    # importName = '2sliLVD_BWSTestVariousCliNums[5-20-50-75-100]Fairness1alphas[0.0, 0.5, 1.0]'
    fileToImport = '../../algorithm/' + importName + '.csv'
    
    with open(fileToImport, mode='r') as readFile:
        csv_reader = csv.reader(readFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                chosenAlphaList = row
            elif line_count == 1:
                chosenCliConfigs = row
            elif line_count == 2:
                chosenAssignments = row
            elif line_count == 3:
                chosenObjFunc = row
            elif line_count == 4:
                chosenMinMos = row
            elif line_count == 5:
                chosenMaxMos = row
            elif line_count == 6:
                chosenAvgMos = row
            elif line_count == 7:
                chosenMosFairness = row
            elif line_count == 8:
                chosenMeanBandSlice = row
            elif line_count == 9:
                chosenEstimDelaySlice = row
            elif line_count == 10:
                chosenEstMosSlice = row
            line_count += 1
    minMos = eval(chosenMinMos[chosenAlphaList.index(alpha)])[2]
    # print(chosenCliConfigs[i])
    maxMos = eval(chosenMaxMos[chosenAlphaList.index(alpha)])[2]
    avgMosTemp = eval(chosenEstMosSlice[chosenAlphaList.index(alpha)])
    avgMos = {}
    for sli in avgMosTemp:
        for cli in avgMosTemp[sli]:
            avgMos[cli] = avgMosTemp[sli][cli]
    avgMos['overall'] = chosenAvgMos[chosenAlphaList.index(alpha)]
    delaysTemp = eval(chosenEstimDelaySlice[chosenAlphaList.index(alpha)])
    delays = {}
    sumDelays = 0

    for sli in delaysTemp:
        for cli in delaysTemp[sli]:
            delays[cli] = delaysTemp[sli][cli]
            sumDelays = delaysTemp[sli][cli] * eval(chosenCliConfigs[chosenAlphaList.index(alpha)])[sli][cli]
            
    delays['overall'] = sumDelays / 250
    fairness = {}
    fairness['overall'] = chosenMosFairness[chosenAlphaList.index(alpha)]
    # print(minMos, maxMos, avgMos, delays, fairness)
    return minMos, maxMos, avgMos, delays, fairness

def plotMeanDataTypeClientType(baselineTestNames, C2sliTestNames, C5sliTestNames, C2sliAlphas, C5sliAlphas, nodeTypes, nodeSplits, exportName, xAxisValues, experimentAvg, predictedAvg, hostType, dataType, valueName, minMaxValTuple, unit):
    print('Plotting:', valueName, '->',nameMapping[hostType[-3:]] + ' Client')
    fig, ax1 = plt.subplots(1, figsize=(16,12))
    predicted2sli = []
    predicted5sli = []
    simulatedBase = []
    simulated2sli = []
    simulated5sli = []
    for nodeSplit in nodeSplits:
        if 'baselineTestVCD_SSH' in baselineTestNames[0]: testName = 'baselineTestVCD_SSH' + str(nodeSplit[nodeTypes.index('hostSSH')]) + 'VIP' + str(nodeSplit[nodeTypes.index('hostVIP')]) + 'VID' + str(nodeSplit[nodeTypes.index('hostVID')]) + 'LVD' + str(nodeSplit[nodeTypes.index('hostLVD')]) + 'FDO' + str(nodeSplit[nodeTypes.index('hostFDO')])
        else: testName = baselineTestNames[0]
        # print(testName)
        simulatedBase.append(experimentAvg[testName][hostType])
    for testName in C2sliTestNames:
        simulated2sli.append(experimentAvg[testName][hostType])
        predicted2sli.append(predictedAvg[testName][hostType])
    for testName in C5sliTestNames:
        simulated5sli.append(experimentAvg[testName][hostType])
        predicted5sli.append(predictedAvg[testName][hostType])
    # print(simulatedBase)
    ax1.plot(xAxisValues, simulatedBase, label='Simulated Baseline', marker='o', ls='', color='red')
    ax1.plot(xAxisValues, simulated2sli, label='Simulated 2 Slices', marker='o', ls='', color='green')
    ax1.plot(xAxisValues, simulated5sli, label='Simulated 5 Slices', marker='o', ls='', color='blue')
    ax1.plot(xAxisValues, predicted2sli, label='Predicted 2 Slices', marker='P', ls='', color='green')
    ax1.plot(xAxisValues, predicted5sli, label='Predicted 5 Slices', marker='P', ls='', color='blue')
    if minMaxValTuple != (0,0): ax1.set_ylim(minMaxValTuple)
    ax1.set_ylabel(valueName + ' ' + unit)
    ax1.set_xlabel('Test Identifier')
    plt.xticks(rotation=90)
    plt.legend()
    ax1.legend(bbox_to_anchor=(0.4, -0.45))
    plt.grid(True)
    outPath = 'compPlots/'+exportName+'/'+dataType+'_'+hostType+'.png'
    fig.savefig(outPath, dpi=100, bbox_inches='tight')
    plt.close('all')

    fig, ax1 = partialCDFBegin(1)
    partialCDFPlotData(fig, ax1, simulated2sli, '2 Slices Simulations', '-o', 'green')
    partialCDFPlotData(fig, ax1, predicted2sli, '2 Slices Prediction', '-.P', 'green')
    partialCDFPlotData(fig, ax1, simulatedBase, 'Baseline', '-o', 'red')
    partialCDFEndPNG(fig, ax1, nameMapping[hostType[-3:]] + ' Client', valueName + ' ' + unit, 'compPlots/'+exportName+'/2Slices_' + dataType + 'CdfSimPredBase_'+hostType+'.png')

    fig, ax1 = partialCDFBegin(1)
    partialCDFPlotData(fig, ax1, simulated5sli, '5 Slices Simulations', '-o', 'green')
    partialCDFPlotData(fig, ax1, predicted5sli, '5 Slices Prediction', '-.P', 'green')
    partialCDFPlotData(fig, ax1, simulatedBase, 'Baseline', '-o', 'red')
    partialCDFEndPNG(fig, ax1, nameMapping[hostType[-3:]] + ' Client', valueName + ' ' + unit, 'compPlots/'+exportName+'/5Slices_' + dataType + 'CdfSimPredBase_'+hostType+'.png')

    fig, ax1 = partialCDFBegin(1)
    partialCDFPlotData(fig, ax1, [x - y for x,y in zip(simulated2sli,predicted2sli)], '2 Slices', '-o', 'green')
    partialCDFPlotData(fig, ax1, [x - y for x,y in zip(simulated5sli,predicted5sli)], '5 Slices', '-o', 'blue')
    partialCDFEndPNG(fig, ax1, nameMapping[hostType[-3:]] + ' Client', valueName + ' Difference to Prediction ' + unit, 'compPlots/'+exportName+'/' + dataType + 'DiffCdfPrediction_'+hostType+'.png')
    fig, ax1 = partialCDFBegin(1)
    partialCDFPlotData(fig, ax1, [x - y for x,y in zip(simulated2sli,simulatedBase)], '2 Slices', '-o', 'green')
    partialCDFPlotData(fig, ax1, [x - y for x,y in zip(simulated5sli,simulatedBase)], '5 Slices', '-o', 'blue')
    partialCDFEndPNG(fig, ax1, nameMapping[hostType[-3:]] + ' Client', valueName + ' Difference to Baseline ' + unit, 'compPlots/'+exportName+'/' + dataType + 'DiffCdfBase_'+hostType+'.png')

hostTypeOffsetMultiplier = {'hostVID' : -2.5,
                            'hostLVD' : -1.5,
                            'hostFDO' : -0.5,
                            'hostSSH' : 0.5,
                            'hostVIP' : 1.5,
                            'overall' : 2.5}

def plotMeanDataTypeClientAll(baselineTestNames, C2sliTestNames, C5sliTestNames, C2sliAlphas, C5sliAlphas, nodeTypes, nodeSplits, exportName, xAxisValues, experimentAvg, predictedAvg, dataType, valueName, minMaxValTuple, unit):
    print('Plotting:', valueName, '-> All Clients')
    itList = [x for x in nodeTypes]
    itList.append('overall')
    fig, ax1 = partialCDFBegin(1)
    for hostType in itList:
        simulatedBase = []
        for nodeSplit in nodeSplits:
            if 'baselineTestVCD_SSH' in baselineTestNames[0]: testName = 'baselineTestVCD_SSH' + str(nodeSplit[nodeTypes.index('hostSSH')]) + 'VIP' + str(nodeSplit[nodeTypes.index('hostVIP')]) + 'VID' + str(nodeSplit[nodeTypes.index('hostVID')]) + 'LVD' + str(nodeSplit[nodeTypes.index('hostLVD')]) + 'FDO' + str(nodeSplit[nodeTypes.index('hostFDO')])
            else: testName = baselineTestNames[0]
            simulatedBase.append(experimentAvg[testName][hostType])
        partialCDFPlotData(fig, ax1, simulatedBase, nameMapping[hostType[-3:]], '-' + markerMapping[hostType[-3:]], colorMapping[hostType[-3:]])
    partialCDFEndPNG(fig, ax1, '', valueName + ' ' + unit, 'compPlots/'+exportName+'/Baseline_' + dataType + 'Cdf_All.png')
    partialCDFEnd(fig, ax1, '', valueName + ' ' + unit, 'compPlots/'+exportName+'/pdf/Baseline_' + dataType + 'Cdf_All.pdf')

    fig, ax1 = partialCDFBegin(1)
    for hostType in itList:
        simulated2sli = []
        for testName in C2sliTestNames:
            simulated2sli.append(experimentAvg[testName][hostType])
        partialCDFPlotData(fig, ax1, simulated2sli, nameMapping[hostType[-3:]], '-' + markerMapping[hostType[-3:]], colorMapping[hostType[-3:]])
    partialCDFEndPNG(fig, ax1, '', valueName + ' ' + unit, 'compPlots/'+exportName+'/2Slices_' + dataType + 'Cdf_All.png')
    partialCDFEnd(fig, ax1, '', valueName + ' ' + unit, 'compPlots/'+exportName+'/pdf/2Slices_' + dataType + 'Cdf_All.pdf')

    fig, ax1 = partialCDFBegin(1)
    for hostType in itList:
        simulated5sli = []
        for testName in C5sliTestNames:
            if experimentAvg[testName][hostType] > 0: simulated5sli.append(experimentAvg[testName][hostType])
        partialCDFPlotData(fig, ax1, simulated5sli, nameMapping[hostType[-3:]], '-' + markerMapping[hostType[-3:]], colorMapping[hostType[-3:]])
    partialCDFEndPNG(fig, ax1, '', valueName + ' ' + unit, 'compPlots/'+exportName+'/5Slices_' + dataType + 'Cdf_All.png')
    partialCDFEnd(fig, ax1, '', valueName + ' ' + unit, 'compPlots/'+exportName+'/pdf/5Slices_' + dataType + 'Cdf_All.pdf')

    fig, ax1 = partialCDFBegin(1)
    for hostType in itList:
        simulatedBase = []
        simulated2sli = []
        for testName in C2sliTestNames:
            simulated2sli.append(experimentAvg[testName][hostType])
        for nodeSplit in nodeSplits:
            if 'baselineTestVCD_SSH' in baselineTestNames[0]: testName = 'baselineTestVCD_SSH' + str(nodeSplit[nodeTypes.index('hostSSH')]) + 'VIP' + str(nodeSplit[nodeTypes.index('hostVIP')]) + 'VID' + str(nodeSplit[nodeTypes.index('hostVID')]) + 'LVD' + str(nodeSplit[nodeTypes.index('hostLVD')]) + 'FDO' + str(nodeSplit[nodeTypes.index('hostFDO')])
            else: testName = baselineTestNames[0]
            simulatedBase.append(experimentAvg[testName][hostType])
        ax1.set_xlim(minMaxValTuple)
        partialCDFPlotData(fig, ax1, [x - y for x,y in zip(simulated2sli,simulatedBase)], nameMapping[hostType[-3:]], '-' + markerMapping[hostType[-3:]], colorMapping[hostType[-3:]])
    partialCDFEndPNG(fig, ax1, '', valueName + ' Difference to Baseline ' + unit, 'compPlots/'+exportName+'/2Slices_' + dataType + 'DiffCdfBase_All.png')
    partialCDFEnd(fig, ax1, '', valueName + ' Difference to Baseline ' + unit, 'compPlots/'+exportName+'/pdf/2Slices_' + dataType + 'DiffCdfBase_All.pdf')

    barWidth = 0.1

    fig, ax1 = partialCDFBegin(1)
    for hostType in itList:
        simulatedBase = []
        simulated2sli = []
        for testName in C2sliTestNames:
            simulated2sli.append(experimentAvg[testName][hostType])
        for nodeSplit in nodeSplits:
            if 'baselineTestVCD_SSH' in baselineTestNames[0]: testName = 'baselineTestVCD_SSH' + str(nodeSplit[nodeTypes.index('hostSSH')]) + 'VIP' + str(nodeSplit[nodeTypes.index('hostVIP')]) + 'VID' + str(nodeSplit[nodeTypes.index('hostVID')]) + 'LVD' + str(nodeSplit[nodeTypes.index('hostLVD')]) + 'FDO' + str(nodeSplit[nodeTypes.index('hostFDO')])
            else: testName = baselineTestNames[0]
            simulatedBase.append(experimentAvg[testName][hostType])
        ax1.bar(np.arange(len(xAxisValues)) + barWidth*hostTypeOffsetMultiplier[hostType], [x - y for x,y in zip(simulated2sli,simulatedBase)], barWidth, label=nameMapping[hostType[-3:]], color=colorMapping[hostType[-3:]])
    ax1.set_ylabel(valueName + ' Difference to Baseline ' + unit)
    ax1.set_xlabel('\u03B1')
    ax1.set_xticks(np.arange(len(xAxisValues)))
    ax1.set_xticklabels([x.split('; \u03B1 = ')[1] for x in xAxisValues])
    plt.title('')
    plt.legend()
    # ax1.legend(bbox_to_anchor=(0.4, -0.1))
    plt.grid(True, axis='y')
    outPath = 'compPlots/'+exportName+'/2Slices_' + dataType + 'DiffBarBase_All.png'
    fig.savefig(outPath, dpi=100, bbox_inches='tight')
    outPath = 'compPlots/'+exportName+'/pdf/2Slices_' + dataType + 'DiffBarBase_All.pdf'
    fig.savefig(outPath, dpi=100, bbox_inches='tight')
    plt.close('all')

    fig, ax1 = partialCDFBegin(1)
    for hostType in itList:
        simulatedBase = []
        simulated5sli = []
        for testName in C5sliTestNames:
            simulated5sli.append(experimentAvg[testName][hostType])
        for nodeSplit in nodeSplits:
            if 'baselineTestVCD_SSH' in baselineTestNames[0]: testName = 'baselineTestVCD_SSH' + str(nodeSplit[nodeTypes.index('hostSSH')]) + 'VIP' + str(nodeSplit[nodeTypes.index('hostVIP')]) + 'VID' + str(nodeSplit[nodeTypes.index('hostVID')]) + 'LVD' + str(nodeSplit[nodeTypes.index('hostLVD')]) + 'FDO' + str(nodeSplit[nodeTypes.index('hostFDO')])
            else: testName = baselineTestNames[0]
            simulatedBase.append(experimentAvg[testName][hostType])
        ax1.set_xlim(minMaxValTuple)
        partialCDFPlotData(fig, ax1, [x - y for x,y in zip(simulated5sli,simulatedBase) if x > 0 and y > 0], nameMapping[hostType[-3:]], '-' + markerMapping[hostType[-3:]], colorMapping[hostType[-3:]])
    partialCDFEndPNG(fig, ax1, '', valueName + ' Difference to Baseline ' + unit, 'compPlots/'+exportName+'/5Slices_' + dataType + 'DiffCdfBase_All.png')
    partialCDFEnd(fig, ax1, '', valueName + ' Difference to Baseline ' + unit, 'compPlots/'+exportName+'/pdf/5Slices_' + dataType + 'DiffCdfBase_All.pdf')

    fig, ax1 = partialCDFBegin(1)
    for hostType in itList:
        simulatedBase = []
        simulated5sli = []
        for testName in C5sliTestNames:
            simulated5sli.append(experimentAvg[testName][hostType])
        for nodeSplit in nodeSplits:
            if 'baselineTestVCD_SSH' in baselineTestNames[0]: testName = 'baselineTestVCD_SSH' + str(nodeSplit[nodeTypes.index('hostSSH')]) + 'VIP' + str(nodeSplit[nodeTypes.index('hostVIP')]) + 'VID' + str(nodeSplit[nodeTypes.index('hostVID')]) + 'LVD' + str(nodeSplit[nodeTypes.index('hostLVD')]) + 'FDO' + str(nodeSplit[nodeTypes.index('hostFDO')])
            else: testName = baselineTestNames[0]
            simulatedBase.append(experimentAvg[testName][hostType])
        ax1.bar(np.arange(len(xAxisValues)) + barWidth*hostTypeOffsetMultiplier[hostType], [x - y for x,y in zip(simulated5sli,simulatedBase)], barWidth, label=nameMapping[hostType[-3:]], color=colorMapping[hostType[-3:]])
    ax1.set_ylabel(valueName + ' Difference to Baseline ' + unit)
    ax1.set_xlabel('\u03B1')
    ax1.set_xticks(np.arange(len(xAxisValues)))
    ax1.set_xticklabels([x.split('; \u03B1 = ')[1] for x in xAxisValues])
    plt.title('')
    plt.legend()
    # ax1.legend(bbox_to_anchor=(0.4, -0.1))
    plt.grid(True, axis='y')
    outPath = 'compPlots/'+exportName+'/5Slices_' + dataType + 'DiffBarBase_All.png'
    fig.savefig(outPath, dpi=100, bbox_inches='tight')
    outPath = 'compPlots/'+exportName+'/pdf/5Slices_' + dataType + 'DiffBarBase_All.pdf'
    fig.savefig(outPath, dpi=100, bbox_inches='tight')
    plt.close('all')

    if dataType == 'fairness': itList = ['overall']
    fig, ax1 = partialCDFBegin(1)
    for hostType in itList:
        predicted2sli = []
        simulated2sli = []
        for testName in C2sliTestNames:
            simulated2sli.append(experimentAvg[testName][hostType])
            predicted2sli.append(predictedAvg[testName][hostType])
        if dataType == 'delay': ax1.set_xlim(-100,605)
        partialCDFPlotData(fig, ax1, [x - y for x,y in zip(simulated2sli,predicted2sli)], nameMapping[hostType[-3:]], '-' + markerMapping[hostType[-3:]], colorMapping[hostType[-3:]])
    partialCDFEndPNG(fig, ax1, '', valueName + ' Difference to Prediction ' + unit, 'compPlots/'+exportName+'/2Slices_' + dataType + 'DiffCdfPrediction_All.png')
    partialCDFEnd(fig, ax1, '', valueName + ' Difference to Prediction ' + unit, 'compPlots/'+exportName+'/pdf/2Slices_' + dataType + 'DiffCdfPrediction_All.pdf')

    # if dataType == 'fairness': itList = ['overall']
    fig, ax1 = partialCDFBegin(1)
    for hostType in itList:
        predicted2sli = []
        simulated2sli = []
        for testName in C2sliTestNames:
            simulated2sli.append(experimentAvg[testName][hostType])
            predicted2sli.append(predictedAvg[testName][hostType])
        if dataType == 'delay': ax1.set_ylim(-100,600)
        ax1.bar(np.arange(len(xAxisValues)) + barWidth*hostTypeOffsetMultiplier[hostType], [x - y for x,y in zip(simulated2sli,predicted2sli)], barWidth, label=nameMapping[hostType[-3:]], color=colorMapping[hostType[-3:]])
    ax1.set_ylabel(valueName + ' Difference to Prediction ' + unit)
    ax1.set_xlabel('\u03B1')
    ax1.set_xticks(np.arange(len(xAxisValues)))
    ax1.set_xticklabels([x.split('; \u03B1 = ')[1] for x in xAxisValues])
    plt.title('')
    plt.legend()
    # ax1.legend(bbox_to_anchor=(0.4, -0.1))
    plt.grid(True, axis='y')
    outPath = 'compPlots/'+exportName+'/2Slices_' + dataType + 'DiffBarPrediction_All.png'
    fig.savefig(outPath, dpi=100, bbox_inches='tight')
    outPath = 'compPlots/'+exportName+'/pdf/2Slices_' + dataType + 'DiffBarPrediction_All.pdf'
    fig.savefig(outPath, dpi=100, bbox_inches='tight')
    plt.close('all')
    

    fig, ax1 = partialCDFBegin(1)
    for hostType in itList:
        predicted5sli = []
        simulated5sli = []
        for testName in C5sliTestNames:
            simulated5sli.append(experimentAvg[testName][hostType])
            predicted5sli.append(predictedAvg[testName][hostType])
        if dataType == 'delay': ax1.set_xlim(-100,600)
        partialCDFPlotData(fig, ax1, [x - y for x,y in zip(simulated5sli,predicted5sli) if x > 0 and y > 0], nameMapping[hostType[-3:]], '-' + markerMapping[hostType[-3:]], colorMapping[hostType[-3:]])
    partialCDFEndPNG(fig, ax1, '', valueName + ' Difference to Prediction ' + unit, 'compPlots/'+exportName+'/5Slices_' + dataType + 'DiffCdfPrediction_All.png')
    partialCDFEnd(fig, ax1, '', valueName + ' Difference to Prediction ' + unit, 'compPlots/'+exportName+'/pdf/5Slices_' + dataType + 'DiffCdfPrediction_All.pdf')

    fig, ax1 = partialCDFBegin(1)
    for hostType in itList:
        predicted5sli = []
        simulated5sli = []
        for testName in C5sliTestNames:
            simulated5sli.append(experimentAvg[testName][hostType])
            predicted5sli.append(predictedAvg[testName][hostType])
        if dataType == 'delay': ax1.set_ylim(-100,605)
        ax1.bar(np.arange(len(xAxisValues)) + barWidth*hostTypeOffsetMultiplier[hostType], [x - y for x,y in zip(simulated5sli,predicted5sli)], barWidth, label=nameMapping[hostType[-3:]], color=colorMapping[hostType[-3:]])
    ax1.set_ylabel(valueName + ' Difference to Prediction ' + unit)
    ax1.set_xlabel('\u03B1')
    ax1.set_xticks(np.arange(len(xAxisValues)))
    ax1.set_xticklabels([x.split('; \u03B1 = ')[1] for x in xAxisValues])
    plt.title('')
    plt.legend()
    # ax1.legend(bbox_to_anchor=(0.4, -0.1))
    plt.grid(True, axis='y')
    outPath = 'compPlots/'+exportName+'/5Slices_' + dataType + 'DiffBarPrediction_All.png'
    fig.savefig(outPath, dpi=100, bbox_inches='tight')
    outPath = 'compPlots/'+exportName+'/pdf/5Slices_' + dataType + 'DiffBarPrediction_All.pdf'
    fig.savefig(outPath, dpi=100, bbox_inches='tight')
    plt.close('all')
        # predicted2sli = []
        # predicted5sli = []
        # simulated2sli = []
        # simulated5sli = []
    #     for testName in C2sliTestNames:
    #         simulated2sli.append(experimentAvg[testName][hostType])
    #         predicted2sli.append(predictedAvg[testName][hostType])
    #     for testName in C5sliTestNames:
    #         simulated5sli.append(experimentAvg[testName][hostType])
    #         predicted5sli.append(predictedAvg[testName][hostType])
    # fig, ax1 = partialCDFBegin(1)
    # partialCDFPlotData(fig, ax1, simulated5sli, '5 Slices Simulations', '-o', 'green')
    # partialCDFPlotData(fig, ax1, predicted5sli, '5 Slices Prediction', '-.P', 'green')
    # partialCDFPlotData(fig, ax1, simulatedBase, 'Baseline', '-o', 'red')
    # partialCDFEndPNG(fig, ax1, nameMapping[hostType[-3:]] + ' Client', valueName + ' ' + unit, 'compPlots/'+exportName+'/5Slices_' + dataType + 'CdfSimPredBase_'+hostType+'.png')

    # fig, ax1 = partialCDFBegin(1)
    # partialCDFPlotData(fig, ax1, [x - y for x,y in zip(simulated2sli,predicted2sli)], '2 Slices', '-o', 'green')
    # partialCDFPlotData(fig, ax1, [x - y for x,y in zip(simulated5sli,predicted5sli)], '5 Slices', '-o', 'blue')
    # partialCDFEndPNG(fig, ax1, nameMapping[hostType[-3:]] + ' Client', valueName + ' Difference to Prediction ' + unit, 'compPlots/'+exportName+'/' + dataType + 'DiffCdfPrediction_'+hostType+'.png')
    # fig, ax1 = partialCDFBegin(1)
    # partialCDFPlotData(fig, ax1, [x - y for x,y in zip(simulated2sli,simulatedBase)], '2 Slices', '-o', 'green')
    # partialCDFPlotData(fig, ax1, [x - y for x,y in zip(simulated5sli,simulatedBase)], '5 Slices', '-o', 'blue')
    # partialCDFEndPNG(fig, ax1, nameMapping[hostType[-3:]] + ' Client', valueName + ' Difference to Baseline ' + unit, 'compPlots/'+exportName+'/' + dataType + 'DiffCdfBase_'+hostType+'.png')

def plotComparisons(baselineTestNames, C2sliTestNames, C5sliTestNames, C2sliAlphas, C5sliAlphas, nodeTypes, nodeSplits, exportName, importName2sli, importName5sli):
    experimentMinMos = {}
    experimentMaxMos = {}
    experimentAvgMos = {}
    experimentDelays = {}
    experimentFairness = {}
    for testName in baselineTestNames:
        minMos, maxMos, avgMos, delays, fairness = importResCompExports(testName)
        experimentMinMos[testName] = minMos
        experimentMaxMos[testName] = maxMos
        experimentAvgMos[testName] = avgMos
        experimentDelays[testName] = delays
        experimentFairness[testName] = fairness

    for testName in C2sliTestNames:
        minMos, maxMos, avgMos, delays, fairness = importResCompExports(testName)
        experimentMinMos[testName] = minMos
        experimentMaxMos[testName] = maxMos
        experimentAvgMos[testName] = avgMos
        experimentDelays[testName] = delays
        experimentFairness[testName] = fairness

    for testName in C5sliTestNames:
        minMos, maxMos, avgMos, delays, fairness = importResCompExports(testName)
        experimentMinMos[testName] = minMos
        experimentMaxMos[testName] = maxMos
        experimentAvgMos[testName] = avgMos
        experimentDelays[testName] = delays
        experimentFairness[testName] = fairness
    
    predictedMinMos = {}
    predictedMaxMos = {}
    predictedAvgMos = {}
    predictedDelays = {}
    predictedFairness = {}
                
    for i in range(len(C5sliTestNames)):
        testName = C5sliTestNames[i]
        alpha = C5sliAlphas[i]
        if importName5sli == '5sliTestVariousCliNums[5-20-50-75-100]Fairness1alphas[0.0, 0.5, 1.0]': minMos, maxMos, avgMos, delays, fairness = import5sliPredictions(importName5sli+testName.split('_')[-2]+testName.split('_')[-1], testName, alpha)
        else: minMos, maxMos, avgMos, delays, fairness = import5sliPredictions(importName5sli, testName, alpha)
        predictedMinMos[testName] = minMos
        predictedMaxMos[testName] = maxMos
        predictedAvgMos[testName] = avgMos
        predictedDelays[testName] = delays
        predictedFairness[testName] = fairness

    for i in range(len(C2sliTestNames)):
        testName = C2sliTestNames[i]
        alpha = C2sliAlphas[i]
        minMos, maxMos, avgMos, delays, fairness = import2sliPredictions(importName2sli, testName, alpha, i)
        predictedMinMos[testName] = minMos
        predictedMaxMos[testName] = maxMos
        predictedAvgMos[testName] = avgMos
        predictedDelays[testName] = delays
        predictedFairness[testName] = fairness

    testNumbers = []
    testNumbersAlpha = []
    prettyTestNames = []
    prettyTestNamesAlpha = []

    for i in range(len(C2sliAlphas)):
        testNumbers.append('C' + str(i+1))
        testNumbersAlpha.append('C' + str(i+1) + '; \u03B1 = ' + str(float(C2sliAlphas[i])))
        prettyTestNames.append('Config ' + str(i+1))
        prettyTestNamesAlpha.append('Config ' + str(i+1) + '; \u03B1 = ' + str(float(C2sliAlphas[i])))

    if not os.path.exists('compPlots/'+exportName+'/'):
        os.makedirs('compPlots/'+exportName+'/')
    if not os.path.exists('compPlots/'+exportName+'/pdf/'):
        os.makedirs('compPlots/'+exportName+'/pdf/')

    plotMeanDataTypeClientType(baselineTestNames, C2sliTestNames, C5sliTestNames, C2sliAlphas, C5sliAlphas, nodeTypes, nodeSplits, exportName, testNumbersAlpha, experimentAvgMos, predictedAvgMos, 'overall', 'meanUtility', 'Mean Utility', (0.95,5.05), '')
    plotMeanDataTypeClientType(baselineTestNames, C2sliTestNames, C5sliTestNames, C2sliAlphas, C5sliAlphas, nodeTypes, nodeSplits, exportName, testNumbersAlpha, experimentDelays, predictedDelays, 'overall', 'delay', 'Mean Delay', (0,0), '[ms]')
    plotMeanDataTypeClientType(baselineTestNames, C2sliTestNames, C5sliTestNames, C2sliAlphas, C5sliAlphas, nodeTypes, nodeSplits, exportName, testNumbersAlpha, experimentFairness, predictedFairness, 'overall', 'fairness', 'Fairness', (-0.01,1.01), '')
    for hType in nodeTypes:
        plotMeanDataTypeClientType(baselineTestNames, C2sliTestNames, C5sliTestNames, C2sliAlphas, C5sliAlphas, nodeTypes, nodeSplits, exportName, testNumbersAlpha, experimentAvgMos, predictedAvgMos, hType, 'meanUtility', 'Mean Utility', (0.95,5.05), '')
        plotMeanDataTypeClientType(baselineTestNames, C2sliTestNames, C5sliTestNames, C2sliAlphas, C5sliAlphas, nodeTypes, nodeSplits, exportName, testNumbersAlpha, experimentDelays, predictedDelays, hType, 'delay', 'Mean Delay', (0,0), '[ms]')
    plotMeanDataTypeClientAll(baselineTestNames, C2sliTestNames, C5sliTestNames, C2sliAlphas, C5sliAlphas, nodeTypes, nodeSplits, exportName, testNumbersAlpha, experimentAvgMos, predictedAvgMos, 'meanUtility', 'Mean Utility', (-3,4), '')
    plotMeanDataTypeClientAll(baselineTestNames, C2sliTestNames, C5sliTestNames, C2sliAlphas, C5sliAlphas, nodeTypes, nodeSplits, exportName, testNumbersAlpha, experimentDelays, predictedDelays, 'delay', 'Mean Delay', (-500,700), '[ms]')
    plotMeanDataTypeClientAll(baselineTestNames, C2sliTestNames, C5sliTestNames, C2sliAlphas, C5sliAlphas, nodeTypes, nodeSplits, exportName, testNumbersAlpha, experimentFairness, predictedFairness, 'fairness', 'Fairness', (-0.5,0.5), '')




######## plotComparisons(testNamesBaseline, testNames2sli, testNames5sli, alphas2or5sli, alphas2or5sli, ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], nodeSplits, 'baseline_2sliLVD-BWS_5sli_comparisons', '2sliLVD_BWSTestVariousCliNums[5-20-50-75-100]Fairness1alphas[0.0, 0.5, 1.0]', '5sliTestVariousCliNums[5-20-50-75-100]Fairness1alphas[0.0, 0.5, 1.0]')
# plotComparisons(testNamesBaseline, testNames2sli[:7], testNames5sli[:7], alphas2or5sli[:7], alphas2or5sli[:7], ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], nodeSplits[:7], 'baseline_2sliLVD-BWS_5sli_comparisons_small')

######## plotComparisons(['baselineTest'], ['baselineTestNS_2sli_LVD-BWS_AlgoTest_alpha00', 'baselineTestNS_2sli_LVD-BWS_AlgoTest_alpha05', 'baselineTestNS_2sli_LVD-BWS_AlgoTest_alpha10'], ['baselineTestNS_5sli_AlgoTest_alpha00', 'baselineTestNS_5sli_AlgoTest_alpha05', 'baselineTestNS_5sli_AlgoTest_alpha10'], [0.0, 0.5, 1.0], [0.0, 0.5, 1.0], ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [[50 for _ in range(5)] for _ in range(3)], 'baseline50cli_2sliLVD-BWS_5sli_comparisons', 'selectedConfigsRes/baselineTestNS_2sli_LVD-BWS_AlgoTest_alphas[0.0, 0.5, 1.0]', 'baselineTestNS_5sli_AlgoTest_alphas[0.0, 0.5, 1.0]')

def extractUltimateClientConfigs(algoResName, algoType, alphas, metrics, minMaxes, configName):
    chosenAlphaList = []
    chosenMetric = []
    chosenMinMax = []
    chosenCliConfigs = []
    chosenAssignments = []
    chosenObjFunc = []
    chosenMinMos = []
    chosenMaxMos = []
    chosenAvgMos = []
    chosenMosFairness = []
    chosenMeanBandSlice = []
    chosenEstimDelaySlice = []
    chosenEstMosSlice = []

    prettyTestNames = []
    
    for metric in metrics:
        for minMax in minMaxes:
            file_to_read = '../../algorithm/selectedConfigsRes/'+algoResName + algoType + 'alphas' + str(alphas)+metric+minMax+'.csv'
            with open(file_to_read, mode='r') as readFile:
                csv_reader = csv.reader(readFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
                line_count = 0
                for row in csv_reader:
                    if line_count == 0:
                        chosenAlphaList.extend(row)
                    elif line_count == 1:
                        chosenMetric.extend(row)
                    elif line_count == 2:
                        chosenMinMax.extend(row)
                    elif line_count == 3:
                        chosenCliConfigs.extend([eval(x) for x in row])
                    elif line_count == 4:
                        chosenAssignments.extend([eval(x) for x in row])
                    elif line_count == 5:
                        chosenObjFunc.extend(row)
                    elif line_count == 6:
                        chosenMinMos.extend([eval(x) for x in row])
                    elif line_count == 7:
                        chosenMaxMos.extend([eval(x) for x in row])
                    elif line_count == 8:
                        chosenAvgMos.extend(row)
                    elif line_count == 9:
                        chosenMosFairness.extend(row)
                    elif line_count == 10:
                        chosenMeanBandSlice.extend([eval(x) for x in row])
                    elif line_count == 11:
                        chosenEstimDelaySlice.extend([eval(x) for x in row])
                    elif line_count == 12:
                        chosenEstMosSlice.extend([eval(x) for x in row])
                    line_count += 1
    cliConfig = []
    for i in range(len(chosenAlphaList)):
        prettyTestNames.append(str(float(chosenAlphaList[i])/10) + '-' + chosenMetric[i]+'-'+chosenMinMax[i])
        tempCliConfig = {}
        for sli in chosenCliConfigs[i]:
            for cli in chosenCliConfigs[i][sli]:
                tempCliConfig[cli] = chosenCliConfigs[i][sli][cli]
        cliConfig.append(tempCliConfig)
        print(chosenAlphaList[i], cliConfig[i])
    
    if not os.path.exists('ultimateConfigs/'):
        os.makedirs('ultimateConfigs/')
    with open('ultimateConfigs/' + configName + 'alphas' + str(alphas) + '.csv', mode='w') as writeFile:
            fw = csv.writer(writeFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
            fw.writerow(chosenAlphaList)
            fw.writerow(cliConfig)

# extractUltimateClientConfigs('5sliTestVariousCliNums[5-20-50-75-100]', 'Fairness1', [0.0, 0.5, 1.0], ['fairness', 'min', 'mean'], ['max', 'min'], 'cliNums[5-20-50-75-100]')

# getMeanDataTypeAppClass('baselineTestNS_5sli_AlgoTest1', 250, ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [50 for x in range(5)], 'Mos', 'mos', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], {'sliceSSH' : {'hostSSH' : 50}, 'sliceVIP' : {'hostVIP' : 50}, 'sliceVID' : {'hostVID' : 50}, 'sliceLVD' : {'hostLVD' : 50}, 'sliceFDO' : {'hostFDO' : 50}})
# getMeanDataTypeAppClass('baselineTestNS_5sli_AlgoTest2', 250, ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [50 for x in range(5)], 'Mos', 'mos', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], {'sliceSSH' : {'hostSSH' : 50}, 'sliceVIP' : {'hostVIP' : 50}, 'sliceVID' : {'hostVID' : 50}, 'sliceLVD' : {'hostLVD' : 50}, 'sliceFDO' : {'hostFDO' : 50}})
# getMeanDataTypeAppClass('baselineTestNS_2sli_LVD-DES_AlgoTest1', 250, ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [50 for x in range(5)], 'Mos', 'mos', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], {'sliceDel' : {'hostSSH' : 50, 'hostLVD' : 50, 'hostVIP' : 50}, 'sliceBand' : {'hostVID' : 50, 'hostFDO' : 50}})
# getMeanDataTypeAppClass('baselineTestNS_2sli_LVD-BWS_AlgoTest1', 250, ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [50 for x in range(5)], 'Mos', 'mos', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], {'sliceDel' : {'hostSSH' : 50, 'hostVIP' : 50}, 'sliceBand' : {'hostVID' : 50, 'hostLVD' : 50, 'hostFDO' : 50}})

# getMeanDataTypeAppClass('baselineTestNS_5sli_AlgoTest3', 250, ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [50 for x in range(5)], 'Mos', 'mos', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], {'sliceSSH' : {'hostSSH' : 50}, 'sliceVIP' : {'hostVIP' : 50}, 'sliceVID' : {'hostVID' : 50}, 'sliceLVD' : {'hostLVD' : 50}, 'sliceFDO' : {'hostFDO' : 50}})
# getMeanDataTypeAppClass('baselineTest', 250, ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [50 for x in range(5)], 'Mos', 'mos', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], {'sliceSSH' : {'hostSSH' : 50, 'hostVIP' : 50, 'hostVID' : 50, 'hostLVD' : 50, 'hostFDO' : 50}})
# getMeanDataTypeAppClass('baselineTestNS_2sli_LVD-DES_AlgoTest3', 250, ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [50 for x in range(5)], 'Mos', 'mos', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], {'sliceDel' : {'hostSSH' : 50, 'hostLVD' : 50, 'hostVIP' : 50}, 'sliceBand' : {'hostVID' : 50, 'hostFDO' : 50}})
# getMeanDataTypeAppClass('baselineTestNS_2sli_LVD-BWS_AlgoTest3', 250, ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [50 for x in range(5)], 'Mos', 'mos', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], {'sliceDel' : {'hostSSH' : 50, 'hostVIP' : 50}, 'sliceBand' : {'hostVID' : 50, 'hostLVD' : 50, 'hostFDO' : 50}})

def prepConfigNameBaseline(overallTestName, cliConfig):
    configName = overallTestName + '_' 
    for cli in cliConfig:
        configName += cli[-3:]+str(cliConfig[cli])

    if not os.path.exists('genConfigNames/'):
        os.makedirs('genConfigNames/')
    with open('genConfigNames/configNames.txt', mode='a') as writeFile:
        writeFile.write(configName+'\n')

    return configName


def prepareConfigBaselineINI(overallTestName, cliConfig):
    configString = '[Config ' + prepConfigNameBaseline(overallTestName, cliConfig)
    configString += ']\ndescription = \"Automatically generated config\"\n'
    configString += 'extends = baselineTest_base\n\n'
    for cli in cliConfig:
        configString += '*.n' + cli[-3:] + ' = ' + str(cliConfig[cli]) + '\n'
    configString += '\n'
    return configString

def prepBaselineTestConfig(configName, alphas, testName):
    chosenAlphaList = []
    cliConfig = []
    file_to_read = 'ultimateConfigs/' + configName + 'alphas' + str(alphas) + '.csv'
    print(file_to_read)
    with open(file_to_read, mode='r') as readFile:
        csv_reader = csv.reader(readFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                chosenAlphaList.extend(row)
            elif line_count == 1:
                cliConfig.extend(row)
            line_count += 1
    tempCliConfig = [eval(x) for x in list(dict.fromkeys(cliConfig))]
    resConfig = ''
    for config in tempCliConfig:
        resConfig += prepareConfigBaselineINI(testName, config)
        # print('./runSimCampaign.sh -i baselineTest.ini -c', prepConfigNameBaseline(testName, config), '-t 1')
        # print(config)
        hostList = ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP']
        print('extractAll(\'' + prepConfigNameBaseline(testName, config) + '\',', str(hostList) + ',', str([config[x] for x in hostList]) + ', 1)')
        # print('./export_results_individual_NS.sh -f 0 -l 0 -r 1 -s', prepConfigNameBaseline(testName, config), '-o ../../../analysis/' + prepConfigNameBaseline(testName, config), '-t', prepConfigNameBaseline(testName, config), '-d', prepConfigNameBaseline(testName, config))
    
    # if not os.path.exists('simConfigStubs/'):
    #     os.makedirs('simConfigStubs/')
    # with open('simConfigStubs/' + testName + '.txt', mode='w') as writeFile:
    #     writeFile.write(resConfig)

# prepBaselineTestConfig('cliNums[5-20-50-75-100]', [0.0, 0.5, 1.0], 'baselineTestVCD')