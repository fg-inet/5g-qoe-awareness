import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import csv
import math
import statistics
from scipy import stats

font = {'weight' : 'normal',
        'size'   : 30}

matplotlib.rc('font', **font)
matplotlib.rc('lines', linewidth=2.0)
matplotlib.rc('lines', markersize=8)

downlink = ['Downlink', 'rxPkOk:vector(packetBytes)']
uplink = ['Uplink', 'txPk:vector(packetBytes)']
maxSimTime = 400

def partialCDFBegin():
    fig, ax = plt.subplots(1, figsize=(16,12))
    return fig, ax

def partialCDFPlotData(fig, ax, data, label, lineType, lineColor):
    sorted_data = np.sort(data)
    linspaced = np.linspace(0, 1, len(data), endpoint=False)
    ax.plot(sorted_data, linspaced, lineType, label=label, color=lineColor)

def partialCDFEnd(fig, ax, title, xLabel, outPath):
    ax.set_ylim(0,1.1)
    plt.legend()
    plt.title(title)
    plt.xlabel(xLabel)
    plt.ylabel("CDF")
    fig.savefig(outPath, dpi=100, bbox_inches='tight')
    plt.close('all')

def partialCDFEndPNG(fig, ax, title, xLabel, outPath):
    ax.set_ylim(0,1.1)
    plt.legend()
    plt.title(title)
    plt.xlabel(xLabel)
    plt.ylabel("CDF")
    fig.savefig(outPath, dpi=100, bbox_inches='tight', format='png')
    plt.close('all')

def importDF(testName, numCLI, dataType, dataTypeExtension):
    # File that will be read
    fullScenarioName = str(testName) + '_' + str(numCLI)
    file_to_read = '../exports/extracted/' + str(dataType) + '/' + fullScenarioName + dataTypeExtension + '.csv'
    print("Results from run: " + file_to_read)
    # Read the CSV
    return pd.read_csv(file_to_read)

def plotTPdirection(testName, numCLI, cliNumBoundaries, cliTypes, direction):
    df = importDF(testName, numCLI, 'throughputs', '_' + direction[0])
    fig, ax1 = plt.subplots(1, figsize=(16,12))
    lowerBound = 0
    upperBound = 0
    times = range(1,maxSimTime+1,1)
    for idx in range(len(cliNumBoundaries)):
        upperBound = cliNumBoundaries[idx]
        tempDF = pd.DataFrame()
        for i in range(lowerBound, upperBound+1, 1):
            colName = direction[0] + ' Throughput cli' + str(i)
            tempDF = pd.concat([tempDF,df[colName]],axis=1,ignore_index=False)
        ax1.plot(times, [x/1000 for x in tempDF.sum(axis=1).tolist()], label=cliTypes[idx], marker='o', ls='-')
        lowerBound = cliNumBoundaries[idx] + 1

    linkTP = [x/1000 for x in df[direction[0] + ' Throughput link'].tolist()]
    ax1.plot(times, linkTP, label="Link", marker='o', ls='-')
    ax1.set_ylabel(direction[0]+' Throughput [mbps]')
    ax1.set_xlabel('Simulation Time [s]')
    ax1.set_xlim(0,1.05*times[-1])
    ax1.set_ylim(0,1.05*max(linkTP))
    plt.legend()
    fig.savefig('../exports/plots/'+str(testName)+'_'+direction[0]+'Throughputs.pdf', dpi=100, bbox_inches='tight')

def plotTPdirectionSingleApp(testNames, numCLIs, appBoundaries, cliTypeName, direction):
    fig, ax1 = plt.subplots(1, figsize=(16,12))
    iterator = 0
    for testName in testNames:
        df = importDF(testName, numCLIs[iterator], 'throughputs', '_' + direction[0])
        lowerBound = appBoundaries[iterator][0]
        upperBound = appBoundaries[iterator][1]
        times = range(1,maxSimTime+1,1)
        tempDF = pd.DataFrame()
        for i in range(lowerBound, upperBound+1, 1):
            colName = direction[0] + ' Throughput cli' + str(i)
            tempDF = pd.concat([tempDF,df[colName]],axis=1,ignore_index=False)
        ax1.plot(times, [x/1000 for x in tempDF.sum(axis=1).tolist()], label=testName, marker='o', ls='-')
        iterator += 1
        # linkTP = [x/1000 for x in df[direction[0] + ' Throughput link'].tolist()]
        # ax1.plot(times, linkTP, label="Link", marker='o', ls='-')
    ax1.set_ylabel(direction[0]+' Throughput [mbps]')
    ax1.set_xlabel('Simulation Time [s]')
    # ax1.set_xlim(0,1.05*times[-1])
    # ax1.set_ylim(0,1.05*max(linkTP))
    plt.legend()
    fig.savefig('../exports/plots/'+str(testNames)+'_'+str(cliTypeName)+'_'+direction[0]+'Throughputs.pdf', dpi=100, bbox_inches='tight')

def plotMeanMOScdfAppClass(testName, numCLI, cliNumBoundaries, cliTypes, lineColors):
    df = importDF(testName, numCLI, 'mos', '')
    lowerBound = 0
    upperBound = 0
    fig, ax1 = partialCDFBegin()
    for idx in range(len(cliNumBoundaries)):
        upperBound = cliNumBoundaries[idx]
        tempMOS = []
        for i in range(lowerBound, upperBound+1, 1):
            colName = 'cli' + str(i) + ' Mos Val'
            tempMOS.append(statistics.mean(df[colName].dropna().tolist()) if len(df[colName].dropna().tolist()) > 0 else 1)
        # print(tempMOS)
        partialCDFPlotData(fig, ax1, tempMOS, cliTypes[idx], '-o', lineColors[idx])
        lowerBound = cliNumBoundaries[idx] + 1
    ax1.set_xlim(0.95,5.05)
    partialCDFEnd(fig,ax1,'', 'Mean Client MOS Value', '../exports/plots/'+str(testName)+'_MeanMosCDFAppClass.pdf')

