import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import csv
import math
import statistics
import os

import glob

font = {'weight' : 'normal',
        'size'   : 40}

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

# def importDF(testName, numCLI, nodeTypes, nodeSplit, dataType):
#     # File that will be read
#     fullScenarioName = makeFullScenarioName(testName, numCLI, nodeTypes, nodeSplit)
#     file_to_read = '../exports/extracted/' + str(dataType) + '/' + fullScenarioName + '.csv'
#     print("Results from run: " + file_to_read)
#     # Read the CSV
#     return pd.read_csv(file_to_read)

# def importDFextended(testName, numCLI, nodeTypes, nodeSplit, dataType, extension):
#     # File that will be read
#     print(filenames)
#     fullScenarioName = makeFullScenarioName(testName, numCLI, nodeTypes, nodeSplit)
#     file_to_read = '../exports/extracted/' + str(dataType) + '/' + fullScenarioName + extension + '.csv'
#     print("Results from run: " + file_to_read)
#     # Read the CSV
#     return pd.read_csv(file_to_read)

def filterDFType(df, filterType):
    return df.filter(like=filterType)

def getFilteredDFtypeAndTS(df, filterType):
    filteredDF = filterDFType(df, filterType)
    if len(filteredDF.columns):
        colNoTS = df.columns.get_loc(df.filter(filteredDF).columns[0])
        return df.iloc[:,[colNoTS,colNoTS+1]].dropna()
    else:
        return pd.DataFrame(columns=['ts', 'tp'])

def importDFdata(testName, nodeType, nodeNum):
    # File that will be read
    # fullScenarioExportName = makeFullScenarioName(testName, numCLI, nodeTypes, nodeSplit)
    folder = glob.glob('../'+testName+'/*')
    prePath = folder[0]+'/vectors/'
    
    # print(filenames)
    fileToRead = glob.glob(prePath+'*'+nodeType+str(nodeNum)+'*')[0]
    print(fileToRead)
    # fileToRead = '../' + str(testName) + '/' + fullScenarioExportName + '/vectors/' + fullScenarioExportName + '_' + makeNodeIdentifier(nodeType, nodeNum) + '_vec.csv'
    # print("Importing: " + fileToRead)
    # Read the CSV
    return pd.read_csv(fileToRead)

# importDFdata('aNewHopeV1GBR85No2_2sli_R100_Q30_M85_C200', 'hostVIP', 13)

def calculateThrougputPerSecondDirection(df, direction, nodeIdent, timestep):
    dirDF = getFilteredDFtypeAndTS(df, direction[1])
    dirDF = dirDF.rename(columns={str(dirDF.columns[0]) : "ts", str(dirDF.columns[1]) : "bytes"})
    print(statistics.mean(dirDF['bytes'].tolist()))
    sT = timestep/1000 # timestep in seconds
    # print(sT)
    tB = [0,sT] # time bounds for calculation
    colName = direction[0] + ' Throughput ' + nodeIdent
    tpDirDF = pd.DataFrame(columns=[colName])
    while tB[1] <= maxSimTime:
        # if DEBUG: print(tB, end =" -> Throughput: ")
        throughput = dirDF.loc[(dirDF['ts'] > tB[0]) & (dirDF['ts'] <= tB[1])]["bytes"].sum()/sT
        # if throughput != 0 and throughput != 3750: print(tB[1], throughput)
        tpDirDF = tpDirDF.append({colName : throughput*8/1000}, ignore_index=True)
        # if DEBUG: print(throughput*8/1000, end=" kbps\n")
        tB = [x+sT for x in tB]
    return tpDirDF

# timestep in miliseconds
def extractNodeThroughputDirection(testName, nodeType, nodeNum, timestep, direction):
    print('TP ' + direction[0], end=' - ')
    nodeDF = importDFdata(testName, nodeType, nodeNum)
    # print(nodeDF)
    nodeIdent = makeNodeIdentifier(nodeType, nodeNum)
    return calculateThrougputPerSecondDirection(nodeDF, direction, nodeIdent, timestep)

# print(extractNodeThroughputDirection('aNewHopeV1GBR85No2_2sli_R100_Q30_M85_C200', 'hostVIP', 13, 20, downlink))

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

def extractNodeDataTypeToDF(testName, nodeType, nodeNum, dataType, dataIdent):
    print(dataIdent, end=' - ')
    nodeDF = importDFdata(testName, nodeType, nodeNum)
    dataTypeDF = getFilteredDFtypeAndTS(nodeDF, dataType)
    nodeIdent = makeNodeIdentifier(nodeType, nodeNum)
    dataTypeDF = dataTypeDF.rename(columns={str(dataTypeDF.columns[0]) : nodeIdent + " " + dataIdent + " TS", str(dataTypeDF.columns[1]) : nodeIdent + " " + dataIdent + " Val"})
    return dataTypeDF


