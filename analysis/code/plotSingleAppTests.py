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

def makeFullScenarioName(testName, numCLI, nodeTypes, nodeSplit):
    scenName = str(testName) + '_' + str(numCLI)
    for nodeType,numNodesType in zip(nodeTypes, nodeSplit):
        scenName += '_' + nodeType.replace('host','') + str(numNodesType)
    return scenName

def makeXaxisLabel(valueType):
    if 'mos' in valueType:
        return 'Average Mos Value'
    if valueType == 'endToEndDelay':
        return 'Average End-To-End Delay [s]'
    if valueType == 'packetLossRate':
        return 'Average Packet Loss Rate'
    if valueType == 'playoutLossRate':
        return 'Average Playout Loss Rate'
    if valueType == 'playoutDelay':
        return 'Average Playout Delay [s]'
    if valueType == 'averageDownloadThroughput':
        return 'Average Download Throughput [bps]'
    if valueType == 'downloadTime':
        return 'Average Download Time [s]'
    if valueType == 'DASHReceivedBytes':
        return 'Average Number of Bytes Received per Video Segment'
    if valueType == 'DASHBufferLength':
        return 'Average Video Buffer Length [s]'
    if valueType == 'numActiveSessions':
        return 'Average Number of Active Sessions per Client'
    if valueType == 'roundTripTime':
        return 'Average Round Trip Time [s]'
    if valueType == 'packetReceived':
        return 'Average Size of Received Packets [Bytes]'
    if valueType == 'packetSent':
        return 'Average Size of Sent Packets [Bytes]'
    if valueType == 'DASHliveDelay':
        return 'Average Delay to Live Video Edge [s]'

    return valueType