def plotMOSappClass(testName, numCLI, cliNumBoundaries, cliTypes, lineColors):
    df = importDF(testName, numCLI, 'mos', '')
    lowerBound = 0
    upperBound = 0
    fig, ax1 = plt.subplots(1, figsize=(16,12))
    for idx in range(len(cliNumBoundaries)):
        upperBound = cliNumBoundaries[idx]
        tempTime = []
        tempMOS = []
        for i in range(lowerBound, upperBound+1, 1):
            colName = 'cli' + str(i) + ' Mos Val'
            tempMOS.extend(df[colName].dropna().tolist())
            colName = 'cli' + str(i) + ' Mos TS'
            tempTime.extend(df[colName].dropna().tolist())
        ax1.plot(tempTime, tempMOS, '-o', label=cliTypes[idx], color=lineColors[idx])
        lowerBound = cliNumBoundaries[idx] + 1

    ax1.set_ylabel('MOS Value')
    ax1.set_xlabel('Simulation Time [s]')
    ax1.set_xlim(0,1.05*maxSimTime)
    ax1.set_ylim(1,1.05*5)
    plt.legend()
    fig.savefig('../exports/plots/'+str(testName)+'_mosAppClass.pdf', dpi=100, bbox_inches='tight')

def plotTPScdfDirection(testName, numCLI, cliNumBoundaries, cliTypes, direction, lineColors, cutoff):
    df = importDF(testName, numCLI, 'throughputs', '_' + direction[0])
    fig, ax1 = partialCDFBegin()
    lowerBound = 0
    upperBound = 0
    for idx in range(len(cliNumBoundaries)):
        upperBound = cliNumBoundaries[idx]
        tempTPSall = []
        for i in range(lowerBound, upperBound+1, 1):
            colName = direction[0] + ' Throughput cli' + str(i)
            tempTPSall.extend([x/1000 for x in df[colName].tolist()[:int(cutoff)+1]])
        partialCDFPlotData(fig, ax1, tempTPSall, cliTypes[idx], '-o', lineColors[idx])
        lowerBound = cliNumBoundaries[idx] + 1

    # linkTP = [x/1000 for x in df[direction[0] + ' Throughput link'].tolist()[:int(cutoff)+1]]
    # partialCDFPlotData(fig, ax1, linkTP, 'link', '-o', 'k')
    partialCDFEnd(fig,ax1,'', 'Throughput [mbps]', '../exports/plots/'+str(testName)+'_'+direction[0]+'CDFtpsCutoff'+ str(cutoff) + '.pdf')

def plotTPScdfDirectionSingleApp(testNames, numCLIs, appBoundaries, cliTypeName, direction, lineColors, cutoff):
    fig, ax1 = partialCDFBegin()
    iterator = 0
    for testName in testNames:
        df = importDF(testName, numCLIs[iterator], 'throughputs', '_' + direction[0])
        lowerBound = appBoundaries[iterator][0]
        upperBound = appBoundaries[iterator][1]
        tempTPSall = []
        for i in range(lowerBound, upperBound+1, 1):
            colName = direction[0] + ' Throughput cli' + str(i)
            tempTPSall.extend([x/1000 for x in df[colName].tolist()[:int(cutoff)+1]])
        partialCDFPlotData(fig, ax1, tempTPSall, testName, '-o', lineColors[iterator])
        iterator += 1

    # linkTP = [x/1000 for x in df[direction[0] + ' Throughput link'].tolist()[:int(cutoff)+1]]
    # partialCDFPlotData(fig, ax1, linkTP, 'link', '-o', 'k')
    partialCDFEnd(fig,ax1,'', 'Throughput [mbps]', '../exports/plots/'+str(testNames)+'_'+str(cliTypeName)+'_'+direction[0]+'CDFtpsCutoff'+ str(cutoff) + '.pdf')

def plotMeanTPScdfDirection(testName, numCLI, cliNumBoundaries, cliTypes, direction, lineColors, cutoff):
    df = importDF(testName, numCLI, 'throughputs', '_' + direction[0])
    fig, ax1 = partialCDFBegin()
    lowerBound = 0
    upperBound = 0
    for idx in range(len(cliNumBoundaries)):
        upperBound = cliNumBoundaries[idx]
        tempTPSall = []
        for i in range(lowerBound, upperBound+1, 1):
            colName = direction[0] + ' Throughput cli' + str(i)
            tempTPSall.append(statistics.mean([x/1000 for x in df[colName].tolist()[:int(cutoff)+1]]))
        partialCDFPlotData(fig, ax1, tempTPSall, cliTypes[idx], '-o', lineColors[idx])
        lowerBound = cliNumBoundaries[idx] + 1

    # linkTP = [x/1000 for x in df[direction[0] + ' Throughput link'].tolist()[:int(cutoff)+1]]
    # partialCDFPlotData(fig, ax1, linkTP, 'link', '-o', 'k')
    partialCDFEnd(fig,ax1,'', 'Mean Client Throughput [mbps]', '../exports/plots/'+str(testName)+'_'+direction[0]+'CDFmeanTpsCutoff'+ str(cutoff) + '.pdf')

def plotMeanTPScdfDirectionSingleApp(testNames, numCLIs, appBoundaries, cliTypeName, direction, lineColors, cutoff):
    fig, ax1 = partialCDFBegin()
    iterator = 0
    for testName in testNames:
        df = importDF(testName, numCLIs[iterator], 'throughputs', '_' + direction[0])
        lowerBound = appBoundaries[iterator][0]
        upperBound = appBoundaries[iterator][1]
        tempTPSall = []
        for i in range(lowerBound, upperBound+1, 1):
            colName = direction[0] + ' Throughput cli' + str(i)
            tempTPSall.append(statistics.mean([x/1000 for x in df[colName].tolist()[:int(cutoff)+1]]))
        partialCDFPlotData(fig, ax1, tempTPSall, testName, '-o', lineColors[iterator])
        iterator += 1

    partialCDFEnd(fig,ax1,'', 'Mean Client Throughput [mbps]', '../exports/plots/'+str(testNames)+'_'+str(cliTypeName)+'_'+direction[0]+'CDFmeanTpsCutoff'+ str(cutoff) + '.pdf')

def plotMOScdfAppClass(testName, numCLI, cliNumBoundaries, cliTypes, lineColors):
    df = importDF(testName, numCLI, 'mos', '')
    lowerBound = 0
    upperBound = 0
    fig, ax1 = partialCDFBegin()
    for idx in range(len(cliNumBoundaries)):
        upperBound = cliNumBoundaries[idx]
        tempMOS = []
        for i in range(lowerBound, upperBound+1, 1):
            colName = 'cli' + str(i) + ' Mos Val'
            tempMOS.extend(df[colName].dropna().tolist())
        # print(tempMOS)
        partialCDFPlotData(fig, ax1, tempMOS, cliTypes[idx], '-o', lineColors[idx])
        lowerBound = cliNumBoundaries[idx] + 1

    partialCDFEnd(fig,ax1,'', 'MOS Value', '../exports/plots/'+str(testName)+'_mosCDFAppClass.pdf')