def plotTPdirection(testName, nodeType, nodeNum, timestep, direction):
    df = extractNodeThroughputDirection(testName, nodeType, nodeNum, timestep, direction)
    # print(df)
    sT = timestep/1000
    fig, ax1 = plt.subplots(1, figsize=(16,12))
    colName = direction[0] + " Throughput " + makeNodeIdentifier(nodeType, nodeNum)

    tps = df[colName].tolist()
    index = [ n for n,i in enumerate(tps) if i>30.0 ]
    firstTime = 0
    lastTime = 10
    if len(index) > 0:
        firstTime = max(index[0]-5/sT, 0)*sT
        lastTime = firstTime + 10

    timesTemp = range(1,len(tps)+1,1)
    times = []
    for i in timesTemp:
        times.append(i*sT)

    ax1.plot(times, tps, label=chooseName(nodeType), marker='o', ls='-', color='tab:red')
    
    ax1.set_ylabel(direction[0]+' Throughput [mbps]')
    ax1.set_xlabel('Simulation Time [s]')
    ax1.set_xlim(firstTime, lastTime)
    # ax1.set_ylim(0,105)
    # plt.legend()
    plt.grid(True)
    prePath = '../exports/plots/oneVoIP/thorughputs/'
    if not os.path.exists(prePath):
        os.makedirs(prePath)
    fig.savefig(prePath+testName+'_'+direction[0]+'Throughput_' + str(nodeType) + str(nodeNum) + '_timestep' + str(timestep) + '.pdf', dpi=100, bbox_inches='tight')

def plotTPdirectionAndE2ED(testName, nodeType, nodeNum, timestep, direction):
    df = extractNodeThroughputDirection(testName, nodeType, nodeNum, timestep, direction)
    # print(df)
    sT = timestep/1000
    fig, (ax1, ax2) = plt.subplots(nrows=2, ncols=1, figsize=(16,24))
    colName = direction[0] + " Throughput " + makeNodeIdentifier(nodeType, nodeNum)

    tps = df[colName].tolist()
    index = [ n for n,i in enumerate(tps) if i>30.0 ]
    firstTime = 0
    lastTime = 10
    if len(index) > 0:
        firstTime = max(index[0]-5/sT, 0)*sT
        lastTime = firstTime + 10

    timesTemp = range(1,len(tps)+1,1)
    times = []
    for i in timesTemp:
        times.append(i*sT)

    ax1.plot(times, tps, label=chooseName(nodeType), marker='o', ls='-', color='tab:red')
    
    df2 = extractNodeDataTypeToDF(testName, nodeType, nodeNum, 'endToEndDelay', 'e2ed')
    timesDel = df2[makeNodeIdentifier(nodeType, nodeNum) + " " + 'e2ed' + " TS"].dropna().tolist()
    delays = df2[makeNodeIdentifier(nodeType, nodeNum) + " " + 'e2ed' + " Val"].dropna().tolist()
    ax2.plot(timesDel, [x*1000 for x in delays], label=chooseName(nodeType), marker='o', ls='-', color='tab:blue')


    ax1.set_ylabel(direction[0]+' Throughput [kbps]')
    ax2.set_xlabel('Simulation Time [s]')
    ax1.set_xlabel('Simulation Time [s]')
    ax1.set_xlim(firstTime, lastTime)
    ax2.set_ylabel('End-To-End Delay [ms]')
    ax2.set_xlim(firstTime, lastTime)
    ax2.set_ylim(55,100)
    # plt.legend()
    ax1.grid(True)
    ax2.grid(True)
    prePath = '../exports/plots/oneVoIP/thorughputAndDelay/'
    if not os.path.exists(prePath):
        os.makedirs(prePath)
    fig.savefig(prePath+testName+'_'+direction[0]+'ThroughputAndDelay_' + str(nodeType) + str(nodeNum) + '_timestep' + str(timestep) + '.png', dpi=100, bbox_inches='tight', format='png')

testNames = [
    'aNewHopeV1GBR100No12Base_R100_Q30_M100_C200',
    'aNewHopeV1GBR100No2_2sli_R100_Q30_M100_C200',
    'aNewHopeV1GBR100No3_5sli_R100_Q30_M100_C200',
    'aNewHopeV1GBR85No12Base_R100_Q30_M85_C200',
    'aNewHopeV1GBR85No2_2sli_R100_Q30_M85_C200',
    'aNewHopeV1GBR85No3_5sli_R100_Q30_M85_C200',
    'aNewHopeV1GBR100No12Base_R100_Q35_M100_C200',
    'aNewHopeV1GBR100No2_2sli_R100_Q35_M100_C200',
    'aNewHopeV1GBR100No3_5sli_R100_Q35_M100_C200',
    'aNewHopeV1GBR85No12Base_R100_Q35_M85_C200',
    'aNewHopeV1GBR85No2_2sli_R100_Q35_M85_C200',
    'aNewHopeV1GBR85No3_5sli_R100_Q35_M85_C200',
    'aNewHopeV1GBR100No12Base_R100_Q40_M100_C200',
    'aNewHopeV1GBR100No2_2sli_R100_Q40_M100_C200',
    'aNewHopeV1GBR100No3_5sli_R100_Q40_M100_C200',
    'aNewHopeV1GBR85No12Base_R100_Q40_M85_C200',
    'aNewHopeV1GBR85No2_2sli_R100_Q40_M85_C200',
    'aNewHopeV1GBR85No3_5sli_R100_Q40_M85_C200'
]

for testName in testNames:
    # plotTPdirection(testName, 'hostVIP', 13, 20, downlink)
    plotTPdirectionAndE2ED(testName, 'hostVIP', 13, 20, downlink)