def plotDelayMeanValue(testName, numCLI, nodeTypes, nodeSplit, valueType):
    delays = []
    meanValues = []
    file_to_read = '../exports/extracted/' + valueType + '/' + makeFullScenarioName(testName, numCLI, nodeTypes, nodeSplit) + '.csv'
    with open(file_to_read, mode='r') as readFile:
        csv_reader = csv.reader(readFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                delays = row
            elif line_count == 1:
                meanValues = row
            line_count += 1 

    fig, ax1 = plt.subplots(1, figsize=(16,12))
    # print(meanValues)
    dela = [x for x, y in zip(delays, meanValues) if y >= 0]
    meanVal = [x for x in meanValues if x >= 0]
    ax1.plot(dela, meanVal, 'o-')
    
    plt.xlabel('Link Delay [ms]')
    plt.ylabel(makeXaxisLabel(valueType))
    prePath = '../exports/plots/' + makeFullScenarioName(testName, numCLI, nodeTypes, nodeSplit) + '/'
    if not os.path.exists(prePath):
        os.makedirs(prePath)
    outPath = prePath + valueType + '.pdf'
    fig.savefig(outPath, dpi=100, bbox_inches='tight')
    outPath2 = prePath + valueType + '.png'
    fig.savefig(outPath2, dpi=100, bbox_inches='tight', format='png')
    plt.close('all')

def plotDelayMeanTPsDirection(testName, numCLI, nodeTypes, nodeSplit, direction):
    delays = []
    meanValues = []
    file_to_read = '../exports/extracted/throughput' + direction[0] + '/' + makeFullScenarioName(testName, numCLI, nodeTypes, nodeSplit) + '.csv'
    with open(file_to_read, mode='r') as readFile:
        csv_reader = csv.reader(readFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                delays = row
            elif line_count == 1:
                meanValues = row
            line_count += 1 

    fig, ax1 = plt.subplots(1, figsize=(16,12))
    # print(meanValues)
    ax1.plot(delays, meanValues, 'o-')
    
    plt.xlabel('Link Delay [ms]')
    plt.ylabel('Mean ' + direction[0] + ' Throughput [kbps]')
    prePath = '../exports/plots/' + makeFullScenarioName(testName, numCLI, nodeTypes, nodeSplit) + '/'
    if not os.path.exists(prePath):
        os.makedirs(prePath)
    outPath = prePath + 'meanThroughput' + direction[0] + '.pdf'
    fig.savefig(outPath, dpi=100, bbox_inches='tight')
    outPath2 = prePath + 'meanThroughput' + direction[0] + '.png'
    fig.savefig(outPath2, dpi=100, bbox_inches='tight', format='png')
    plt.close('all')

def plotMeanTPMeanE2EDScatter(testName, sumNodes, nodeTypes, nodeSplit):
    meanTPs = []
    meanE2EDs = []
    file_to_read = '../exports/extracted/eachNodeMeanTPMeanE2ED/' + makeFullScenarioName(testName, sumNodes, nodeTypes, nodeSplit) + '.csv'
    with open(file_to_read, mode='r') as readFile:
        csv_reader = csv.reader(readFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                meanTPs = row
            elif line_count == 1:
                meanE2EDs = row
            line_count += 1 

    fig, ax1 = plt.subplots(1, figsize=(16,12))
    # print(meanValues)
    ax1.plot(meanTPs, meanE2EDs, 'o')
    
    plt.xlabel('Mean Client Throughput [kbps]')
    plt.ylabel('Mean Client End-To-End Delay [s]')
    prePath = '../exports/plots/' + makeFullScenarioName(testName, sumNodes, nodeTypes, nodeSplit) + '/'
    if not os.path.exists(prePath):
        os.makedirs(prePath)
    outPath = prePath + 'meanTPMeanE2EDScatter.pdf'
    fig.savefig(outPath, dpi=100, bbox_inches='tight')
    outPath2 = prePath + 'meanTPMeanE2EDScatter.png'
    fig.savefig(outPath2, dpi=100, bbox_inches='tight', format='png')
    plt.close('all')

def plotMeanTPMedianE2EDScatter(testName, sumNodes, nodeTypes, nodeSplit):
    meanTPs = []
    meanE2EDs = []
    file_to_read = '../exports/extracted/eachNodeMeanTPMedianE2ED/' + makeFullScenarioName(testName, sumNodes, nodeTypes, nodeSplit) + '.csv'
    with open(file_to_read, mode='r') as readFile:
        csv_reader = csv.reader(readFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                meanTPs = row
            elif line_count == 1:
                meanE2EDs = row
            line_count += 1 

    fig, ax1 = plt.subplots(1, figsize=(16,12))
    # print(meanValues)
    ax1.plot(meanTPs, meanE2EDs, 'o')
    
    plt.xlabel('Mean Client Throughput [kbps]')
    plt.ylabel('Median Client End-To-End Delay [s]')
    prePath = '../exports/plots/' + makeFullScenarioName(testName, sumNodes, nodeTypes, nodeSplit) + '/'
    if not os.path.exists(prePath):
        os.makedirs(prePath)
    outPath = prePath + 'mediTPMedianE2EDScatter.pdf'
    fig.savefig(outPath, dpi=100, bbox_inches='tight')
    outPath2 = prePath + 'meanTPMedianE2EDScatter.png'
    fig.savefig(outPath2, dpi=100, bbox_inches='tight', format='png')
    plt.close('all')

def plotMeanTPMaxE2EDScatter(testName, sumNodes, nodeTypes, nodeSplit):
    meanTPs = []
    meanE2EDs = []
    file_to_read = '../exports/extracted/eachNodeMeanTPMaxE2ED/' + makeFullScenarioName(testName, sumNodes, nodeTypes, nodeSplit) + '.csv'
    with open(file_to_read, mode='r') as readFile:
        csv_reader = csv.reader(readFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                meanTPs = row
            elif line_count == 1:
                meanE2EDs = row
            line_count += 1 

    fig, ax1 = plt.subplots(1, figsize=(16,12))
    # print(meanValues)
    ax1.plot(meanTPs, meanE2EDs, 'o')
    
    plt.xlabel('Mean Client Throughput [kbps]')
    plt.ylabel('Max Client End-To-End Delay [s]')
    prePath = '../exports/plots/' + makeFullScenarioName(testName, sumNodes, nodeTypes, nodeSplit) + '/'
    if not os.path.exists(prePath):
        os.makedirs(prePath)
    outPath = prePath + 'meanTPMaxE2EDScatter.pdf'
    fig.savefig(outPath, dpi=100, bbox_inches='tight')
    outPath2 = prePath + 'meanTPMaxE2EDScatter.png'
    fig.savefig(outPath2, dpi=100, bbox_inches='tight', format='png')
    plt.close('all')

def plotMeanTPXPercentileE2EDScatter(testName, sumNodes, nodeTypes, nodeSplit, percentile):
    meanTPs = []
    meanE2EDs = []
    file_to_read = '../exports/extracted/eachNodeMeanTP' + str(percentile) + 'percentileE2ED/' + makeFullScenarioName(testName, sumNodes, nodeTypes, nodeSplit) + '.csv'
    with open(file_to_read, mode='r') as readFile:
        csv_reader = csv.reader(readFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                meanTPs = row
            elif line_count == 1:
                meanE2EDs = row
            line_count += 1 

    fig, ax1 = plt.subplots(1, figsize=(16,12))
    # print(meanValues)
    ax1.plot(meanTPs, meanE2EDs, 'o')
    
    plt.xlabel('Mean Client Throughput [kbps]')
    plt.ylabel(str(percentile) + 'th-Percentile Client End-To-End Delay [s]')
    prePath = '../exports/plots/' + makeFullScenarioName(testName, sumNodes, nodeTypes, nodeSplit) + '/'
    if not os.path.exists(prePath):
        os.makedirs(prePath)
    outPath = prePath + 'meanTP' + str(percentile) + 'percentileE2EDScatter.pdf'
    fig.savefig(outPath, dpi=100, bbox_inches='tight')
    outPath2 = prePath + 'meanTP' + str(percentile) +'percentileE2EDScatter.png'
    fig.savefig(outPath2, dpi=100, bbox_inches='tight', format='png')
    plt.close('all')


def plotMeanQLMeanE2EDScatter(testName, sumNodes, nodeTypes, nodeSplit, numRouters):
    meanQLs = {}
    qlRows = [x for x in range(numRouters)]
    meanE2EDs = []
    file_to_read = '../exports/extracted/eachNodeMeanQLandMeanE2ED/' + makeFullScenarioName(testName, sumNodes, nodeTypes, nodeSplit) + '.csv'
    with open(file_to_read, mode='r') as readFile:
        csv_reader = csv.reader(readFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
        line_count = 0
        for row in csv_reader:
            if line_count in qlRows:
                meanQLs['router'+str(line_count)] = row
            elif line_count == qlRows[-1] + 1:
                meanE2EDs = row
            line_count += 1 

    fig, ax1 = plt.subplots(1, figsize=(16,12))
    # print(meanValues)
    routerNums = {0 : 'Uplink', 1 : 'Downlink'}
    for num in qlRows:
        ax1.plot(meanQLs['router'+str(num)], meanE2EDs, 'o', label=routerNums[num])
    
    plt.xlabel('Mean Queue Length [packets]')
    plt.ylabel('Mean Client End-To-End Delay [s]')
    plt.legend()
    prePath = '../exports/plots/' + makeFullScenarioName(testName, sumNodes, nodeTypes, nodeSplit) + '/'
    if not os.path.exists(prePath):
        os.makedirs(prePath)
    outPath = prePath + 'meanQLMeanE2EDScatter.pdf'
    fig.savefig(outPath, dpi=100, bbox_inches='tight')
    outPath2 = prePath + 'meanQLMeanE2EDScatter.png'
    fig.savefig(outPath2, dpi=100, bbox_inches='tight', format='png')
    plt.close('all')

# plotMeanTPMeanE2EDScatter('singleAppStressTest_SSH_smallLink', 8200, ['hostVID', 'hostFDO', 'hostSSH', 'hostVIP'], [0,0,400,0])

def plotAllValuesForDelayTest(testName, nodeTypes, nodeSplit, nodeType):
    print('Plotting for ' + testName)
    numCLI = sum(nodeSplit)
    valueTypes = []
    if nodeType == 'hostVIP':
        valueTypes = ['mos', 'endToEndDelay', 'packetLossRate', 'playoutDelay', 'playoutLossRate', 'taildropLossRate']
        plotDelayMeanTPsDirection(testName, numCLI, nodeTypes, nodeSplit, downlink)
    if nodeType == 'hostSSH':
        valueTypes = ['numActiveSessions', 'packetSent', 'packetReceived', 'endToEndDelay', 'roundTripTime', 'mosValue']
        plotDelayMeanTPsDirection(testName, numCLI, nodeTypes, nodeSplit, downlink)
        plotDelayMeanTPsDirection(testName, numCLI, nodeTypes, nodeSplit, uplink)
    if nodeType == 'hostVID':
        valueTypes = ['DASHBufferLength', 'DASHVideoBitrate', 'numActiveSessions', 'DASHReceivedBytes', 'DASHmosScore', 'DASHliveDelay']
        plotDelayMeanTPsDirection(testName, numCLI, nodeTypes, nodeSplit, downlink)
        plotDelayMeanTPsDirection(testName, numCLI, nodeTypes, nodeSplit, uplink)
    for valueType in valueTypes:
        plotDelayMeanValue(testName, numCLI, nodeTypes, nodeSplit, valueType)

def plotStressMeanValue(testName, numCLIs, nodeTypes, nodeSplit, valueType):
    meanValues = []
    file_to_read = '../exports/extracted/' + valueType + '/' + makeFullScenarioName(testName, numCLIs, nodeTypes, nodeSplit) + '.csv'
    with open(file_to_read, mode='r') as readFile:
        csv_reader = csv.reader(readFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
        line_count = 0
        for row in csv_reader:
            if line_count == 1:
                meanValues = row
                break
            line_count += 1 

    fig, ax1 = plt.subplots(1, figsize=(16,12))
    # print(meanValues)
    nCLI = [x for x, y in zip(numCLIs, meanValues) if y >= 0]
    meanVal = [x for x in meanValues if x >= 0]
    ax1.plot(nCLI, meanVal, 'o-')
    
    plt.xlabel('Number of Clients')
    plt.ylabel(makeXaxisLabel(valueType))
    prePath = '../exports/plots/' + makeFullScenarioName(testName, numCLIs, nodeTypes, nodeSplit) + '/'
    if not os.path.exists(prePath):
        os.makedirs(prePath)
    outPath = prePath + valueType + '.pdf'
    fig.savefig(outPath, dpi=100, bbox_inches='tight')
    outPath2 = prePath + valueType + '.png'
    fig.savefig(outPath2, dpi=100, bbox_inches='tight', format='png')
    plt.close('all')

def plotStressMeanTPsDirection(testName, numCLIs, nodeTypes, nodeSplit, direction):
    meanValues = []
    file_to_read = '../exports/extracted/throughput' + direction[0] + '/' + makeFullScenarioName(testName, numCLIs, nodeTypes, nodeSplit) + '.csv'
    with open(file_to_read, mode='r') as readFile:
        csv_reader = csv.reader(readFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
        line_count = 0
        for row in csv_reader:
            if line_count == 1:
                meanValues = row
                break
            line_count += 1 

    fig, ax1 = plt.subplots(1, figsize=(16,12))
    # print(meanValues)
    ax1.plot(numCLIs, meanValues, 'o-')
    
    plt.xlabel('Number of Clients')
    plt.ylabel('Mean ' + direction[0] + ' Throughput [kbps]')
    prePath = '../exports/plots/' + makeFullScenarioName(testName, numCLIs, nodeTypes, nodeSplit) + '/'
    if not os.path.exists(prePath):
        os.makedirs(prePath)
    outPath = prePath + 'meanThroughput' + direction[0] + '.pdf'
    fig.savefig(outPath, dpi=100, bbox_inches='tight')
    outPath2 = prePath + 'meanThroughput' + direction[0] + '.png'
    fig.savefig(outPath2, dpi=100, bbox_inches='tight', format='png')
    plt.close('all')

def plotAllValuesForStressTest(testName, numCLIs, nodeTypes, nodeSplit, nodeType):
    print('Plotting for ' + testName)
    valueTypes = []
    if nodeType == 'hostVIP':
        valueTypes = ['mos', 'endToEndDelay', 'packetLossRate', 'playoutDelay', 'playoutLossRate', 'taildropLossRate']
        plotStressMeanTPsDirection(testName, numCLIs, nodeTypes, nodeSplit, downlink)

    if nodeType == 'hostSSH':
        valueTypes = ['numActiveSessions', 'packetSent', 'packetReceived', 'endToEndDelay', 'roundTripTime', 'mosValue']
        plotStressMeanTPsDirection(testName, numCLIs, nodeTypes, nodeSplit, downlink)
        plotStressMeanTPsDirection(testName, numCLIs, nodeTypes, nodeSplit, uplink)

    if nodeType == 'hostFDO':
        valueTypes = ['endToEndDelay', 'mosScore', 'downloadTime', 'averageDownloadThroughput']
        plotStressMeanTPsDirection(testName, numCLIs, nodeTypes, nodeSplit, downlink)
        plotStressMeanTPsDirection(testName, numCLIs, nodeTypes, nodeSplit, uplink)

    if nodeType == 'hostVID':
        valueTypes = ['DASHBufferLength', 'DASHVideoBitrate', 'numActiveSessions', 'DASHReceivedBytes', 'DASHmosScore', 'DASHliveDelay']
        if 'Live' in testName:
            valueTypes.append('endToEndDelay')
        plotStressMeanTPsDirection(testName, numCLIs, nodeTypes, nodeSplit, downlink)
        plotStressMeanTPsDirection(testName, numCLIs, nodeTypes, nodeSplit, uplink)

    plotMeanTPMeanE2EDScatter(testName, sum(numCLIs),nodeTypes, nodeSplit)
    plotMeanTPMedianE2EDScatter(testName, sum(numCLIs),nodeTypes, nodeSplit)
    plotMeanTPMaxE2EDScatter(testName, sum(numCLIs),nodeTypes, nodeSplit)
    plotMeanTPXPercentileE2EDScatter(testName, sum(numCLIs),nodeTypes, nodeSplit, 90)
    plotMeanTPXPercentileE2EDScatter(testName, sum(numCLIs),nodeTypes, nodeSplit, 95)
    plotMeanTPXPercentileE2EDScatter(testName, sum(numCLIs),nodeTypes, nodeSplit, 97)

    plotMeanQLMeanE2EDScatter(testName, sum(numCLIs), nodeTypes, nodeSplit, 2)

    for valueType in valueTypes:
        plotStressMeanValue(testName, numCLIs, nodeTypes, nodeSplit, valueType)



# plotAllValuesForDelayTest('singleAppDelayTest_VoIP_1cli', ['hostVID', 'hostFDO', 'hostSSH', 'hostVIP'], [0,0,0,1], 'hostVIP')
# plotAllValuesForDelayTest('singleAppDelayTest_VoIP_10cli', ['hostVID', 'hostFDO', 'hostSSH', 'hostVIP'], [0,0,0,10], 'hostVIP')
# plotAllValuesForDelayTest('singleAppDelayTest_VoIP_50cli', ['hostVID', 'hostFDO', 'hostSSH', 'hostVIP'], [0,0,0,50], 'hostVIP')

# plotAllValuesForDelayTest('singleAppDelayTest_SSH_1cli', ['hostVID', 'hostFDO', 'hostSSH', 'hostVIP'], [0,0,1,0], 'hostSSH')
# plotAllValuesForDelayTest('singleAppDelayTest_SSH_10cli', ['hostVID', 'hostFDO', 'hostSSH', 'hostVIP'], [0,0,10,0], 'hostSSH')

# plotAllValuesForDelayTest('singleAppDelayTest_LiveVideo', ['hostVID', 'hostFDO', 'hostSSH', 'hostVIP'], [1,0,0,0], 'hostVID')
# plotAllValuesForDelayTest('singleAppDelayTest_LiveVideoV2', ['hostVID', 'hostFDO', 'hostSSH', 'hostVIP'], [1,0,0,0], 'hostVID')
# plotAllValuesForDelayTest('singleAppDelayTest_NewLiveVideoClient', ['hostVID', 'hostFDO', 'hostSSH', 'hostVIP'], [1,0,0,0], 'hostVID')

# plotAllValuesForStressTest('singleAppStressTest_VoIP', [1,5,10,15,20,25,30,35,40,45,50,55,60], ['hostVID', 'hostFDO', 'hostSSH', 'hostVIP'], [0,0,0,60], 'hostVIP')
plotAllValuesForStressTest('singleAppStressTest_VoIP', [1,5,10,15,20,21,22,23,24,25,26,27,28,29,30,35,40,45,50,55,60], ['hostVID', 'hostFDO', 'hostSSH', 'hostVIP'], [0,0,0,60], 'hostVIP')

# plotAllValuesForStressTest('singleAppStressTest_SSH', [10,20,30,40,50,60,70,80,90,100,110,120,130,140,150,160,170,180,190,200,210,220,230,240,250,260,270,280,290,300], ['hostVID', 'hostFDO', 'hostSSH', 'hostVIP'], [0,0,300,0], 'hostSSH')
plotAllValuesForStressTest('singleAppStressTest_SSH_smallLink', [10,20,30,40,50,60,70,80,90,100,110,120,130,140,150,160,170,180,190,200,210,220,230,240,250,260,270,280,290,300,310,320,330,340,350,360,370,380,390,400], ['hostVID', 'hostFDO', 'hostSSH', 'hostVIP'], [0,0,400,0], 'hostSSH')

# plotAllValuesForStressTest('singleAppStressTest_FileDownload', [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40], ['hostVID', 'hostFDO', 'hostSSH', 'hostVIP'], [0,40,0,0], 'hostFDO')
plotAllValuesForStressTest('singleAppStressTest_FileDownload2-5MB', [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40], ['hostVID', 'hostFDO', 'hostSSH', 'hostVIP'], [0,40,0,0], 'hostFDO')

# plotAllValuesForStressTest('singleAppStressTest_Video', [1,5,10,15,20,25,30,35,40,45,50,55,60,65,70,75,80,85,90,95,100,105,110,115,120,125,130,135,140,145,150], ['hostVID', 'hostFDO', 'hostSSH', 'hostVIP'], [150,0,0,0], 'hostVID')
plotAllValuesForStressTest('singleAppStressTest_VideoV2', [1,5,10,15,20,25,30,35,40,45,50,55,60,65,70,75,80,85,90,95,100,105,110,115,120,125,130,135,140,145,150], ['hostVID', 'hostFDO', 'hostSSH', 'hostVIP'], [150,0,0,0], 'hostVID')

# plotAllValuesForStressTest('singleAppStressTest_LiveVideo', [1,5,10,15,20,25,30,35,40,45,50,55,60,65,70,75,80,85,90,95,100,105,110,115,120,125,130,135,140,145,150], ['hostVID', 'hostFDO', 'hostSSH', 'hostVIP'], [150,0,0,0], 'hostVID')
# plotAllValuesForStressTest('singleAppStressTest_LiveVideoV2', [1,5,10,15,20,25,30,35,40,45,50,55,60,65,70,75,80,85,90,95,100,105,110,115,120,125,130,135,140,145,150], ['hostVID', 'hostFDO', 'hostSSH', 'hostVIP'], [150,0,0,0], 'hostVID')
plotAllValuesForStressTest('singleAppStressTest_NewLiveVideoClient', [1,2,3,4,5,6,7,8,9,10,15,20,25,30,35,40,45,50,55,60,65,70,75,80,85,90,95,100,105,110,115,120,125,130,135,140,145,150], ['hostVID', 'hostFDO', 'hostSSH', 'hostVIP'], [150,0,0,0], 'hostVID')