def plotMOScdfSingleAppMultiTest(testNames, numCLIs, appBoundaries, cliTypeName, lineColors):
    fig, ax1 = partialCDFBegin()
    ax1.set_xlim(0.95, 5.05)
    iterator = 0
    for testName in testNames:
        df = importDF(testName, numCLIs[iterator], 'mos', '')
        lowerBound = appBoundaries[iterator][0]
        upperBound = appBoundaries[iterator][1]
        tempMOS = []
        for i in range(lowerBound, upperBound+1, 1):
            colName = 'cli' + str(i) + ' Mos Val'
            tempMOS.extend(df[colName].dropna().tolist())
        partialCDFPlotData(fig, ax1, tempMOS, testName, '-o', lineColors[iterator])
        iterator += 1

    partialCDFEndPNG(fig,ax1,'', 'MOS Value', '../exports/plots/' + str(testNames) + '_' + str(cliTypeName) + '_mosCDF.png')

def plotRTTcdfSSHVoIP(testName, numCLI, lowBoundSSH, highBoundSSH, lowBoundVoIP, highBoundVoIP):
    df = importDF(testName, numCLI, 'rtt', '')
    fig, ax1 = partialCDFBegin()
    tempRTT = []
    for i in range(lowBoundSSH, highBoundSSH+1, 1):
        colName = 'cli' + str(i) + ' RTT Val'
        tempRTT.extend([x for x in df[colName].dropna().tolist() if x < 2])
    partialCDFPlotData(fig, ax1, tempRTT, 'SSH', '-o', 'y') 
    partialCDFEnd(fig,ax1,'', 'Round Trip Time [s]', '../exports/plots/'+str(testName)+'_sshVoIPrttCDF.pdf')

def plotRTTcdfSSHmultiTest(testNames, numCLIs, appBoundaries, lineColors):
    fig, ax1 = partialCDFBegin()
    iterator = 0
    for testName in testNames:
        df = importDF(testName, numCLIs[iterator], 'rtt', '')
        tempRTT = []
        for i in range(appBoundaries[iterator][0], appBoundaries[iterator][1]+1, 1):
            colName = 'cli' + str(i) + ' RTT Val'
            tempRTT.extend([x for x in df[colName].dropna().tolist() if x < 2])
        partialCDFPlotData(fig, ax1, tempRTT, testName, '-o', lineColors[iterator])
        iterator += 1
    partialCDFEndPNG(fig,ax1,'', 'Round Trip Time [s]', '../exports/plots/'+str(testNames)+'_SSHrttCDFmultiRun.png')

def plotMeanRTTcdfSSHVoIP(testName, numCLI, lowBoundSSH, highBoundSSH, lowBoundVoIP, highBoundVoIP):
    df = importDF(testName, numCLI, 'rtt', '')
    fig, ax1 = partialCDFBegin()
    tempRTT = []
    for i in range(lowBoundSSH, highBoundSSH+1, 1):
        colName = 'cli' + str(i) + ' RTT Val'
        tempRTT.append(statistics.mean(df[colName].dropna().tolist())*1000)
    partialCDFPlotData(fig, ax1, tempRTT, 'SSH Round Trip Time', '-o', 'y')
    df = importDF(testName, numCLI, 'e2ed', '')
    tempE2ED = []
    for i in range(lowBoundVoIP, highBoundVoIP+1, 1):
        colName = 'cli' + str(i) + ' E2ED Val'
        tempE2ED.append(statistics.mean(df[colName].dropna().tolist())*1000)
    partialCDFPlotData(fig, ax1, tempE2ED, 'VoIP End-To-End Delay', '-o', 'b')

    partialCDFEnd(fig,ax1,'', 'Mean Time [ms]', '../exports/plots/'+str(testName)+'_sshVoIPrttMeanCDF.pdf')

def plotE2EDcdfVoiP(testNames, numCLIs, appBoundaries, lineColors):
    fig, ax1 = partialCDFBegin()
    iterator = 0
    for testName in testNames:
        df = importDF(testName, numCLIs[iterator], 'e2ed', '')
        lowerBound = appBoundaries[iterator][0]
        upperBound = appBoundaries[iterator][1]
        tempE2ED = []
        for i in range(lowerBound, upperBound+1, 1):
            colName = 'cli' + str(i) + ' E2ED Val'
            # tempE2ED.append(statistics.mean(df[colName].dropna().tolist())*1000)
            tempE2ED.extend(df[colName].dropna().tolist())
        partialCDFPlotData(fig, ax1, tempE2ED, testName, '-o', lineColors[iterator])
        iterator += 1
    partialCDFEndPNG(fig,ax1,'', 'End-To-End Delay [s]', '../exports/plots/'+str(testNames)+'_VoIP_e2edCDFsingleApp.png')

def plotPkLRcdfVoiP(testNames, numCLIs, appBoundaries, lineColors):
    fig, ax1 = partialCDFBegin()
    iterator = 0
    for testName in testNames:
        df = importDF(testName, numCLIs[iterator], 'pklr', '')
        lowerBound = appBoundaries[iterator][0]
        upperBound = appBoundaries[iterator][1]
        tempE2ED = []
        for i in range(lowerBound, upperBound+1, 1):
            colName = 'cli' + str(i) + ' PkLR Val'
            # tempE2ED.append(statistics.mean(df[colName].dropna().tolist())*1000)
            tempE2ED.extend(df[colName].dropna().tolist())
        partialCDFPlotData(fig, ax1, tempE2ED, testName, '-o', lineColors[iterator])
        iterator += 1
    partialCDFEndPNG(fig,ax1,'', 'Packet Loss Rate - Ratio', '../exports/plots/'+str(testNames)+'_VoIP_pklrCDFsingleApp.png')

def plotRTOcdf(testName, numCLI):
    rtos = []
    numSession = 0
    numSessionWithRTO = 0
    fullScenarioName = str(testName) + '_' + str(numCLI)
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
    fig, ax1 = partialCDFBegin()
    partialCDFPlotData(fig, ax1, rtos, 'SSH Server', '-o', 'y')
    ax1.text(0.25,0.12, 'SSH server sessions - total: ' + str(int(numSession)), horizontalalignment='left', transform=ax1.transAxes)
    ax1.text(0.25,0.07, 'SSH server sessions - with timeout: ' + str(int(numSessionWithRTO)), horizontalalignment='left', transform=ax1.transAxes)
    ax1.text(0.25,0.02, 'Sessions with timeout: ' + str(round(numSessionWithRTO*100/numSession, 2)) + '%', horizontalalignment='left', transform=ax1.transAxes)
    partialCDFEnd(fig,ax1,'', 'RTO Value [s]', '../exports/plots/'+str(testName)+'_sshRtoCDF.pdf')

def plotSSHRTOcdfMultiTest(testNames, numCLIs, lineColors):
    fig, ax1 = partialCDFBegin()
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

# plotSSHRTOcdfMultiTest(['baselineTest10', 'baselineTest20', 'baselineTest30', 'baselineTest40', 'baselineTest50'], [40,80,120,160,200], ['r', 'g', 'y', 'b', 'c'])

def plotAll(testName, numCLI, cliNumBoundaries, cliTypes, lineColors, cutoff):
    plotMeanTPScdfDirection(testName, numCLI, cliNumBoundaries, cliTypes, downlink, lineColors, cutoff)
    plotMeanTPScdfDirection(testName, numCLI, cliNumBoundaries, cliTypes, uplink, lineColors, cutoff)
    plotTPScdfDirection(testName, numCLI, cliNumBoundaries, cliTypes, downlink, lineColors, cutoff)
    plotTPScdfDirection(testName, numCLI, cliNumBoundaries, cliTypes, uplink, lineColors, cutoff)
    plotTPdirection(testName, numCLI, cliNumBoundaries, cliTypes, downlink)
    plotTPdirection(testName, numCLI, cliNumBoundaries, cliTypes, uplink)
    plotMOScdfAppClass(testName, numCLI, cliNumBoundaries, cliTypes, lineColors)
    plotMeanMOScdfAppClass(testName, numCLI, cliNumBoundaries, cliTypes, lineColors)
    # lowBoundSSH = 0
    # if cliTypes.index('SSH') - 1 > 0:
    #     lowBoundSSH = cliNumBoundaries[cliTypes.index('SSH') - 1] + 1
    # highBoundSSH = cliNumBoundaries[cliTypes.index('SSH')]
    # lowBoundVoIP = 0
    # if cliTypes.index('VoIP') - 1 > 0:
    #     lowBoundVoIP = cliNumBoundaries[cliTypes.index('VoIP') - 1] + 1
    # highBoundVoIP = cliNumBoundaries[cliTypes.index('VoIP')]
    # plotMeanRTTcdfSSHVoIP(testName, numCLI, lowBoundSSH, highBoundSSH, lowBoundVoIP, highBoundVoIP)
    # plotRTTcdfSSHVoIP(testName, numCLI, lowBoundSSH, highBoundSSH, lowBoundVoIP, highBoundVoIP)
    # plotRTOcdf(testName, numCLI)

# plotAll('baselineTest10', 40, [9,19,29,39], ['File Download', 'Video', 'SSH', 'VoIP'], ['r', 'g', 'y', 'b'], 400)
# plotAll('baselineTest20', 80, [19,39,59,79], ['File Download', 'Video', 'SSH', 'VoIP'], ['r', 'g', 'y', 'b'], 400)
# plotAll('baselineTest30', 120, [29,59,89,119], ['File Download', 'Video', 'SSH', 'VoIP'], ['r', 'g', 'y', 'b'], 400)
# plotAll('baselineTest40', 160, [39,79,119,159], ['File Download', 'Video', 'SSH', 'VoIP'], ['r', 'g', 'y', 'b'], 400)
# plotAll('baselineTest50', 200, [49,99,149,199], ['File Download', 'Video', 'SSH', 'VoIP'], ['r', 'g', 'y', 'b'], 400)

# plotMOScdfSingleAppMultiTest(['baselineTest10', 'baselineTest20', 'baselineTest30', 'baselineTest40', 'baselineTest50'], [40,80,120,160,200], [[0,9], [0,19], [0,29], [0,39], [0,49]], 'FileDownload', ['r', 'g', 'y', 'b', 'c'])
# plotMOScdfSingleAppMultiTest(['baselineTest10', 'baselineTest20', 'baselineTest30', 'baselineTest40', 'baselineTest50'], [40,80,120,160,200], [[10,19], [20,39], [30,59], [40,79], [50,99]], 'Video', ['r', 'g', 'y', 'b', 'c'])
# plotMOScdfSingleAppMultiTest(['baselineTest10', 'baselineTest20', 'baselineTest30', 'baselineTest40', 'baselineTest50'], [40,80,120,160,200], [[20,29], [40,59], [60,89], [80,119], [100,149]], 'SSH', ['r', 'g', 'y', 'b', 'c'])
# plotMOScdfSingleAppMultiTest(['baselineTest10', 'baselineTest20', 'baselineTest30', 'baselineTest40', 'baselineTest50'], [40,80,120,160,200], [[30,39], [60,79], [90,119], [120,159], [150,199]], 'VoIP', ['r', 'g', 'y', 'b', 'c'])

# plotMeanTPScdfDirectionSingleApp(['baselineTest10', 'baselineTest20', 'baselineTest30', 'baselineTest40', 'baselineTest50'], [40,80,120,160,200], [[0,9], [0,19], [0,29], [0,39], [0,49]], 'FileDownload', downlink, ['r', 'g', 'y', 'b', 'c'], 400)
# plotMeanTPScdfDirectionSingleApp(['baselineTest10', 'baselineTest20', 'baselineTest30', 'baselineTest40', 'baselineTest50'], [40,80,120,160,200], [[10,19], [20,39], [30,59], [40,79], [50,99]], 'Video', downlink, ['r', 'g', 'y', 'b', 'c'], 400)
# plotMeanTPScdfDirectionSingleApp(['baselineTest10', 'baselineTest20', 'baselineTest30', 'baselineTest40', 'baselineTest50'], [40,80,120,160,200], [[20,29], [40,59], [60,89], [80,119], [100,149]], 'SSH', downlink, ['r', 'g', 'y', 'b', 'c'], 400)
# plotMeanTPScdfDirectionSingleApp(['baselineTest10', 'baselineTest20', 'baselineTest30', 'baselineTest40', 'baselineTest50'], [40,80,120,160,200], [[30,39], [60,79], [90,119], [120,159], [150,199]], 'VoIP', downlink, ['r', 'g', 'y', 'b', 'c'], 400)

# plotMeanTPScdfDirectionSingleApp(['baselineTest10', 'baselineTest20', 'baselineTest30', 'baselineTest40', 'baselineTest50'], [40,80,120,160,200], [[0,9], [0,19], [0,29], [0,39], [0,49]], 'FileDownload', uplink, ['r', 'g', 'y', 'b', 'c'], 400)
# plotMeanTPScdfDirectionSingleApp(['baselineTest10', 'baselineTest20', 'baselineTest30', 'baselineTest40', 'baselineTest50'], [40,80,120,160,200], [[10,19], [20,39], [30,59], [40,79], [50,99]], 'Video', uplink, ['r', 'g', 'y', 'b', 'c'], 400)
# plotMeanTPScdfDirectionSingleApp(['baselineTest10', 'baselineTest20', 'baselineTest30', 'baselineTest40', 'baselineTest50'], [40,80,120,160,200], [[20,29], [40,59], [60,89], [80,119], [100,149]], 'SSH', uplink, ['r', 'g', 'y', 'b', 'c'], 400)

# plotTPScdfDirectionSingleApp(['baselineTest10', 'baselineTest20', 'baselineTest30', 'baselineTest40', 'baselineTest50'], [40,80,120,160,200], [[0,9], [0,19], [0,29], [0,39], [0,49]], 'FileDownload', downlink, ['r', 'g', 'y', 'b', 'c'], 400)
# plotTPScdfDirectionSingleApp(['baselineTest10', 'baselineTest20', 'baselineTest30', 'baselineTest40', 'baselineTest50'], [40,80,120,160,200], [[10,19], [20,39], [30,59], [40,79], [50,99]], 'Video', downlink, ['r', 'g', 'y', 'b', 'c'], 400)
# plotTPScdfDirectionSingleApp(['baselineTest10', 'baselineTest20', 'baselineTest30', 'baselineTest40', 'baselineTest50'], [40,80,120,160,200], [[20,29], [40,59], [60,89], [80,119], [100,149]], 'SSH', downlink, ['r', 'g', 'y', 'b', 'c'], 400)
# plotTPScdfDirectionSingleApp(['baselineTest10', 'baselineTest20', 'baselineTest30', 'baselineTest40', 'baselineTest50'], [40,80,120,160,200], [[30,39], [60,79], [90,119], [120,159], [150,199]], 'VoIP', downlink, ['r', 'g', 'y', 'b', 'c'], 400)

# plotTPScdfDirectionSingleApp(['baselineTest10', 'baselineTest20', 'baselineTest30', 'baselineTest40', 'baselineTest50'], [40,80,120,160,200], [[0,9], [0,19], [0,29], [0,39], [0,49]], 'FileDownload', uplink, ['r', 'g', 'y', 'b', 'c'], 400)
# plotTPScdfDirectionSingleApp(['baselineTest10', 'baselineTest20', 'baselineTest30', 'baselineTest40', 'baselineTest50'], [40,80,120,160,200], [[10,19], [20,39], [30,59], [40,79], [50,99]], 'Video', uplink, ['r', 'g', 'y', 'b', 'c'], 400)
# plotTPScdfDirectionSingleApp(['baselineTest10', 'baselineTest20', 'baselineTest30', 'baselineTest40', 'baselineTest50'], [40,80,120,160,200], [[20,29], [40,59], [60,89], [80,119], [100,149]], 'SSH', uplink, ['r', 'g', 'y', 'b', 'c'], 400)

# plotTPdirectionSingleApp(['baselineTest10', 'baselineTest20', 'baselineTest30', 'baselineTest40', 'baselineTest50'], [40,80,120,160,200], [[0,9], [0,19], [0,29], [0,39], [0,49]], 'FileDownload', downlink)
# plotTPdirectionSingleApp(['baselineTest10', 'baselineTest20', 'baselineTest30', 'baselineTest40', 'baselineTest50'], [40,80,120,160,200], [[10,19], [20,39], [30,59], [40,79], [50,99]], 'Video', downlink)
# plotTPdirectionSingleApp(['baselineTest10', 'baselineTest20', 'baselineTest30', 'baselineTest40', 'baselineTest50'], [40,80,120,160,200], [[20,29], [40,59], [60,89], [80,119], [100,149]], 'SSH', downlink)
# plotTPdirectionSingleApp(['baselineTest10', 'baselineTest20', 'baselineTest30', 'baselineTest40', 'baselineTest50'], [40,80,120,160,200], [[30,39], [60,79], [90,119], [120,159], [150,199]], 'VoIP', downlink)

# plotRTTcdfSSHmultiTest(['baselineTest10', 'baselineTest20', 'baselineTest30', 'baselineTest40', 'baselineTest50'], [40,80,120,160,200], [[20,29], [40,59], [60,89], [80,119], [100,149]], ['r', 'g', 'y', 'b', 'c'])
plotSSHRTOcdfMultiTest(['baselineTest10', 'baselineTest20', 'baselineTest30', 'baselineTest40', 'baselineTest50'], [40,80,120,160,200], ['r', 'g', 'y', 'b', 'c'])
# plotE2EDcdfVoiP(['baselineTest10', 'baselineTest20', 'baselineTest30', 'baselineTest40', 'baselineTest50'], [40,80,120,160,200], [[30,39], [60,79], [90,119], [120,159], [150,199]], ['r', 'g', 'y', 'b', 'c'])
# plotPkLRcdfVoiP(['baselineTest10', 'baselineTest20', 'baselineTest30', 'baselineTest40', 'baselineTest50'], [40,80,120,160,200], [[30,39], [60,79], [90,119], [120,159], [150,199]], ['r', 'g', 'y', 'b', 'c'])

# plotMOScdfSingleAppMultiTest(['baselineTestSSHfd', 'baselineTestSSHfd', 'baselineTestSSHfd', 'baselineTestSSHfd', 'baselineTestSSHfd', 'baselineTestSSHfd'], [6,11,21,31,41,51], [[0,0], [0,0], [0,0], [0,0], [0,0], [0,0]], 'SSH', ['r', 'g', 'y', 'b', 'c', 'm'])
# plotRTTcdfSSHmultiTest(['baselineTestSSHfd', 'baselineTestSSHfd', 'baselineTestSSHfd', 'baselineTestSSHfd', 'baselineTestSSHfd', 'baselineTestSSHfd'], [6,11,21,31,41,51], [[0,0], [0,0], [0,0], [0,0], [0,0], [0,0]], ['r', 'g', 'y', 'b', 'c', 'm'])
# plotSSHRTOcdfMultiTest(['baselineTestSSHfd', 'baselineTestSSHfd', 'baselineTestSSHfd', 'baselineTestSSHfd', 'baselineTestSSHfd', 'baselineTestSSHfd'], [6,11,21,31,41,51], ['r', 'g', 'y', 'b', 'c', 'm'])

# plotMOScdfSingleAppMultiTest(['baselineTestSSHvid' for x in range(6)], [6,11,21,31,41,51], [[0,0], [0,0], [0,0], [0,0], [0,0], [0,0]], 'SSH', ['r', 'g', 'y', 'b', 'c', 'm'])
# plotRTTcdfSSHmultiTest(['baselineTestSSHvid' for x in range(6)], [6,11,21,31,41,51], [[0,0], [0,0], [0,0], [0,0], [0,0], [0,0]], ['r', 'g', 'y', 'b', 'c', 'm'])
# plotSSHRTOcdfMultiTest(['baselineTestSSHvid' for x in range(6)], [6,11,21,31,41,51], ['r', 'g', 'y', 'b', 'c', 'm'])

## NO VoIP TEST ##
# plotAll('baselineTestNoVoIP10', 30, [9,19,29], ['File Download', 'Video', 'SSH'], ['r', 'g', 'y'], 400)
# plotAll('baselineTestNoVoIP20', 60, [19,39,59], ['File Download', 'Video', 'SSH'], ['r', 'g', 'y'], 400)
# plotAll('baselineTestNoVoIP30', 90, [29,59,89], ['File Download', 'Video', 'SSH'], ['r', 'g', 'y'], 400)
# plotAll('baselineTestNoVoIP40', 120, [39,79,119], ['File Download', 'Video', 'SSH'], ['r', 'g', 'y'], 400)
# plotAll('baselineTestNoVoIP50', 150, [49,99,149], ['File Download', 'Video', 'SSH'], ['r', 'g', 'y'], 400)

# plotMOScdfSingleAppMultiTest(['baselineTestNoVoIP10', 'baselineTestNoVoIP20', 'baselineTestNoVoIP30', 'baselineTestNoVoIP40', 'baselineTestNoVoIP50'], [30,60,90,120,150], [[0,9], [0,19], [0,29], [0,39], [0,49]], 'FileDownload', ['r', 'g', 'y', 'b', 'c'])
# plotMOScdfSingleAppMultiTest(['baselineTestNoVoIP10', 'baselineTestNoVoIP20', 'baselineTestNoVoIP30', 'baselineTestNoVoIP40', 'baselineTestNoVoIP50'], [30,60,90,120,150], [[10,19], [20,39], [30,59], [40,79], [50,99]], 'Video', ['r', 'g', 'y', 'b', 'c'])
# plotMOScdfSingleAppMultiTest(['baselineTestNoVoIP10', 'baselineTestNoVoIP20', 'baselineTestNoVoIP30', 'baselineTestNoVoIP40', 'baselineTestNoVoIP50'], [30,60,90,120,150], [[20,29], [40,59], [60,89], [80,119], [100,149]], 'SSH', ['r', 'g', 'y', 'b', 'c'])

# plotMeanTPScdfDirectionSingleApp(['baselineTestNoVoIP10', 'baselineTestNoVoIP20', 'baselineTestNoVoIP30', 'baselineTestNoVoIP40', 'baselineTestNoVoIP50'], [30,60,90,120,150], [[0,9], [0,19], [0,29], [0,39], [0,49]], 'FileDownload', downlink, ['r', 'g', 'y', 'b', 'c'], 400)
# plotMeanTPScdfDirectionSingleApp(['baselineTestNoVoIP10', 'baselineTestNoVoIP20', 'baselineTestNoVoIP30', 'baselineTestNoVoIP40', 'baselineTestNoVoIP50'], [30,60,90,120,150], [[10,19], [20,39], [30,59], [40,79], [50,99]], 'Video', downlink, ['r', 'g', 'y', 'b', 'c'], 400)
# plotMeanTPScdfDirectionSingleApp(['baselineTestNoVoIP10', 'baselineTestNoVoIP20', 'baselineTestNoVoIP30', 'baselineTestNoVoIP40', 'baselineTestNoVoIP50'], [30,60,90,120,150], [[20,29], [40,59], [60,89], [80,119], [100,149]], 'SSH', downlink, ['r', 'g', 'y', 'b', 'c'], 400)

# plotMeanTPScdfDirectionSingleApp(['baselineTestNoVoIP10', 'baselineTestNoVoIP20', 'baselineTestNoVoIP30', 'baselineTestNoVoIP40', 'baselineTestNoVoIP50'], [30,60,90,120,150], [[0,9], [0,19], [0,29], [0,39], [0,49]], 'FileDownload', uplink, ['r', 'g', 'y', 'b', 'c'], 400)
# plotMeanTPScdfDirectionSingleApp(['baselineTestNoVoIP10', 'baselineTestNoVoIP20', 'baselineTestNoVoIP30', 'baselineTestNoVoIP40', 'baselineTestNoVoIP50'], [30,60,90,120,150], [[10,19], [20,39], [30,59], [40,79], [50,99]], 'Video', uplink, ['r', 'g', 'y', 'b', 'c'], 400)
# plotMeanTPScdfDirectionSingleApp(['baselineTestNoVoIP10', 'baselineTestNoVoIP20', 'baselineTestNoVoIP30', 'baselineTestNoVoIP40', 'baselineTestNoVoIP50'], [30,60,90,120,150], [[20,29], [40,59], [60,89], [80,119], [100,149]], 'SSH', uplink, ['r', 'g', 'y', 'b', 'c'], 400)

# plotTPScdfDirectionSingleApp(['baselineTestNoVoIP10', 'baselineTestNoVoIP20', 'baselineTestNoVoIP30', 'baselineTestNoVoIP40', 'baselineTestNoVoIP50'], [30,60,90,120,150], [[0,9], [0,19], [0,29], [0,39], [0,49]], 'FileDownload', downlink, ['r', 'g', 'y', 'b', 'c'], 400)
# plotTPScdfDirectionSingleApp(['baselineTestNoVoIP10', 'baselineTestNoVoIP20', 'baselineTestNoVoIP30', 'baselineTestNoVoIP40', 'baselineTestNoVoIP50'], [30,60,90,120,150], [[10,19], [20,39], [30,59], [40,79], [50,99]], 'Video', downlink, ['r', 'g', 'y', 'b', 'c'], 400)
# plotTPScdfDirectionSingleApp(['baselineTestNoVoIP10', 'baselineTestNoVoIP20', 'baselineTestNoVoIP30', 'baselineTestNoVoIP40', 'baselineTestNoVoIP50'], [30,60,90,120,150], [[20,29], [40,59], [60,89], [80,119], [100,149]], 'SSH', downlink, ['r', 'g', 'y', 'b', 'c'], 400)

# plotTPScdfDirectionSingleApp(['baselineTestNoVoIP10', 'baselineTestNoVoIP20', 'baselineTestNoVoIP30', 'baselineTestNoVoIP40', 'baselineTestNoVoIP50'], [30,60,90,120,150], [[0,9], [0,19], [0,29], [0,39], [0,49]], 'FileDownload', uplink, ['r', 'g', 'y', 'b', 'c'], 400)
# plotTPScdfDirectionSingleApp(['baselineTestNoVoIP10', 'baselineTestNoVoIP20', 'baselineTestNoVoIP30', 'baselineTestNoVoIP40', 'baselineTestNoVoIP50'], [30,60,90,120,150], [[10,19], [20,39], [30,59], [40,79], [50,99]], 'Video', uplink, ['r', 'g', 'y', 'b', 'c'], 400)
# plotTPScdfDirectionSingleApp(['baselineTestNoVoIP10', 'baselineTestNoVoIP20', 'baselineTestNoVoIP30', 'baselineTestNoVoIP40', 'baselineTestNoVoIP50'], [30,60,90,120,150], [[20,29], [40,59], [60,89], [80,119], [100,149]], 'SSH', uplink, ['r', 'g', 'y', 'b', 'c'], 400)

# plotTPdirectionSingleApp(['baselineTestNoVoIP10', 'baselineTestNoVoIP20', 'baselineTestNoVoIP30', 'baselineTestNoVoIP40', 'baselineTestNoVoIP50'], [30,60,90,120,150], [[0,9], [0,19], [0,29], [0,39], [0,49]], 'FileDownload', downlink)
# plotTPdirectionSingleApp(['baselineTestNoVoIP10', 'baselineTestNoVoIP20', 'baselineTestNoVoIP30', 'baselineTestNoVoIP40', 'baselineTestNoVoIP50'], [30,60,90,120,150], [[10,19], [20,39], [30,59], [40,79], [50,99]], 'Video', downlink)
# plotTPdirectionSingleApp(['baselineTestNoVoIP10', 'baselineTestNoVoIP20', 'baselineTestNoVoIP30', 'baselineTestNoVoIP40', 'baselineTestNoVoIP50'], [30,60,90,120,150], [[20,29], [40,59], [60,89], [80,119], [100,149]], 'SSH', downlink)

# plotRTTcdfSSHmultiTest(['baselineTestNoVoIP10', 'baselineTestNoVoIP20', 'baselineTestNoVoIP30', 'baselineTestNoVoIP40', 'baselineTestNoVoIP50'], [30,60,90,120,150], [[20,29], [40,59], [60,89], [80,119], [100,149]], ['r', 'g', 'y', 'b', 'c'])
# plotSSHRTOcdfMultiTest(['baselineTestNoVoIP10', 'baselineTestNoVoIP20', 'baselineTestNoVoIP30', 'baselineTestNoVoIP40', 'baselineTestNoVoIP50'], [30,60,90,120,150], ['r', 'g', 'y', 'b', 'c'])

## NO SSH TEST ##
# plotAll('baselineTestNoSSH10', 30, [9,19,29], ['File Download', 'Video', 'VoIP'], ['r', 'g', 'b'], 400)
# plotAll('baselineTestNoSSH20', 60, [19,39,59], ['File Download', 'Video', 'VoIP'], ['r', 'g', 'b'], 400)
# plotAll('baselineTestNoSSH30', 90, [29,59,89], ['File Download', 'Video', 'VoIP'], ['r', 'g', 'b'], 400)
# plotAll('baselineTestNoSSH40', 120, [39,79,119], ['File Download', 'Video', 'VoIP'], ['r', 'g', 'b'], 400)
# plotAll('baselineTestNoSSH50', 150, [49,99,149], ['File Download', 'Video', 'VoIP'], ['r', 'g', 'b'], 400)

# plotMOScdfSingleAppMultiTest(['baselineTestNoSSH10', 'baselineTestNoSSH20', 'baselineTestNoSSH30', 'baselineTestNoSSH40', 'baselineTestNoSSH50'], [30,60,90,120,150], [[0,9], [0,19], [0,29], [0,39], [0,49]], 'FileDownload', ['r', 'g', 'y', 'b', 'c'])
# plotMOScdfSingleAppMultiTest(['baselineTestNoSSH10', 'baselineTestNoSSH20', 'baselineTestNoSSH30', 'baselineTestNoSSH40', 'baselineTestNoSSH50'], [30,60,90,120,150], [[10,19], [20,39], [30,59], [40,79], [50,99]], 'Video', ['r', 'g', 'y', 'b', 'c'])
# plotMOScdfSingleAppMultiTest(['baselineTestNoSSH10', 'baselineTestNoSSH20', 'baselineTestNoSSH30', 'baselineTestNoSSH40', 'baselineTestNoSSH50'], [30,60,90,120,150], [[20,29], [40,59], [60,89], [80,119], [100,149]], 'VoIP', ['r', 'g', 'y', 'b', 'c'])

# plotMeanTPScdfDirectionSingleApp(['baselineTestNoSSH10', 'baselineTestNoSSH20', 'baselineTestNoSSH30', 'baselineTestNoSSH40', 'baselineTestNoSSH50'], [30,60,90,120,150], [[0,9], [0,19], [0,29], [0,39], [0,49]], 'FileDownload', downlink, ['r', 'g', 'y', 'b', 'c'], 400)
# plotMeanTPScdfDirectionSingleApp(['baselineTestNoSSH10', 'baselineTestNoSSH20', 'baselineTestNoSSH30', 'baselineTestNoSSH40', 'baselineTestNoSSH50'], [30,60,90,120,150], [[10,19], [20,39], [30,59], [40,79], [50,99]], 'Video', downlink, ['r', 'g', 'y', 'b', 'c'], 400)
# plotMeanTPScdfDirectionSingleApp(['baselineTestNoSSH10', 'baselineTestNoSSH20', 'baselineTestNoSSH30', 'baselineTestNoSSH40', 'baselineTestNoSSH50'], [30,60,90,120,150], [[20,29], [40,59], [60,89], [80,119], [100,149]], 'VoIP', downlink, ['r', 'g', 'y', 'b', 'c'], 400)

# plotMeanTPScdfDirectionSingleApp(['baselineTestNoSSH10', 'baselineTestNoSSH20', 'baselineTestNoSSH30', 'baselineTestNoSSH40', 'baselineTestNoSSH50'], [30,60,90,120,150], [[0,9], [0,19], [0,29], [0,39], [0,49]], 'FileDownload', uplink, ['r', 'g', 'y', 'b', 'c'], 400)
# plotMeanTPScdfDirectionSingleApp(['baselineTestNoSSH10', 'baselineTestNoSSH20', 'baselineTestNoSSH30', 'baselineTestNoSSH40', 'baselineTestNoSSH50'], [30,60,90,120,150], [[10,19], [20,39], [30,59], [40,79], [50,99]], 'Video', uplink, ['r', 'g', 'y', 'b', 'c'], 400)
# plotMeanTPScdfDirectionSingleApp(['baselineTestNoSSH10', 'baselineTestNoSSH20', 'baselineTestNoSSH30', 'baselineTestNoSSH40', 'baselineTestNoSSH50'], [30,60,90,120,150], [[20,29], [40,59], [60,89], [80,119], [100,149]], 'VoIP', uplink, ['r', 'g', 'y', 'b', 'c'], 400)

# plotTPScdfDirectionSingleApp(['baselineTestNoSSH10', 'baselineTestNoSSH20', 'baselineTestNoSSH30', 'baselineTestNoSSH40', 'baselineTestNoSSH50'], [30,60,90,120,150], [[0,9], [0,19], [0,29], [0,39], [0,49]], 'FileDownload', downlink, ['r', 'g', 'y', 'b', 'c'], 400)
# plotTPScdfDirectionSingleApp(['baselineTestNoSSH10', 'baselineTestNoSSH20', 'baselineTestNoSSH30', 'baselineTestNoSSH40', 'baselineTestNoSSH50'], [30,60,90,120,150], [[10,19], [20,39], [30,59], [40,79], [50,99]], 'Video', downlink, ['r', 'g', 'y', 'b', 'c'], 400)
# plotTPScdfDirectionSingleApp(['baselineTestNoSSH10', 'baselineTestNoSSH20', 'baselineTestNoSSH30', 'baselineTestNoSSH40', 'baselineTestNoSSH50'], [30,60,90,120,150], [[20,29], [40,59], [60,89], [80,119], [100,149]], 'VoIP', downlink, ['r', 'g', 'y', 'b', 'c'], 400)

# plotTPScdfDirectionSingleApp(['baselineTestNoSSH10', 'baselineTestNoSSH20', 'baselineTestNoSSH30', 'baselineTestNoSSH40', 'baselineTestNoSSH50'], [30,60,90,120,150], [[0,9], [0,19], [0,29], [0,39], [0,49]], 'FileDownload', uplink, ['r', 'g', 'y', 'b', 'c'], 400)
# plotTPScdfDirectionSingleApp(['baselineTestNoSSH10', 'baselineTestNoSSH20', 'baselineTestNoSSH30', 'baselineTestNoSSH40', 'baselineTestNoSSH50'], [30,60,90,120,150], [[10,19], [20,39], [30,59], [40,79], [50,99]], 'Video', uplink, ['r', 'g', 'y', 'b', 'c'], 400)
# plotTPScdfDirectionSingleApp(['baselineTestNoSSH10', 'baselineTestNoSSH20', 'baselineTestNoSSH30', 'baselineTestNoSSH40', 'baselineTestNoSSH50'], [30,60,90,120,150], [[20,29], [40,59], [60,89], [80,119], [100,149]], 'VoIP', uplink, ['r', 'g', 'y', 'b', 'c'], 400)

# plotTPdirectionSingleApp(['baselineTestNoSSH10', 'baselineTestNoSSH20', 'baselineTestNoSSH30', 'baselineTestNoSSH40', 'baselineTestNoSSH50'], [30,60,90,120,150], [[0,9], [0,19], [0,29], [0,39], [0,49]], 'FileDownload', downlink)
# plotTPdirectionSingleApp(['baselineTestNoSSH10', 'baselineTestNoSSH20', 'baselineTestNoSSH30', 'baselineTestNoSSH40', 'baselineTestNoSSH50'], [30,60,90,120,150], [[10,19], [20,39], [30,59], [40,79], [50,99]], 'Video', downlink)
# plotTPdirectionSingleApp(['baselineTestNoSSH10', 'baselineTestNoSSH20', 'baselineTestNoSSH30', 'baselineTestNoSSH40', 'baselineTestNoSSH50'], [30,60,90,120,150], [[20,29], [40,59], [60,89], [80,119], [100,149]], 'VoIP', downlink)

# plotPkLRcdfVoiP(['baselineTestNoSSH10', 'baselineTestNoSSH20', 'baselineTestNoSSH30', 'baselineTestNoSSH40', 'baselineTestNoSSH50'], [30,60,90,120,150], [[20,29], [40,59], [60,89], [80,119], [100,149]], ['r', 'g', 'y', 'b', 'c'])
# plotE2EDcdfVoiP(['baselineTestNoSSH10', 'baselineTestNoSSH20', 'baselineTestNoSSH30', 'baselineTestNoSSH40', 'baselineTestNoSSH50'], [30,60,90,120,150], [[20,29], [40,59], [60,89], [80,119], [100,149]], ['r', 'g', 'y', 'b', 'c'])
