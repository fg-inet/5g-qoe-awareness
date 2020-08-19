import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import csv
import math
import statistics
from scipy import stats
import scipy
from sklearn.linear_model import LogisticRegression
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

def plotE2edVsTP(testName, numCLIs, nodeTypes, nodeSplit):
    meanTPValues = []
    meanE2edValues = []
    file_to_read = '../exports/extracted/throughput' + downlink[0] + '/' + makeFullScenarioName(testName, numCLIs, nodeTypes, nodeSplit) + '.csv'
    with open(file_to_read, mode='r') as readFile:
        csv_reader = csv.reader(readFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
        line_count = 0
        for row in csv_reader:
            if line_count == 1:
                meanTPValues = row
                break
            line_count += 1

    file_to_read = '../exports/extracted/endToEndDelay/' + makeFullScenarioName(testName, numCLIs, nodeTypes, nodeSplit) + '.csv'
    with open(file_to_read, mode='r') as readFile:
        csv_reader = csv.reader(readFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
        line_count = 0
        for row in csv_reader:
            if line_count == 1:
                meanE2edValues = row
                break
            line_count += 1 
    
    fig, ax1 = plt.subplots(1, figsize=(16,12))
    ax1.plot(meanTPValues, meanE2edValues, 'o-')
    plt.xlabel('Mean Downlink Throughput [kbps]')
    plt.ylabel('Mean End To End Delay [s]')

    prePath = '../exports/plots/' + makeFullScenarioName(testName, numCLIs, nodeTypes, nodeSplit) + '/'
    if not os.path.exists(prePath):
        os.makedirs(prePath)
    outPath = prePath + 'delayVsTP.pdf'
    fig.savefig(outPath, dpi=100, bbox_inches='tight')
    outPath2 = prePath + 'delayVsTP.png'
    fig.savefig(outPath2, dpi=100, bbox_inches='tight', format='png')
    plt.close('all')

# plotE2edVsTP('singleAppStressTest_VoIP', [1,5,10,15,20,25,30,35,40,45,50,55,60], ['hostVID', 'hostFDO', 'hostSSH', 'hostVIP'], [0,0,0,60])
# plotE2edVsTP('singleAppStressTest_SSH', [10,20,30,40,50,60,70,80,90,100,110,120,130,140,150,160,170,180,190,200,210,220,230,240,250,260,270,280,290,300], ['hostVID', 'hostFDO', 'hostSSH', 'hostVIP'], [0,0,300,0])
# plotE2edVsTP('singleAppStressTest_NewLiveVideoClient', [1,5,10,15,20,25,30,35,40,45,50,55,60,65,70,75,80,85,90,95,100,105,110,115,120,125,130,135,140,145,150], ['hostVID', 'hostFDO', 'hostSSH', 'hostVIP'], [150,0,0,0])
# plotE2edVsTP('singleAppStressTest_VoIP_oneTenth', [x for x in range(1,16)], ['hostVID', 'hostFDO', 'hostSSH', 'hostVIP'], [0,0,0,15])

def makeEquationString(popt):
    return 'Fit: y = ' + '{:.4e}'.format(popt[0]) + ' * exp(' + '{:.4e}'.format(popt[1]) + ' * x) + ' + '{:.4e}'.format(popt[2]) 

def expFunc(x, a, b, c):
    return a * np.exp(b*x) + c

def plotE2edVsUtilizationExp(testName, numCLIs, nodeTypes, nodeSplit, linkBitrate, pZero):
    meanTPValues = []
    meanE2edValues = []
    stdDevValues = []
    ci95hValues = []
    minValues = []
    maxValues = []
    file_to_read = '../exports/extracted/throughput' + downlink[0] + '/' + makeFullScenarioName(testName, numCLIs, nodeTypes, nodeSplit) + '.csv'
    with open(file_to_read, mode='r') as readFile:
        csv_reader = csv.reader(readFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
        line_count = 0
        for row in csv_reader:
            if line_count == 1:
                meanTPValues = row
                break
            line_count += 1

    file_to_read = '../exports/extracted/endToEndDelay/' + makeFullScenarioName(testName, numCLIs, nodeTypes, nodeSplit) + '.csv'
    with open(file_to_read, mode='r') as readFile:
        csv_reader = csv.reader(readFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
        line_count = 0
        for row in csv_reader:
            if line_count == 1:
                meanE2edValues = row
            elif line_count == 2:
                stdDevValues = row
            elif line_count == 3:
                ci95hValues = row
            elif line_count == 4:
                minValues = row
            elif line_count == 5:
                maxValues = row
                break
            line_count += 1 
    
    meanUtilValues = [round((x/linkBitrate)*100,3) for x in meanTPValues]

    x = np.array([a for a,_ in sorted(zip(meanUtilValues, meanE2edValues))])
    y = np.array([round(b*1000,3) for _,b in sorted(zip(meanUtilValues, meanE2edValues))])
    sortedstdDevValues = [round(b*1000,6) for _,b in sorted(zip(meanUtilValues, stdDevValues))]
    sortedci95hValues = [round(b*1000,6) for _,b in sorted(zip(meanUtilValues, ci95hValues))]
    sortedminValues = [round(b*1000,6) for _,b in sorted(zip(meanUtilValues, minValues))]
    sortedmaxValues = [round(b*1000,6) for _,b in sorted(zip(meanUtilValues, maxValues))]

    print(sortedstdDevValues)
    print(sortedci95hValues)

    fig, ax1 = plt.subplots(1, figsize=(16,12))
    ax1.errorbar(x, y, yerr=sortedci95hValues, fmt='-', ecolor='red', label='Measured Data')
    ax1.fill_between(x, sortedminValues, sortedmaxValues, facecolor='grey', alpha=0.2, label='Delay Range')
    plt.xlabel('Mean Link Utilization [%]')
    plt.ylabel('Mean End To End Delay [ms]')

    popt, pcov = scipy.optimize.curve_fit(expFunc, x, y, p0=pZero, maxfev=1000000, bounds=(0,np.inf))
    with np.printoptions(precision=2):
        print(testName + ' with ' + str(nodeSplit) + ': ' + str(popt))
        # regLine = np.linspace(0, max(meanUtilValues), 100)
        regLine = np.linspace(0, 100, 100)
        theLabel = 'Exponential Fit'
        ax1.plot(regLine, expFunc(regLine, *popt), '-', label=theLabel, color='orange')
    plt.legend()

    ax1.set_ylim(0,1.3*max(expFunc(regLine[-1], *popt), max(y)))

    textstr = makeEquationString(popt) + '\n'
    textstr += 'MSE: ' + str(np.mean((y-expFunc(x, *popt))**2)) + '\n'
    ss_res = np.dot((y - expFunc(x, *popt)),(y - expFunc(x, *popt)))
    ymean = np.mean(y)
    ss_tot = np.dot((y-ymean),(y-ymean))
    textstr += 'R2: ' + str(1-ss_res/ss_tot)
    props = dict(boxstyle='round', facecolor='white', alpha=0.2)
    ax1.text(0.03, 0.64, textstr, transform=ax1.transAxes, fontsize=22, verticalalignment='top', bbox=props)

    prePath = '../exports/plots/' + makeFullScenarioName(testName, numCLIs, nodeTypes, nodeSplit) + '/'
    if not os.path.exists(prePath):
        os.makedirs(prePath)
    outPath = prePath + 'delayVsUtilization.pdf'
    fig.savefig(outPath, dpi=100, bbox_inches='tight')
    outPath2 = prePath + 'delayVsUtilization.png'
    fig.savefig(outPath2, dpi=100, bbox_inches='tight', format='png')
    plt.close('all')

def plotRttVsUtilizationExp(testName, numCLIs, nodeTypes, nodeSplit, linkBitrate, pZero):
    meanTPValues = []
    meanE2edValues = []
    stdDevValues = []
    ci95hValues = []
    minValues = []
    maxValues = []
    file_to_read = '../exports/extracted/throughput' + downlink[0] + '/' + makeFullScenarioName(testName, numCLIs, nodeTypes, nodeSplit) + '.csv'
    with open(file_to_read, mode='r') as readFile:
        csv_reader = csv.reader(readFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
        line_count = 0
        for row in csv_reader:
            if line_count == 1:
                meanTPValues = row
                break
            line_count += 1

    file_to_read = '../exports/extracted/rtt/' + makeFullScenarioName(testName, numCLIs, nodeTypes, nodeSplit) + '.csv'
    with open(file_to_read, mode='r') as readFile:
        csv_reader = csv.reader(readFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
        line_count = 0
        for row in csv_reader:
            if line_count == 1:
                meanE2edValues = row
            elif line_count == 2:
                stdDevValues = row
            elif line_count == 3:
                ci95hValues = row
            elif line_count == 4:
                minValues = row
            elif line_count == 5:
                maxValues = row
                break
            line_count += 1 
    
    meanUtilValues = [round((x/linkBitrate)*100,3) for x in meanTPValues]

    x = np.array([a for a,_ in sorted(zip(meanUtilValues, meanE2edValues))])
    y = np.array([round(b*1000,3) for _,b in sorted(zip(meanUtilValues, meanE2edValues))])
    sortedstdDevValues = [round(b*1000,6) for _,b in sorted(zip(meanUtilValues, stdDevValues))]
    sortedci95hValues = [round(b*1000,6) for _,b in sorted(zip(meanUtilValues, ci95hValues))]
    sortedminValues = [round(b*1000,6) for _,b in sorted(zip(meanUtilValues, minValues))]
    sortedmaxValues = [round(b*1000,6) for _,b in sorted(zip(meanUtilValues, maxValues))]

    print(sortedstdDevValues)
    print(sortedci95hValues)

    fig, ax1 = plt.subplots(1, figsize=(16,12))
    ax1.errorbar(x, y, yerr=sortedci95hValues, fmt='-', ecolor='red', label='Measured Data')
    ax1.fill_between(x, sortedminValues, sortedmaxValues, facecolor='grey', alpha=0.2, label='Delay Range')
    plt.xlabel('Mean Link Utilization [%]')
    plt.ylabel('Mean RTT [ms]')

    popt, pcov = scipy.optimize.curve_fit(expFunc, x, y, p0=pZero, maxfev=1000000, bounds=(0,np.inf))
    with np.printoptions(precision=2):
        print(testName + ' with ' + str(nodeSplit) + ': ' + str(popt))
        # regLine = np.linspace(0, max(meanUtilValues), 100)
        regLine = np.linspace(0, 100, 100)
        theLabel = 'Exponential Fit'
        ax1.plot(regLine, expFunc(regLine, *popt), '-', label=theLabel, color='orange')
    plt.legend()

    ax1.set_ylim(0,1.3*max(expFunc(regLine[-1], *popt), max(y)))

    textstr = makeEquationString(popt) + '\n'
    textstr += 'MSE: ' + str(np.mean((y-expFunc(x, *popt))**2)) + '\n'
    ss_res = np.dot((y - expFunc(x, *popt)),(y - expFunc(x, *popt)))
    ymean = np.mean(y)
    ss_tot = np.dot((y-ymean),(y-ymean))
    textstr += 'R2: ' + str(1-ss_res/ss_tot)
    props = dict(boxstyle='round', facecolor='white', alpha=0.2)
    ax1.text(0.03, 0.64, textstr, transform=ax1.transAxes, fontsize=22, verticalalignment='top', bbox=props)

    prePath = '../exports/plots/' + makeFullScenarioName(testName, numCLIs, nodeTypes, nodeSplit) + '/'
    if not os.path.exists(prePath):
        os.makedirs(prePath)
    outPath = prePath + 'rttVsUtilization.pdf'
    fig.savefig(outPath, dpi=100, bbox_inches='tight')
    outPath2 = prePath + 'rttVsUtilization.png'
    fig.savefig(outPath2, dpi=100, bbox_inches='tight', format='png')
    plt.close('all')

def plotE2edJitterVsUtilizationExp(testName, numCLIs, nodeTypes, nodeSplit, linkBitrate, pZero):
    meanTPValues = []
    meanE2edValues = []
    file_to_read = '../exports/extracted/throughput' + downlink[0] + '/' + makeFullScenarioName(testName, numCLIs, nodeTypes, nodeSplit) + '.csv'
    with open(file_to_read, mode='r') as readFile:
        csv_reader = csv.reader(readFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
        line_count = 0
        for row in csv_reader:
            if line_count == 1:
                meanTPValues = row
                break
            line_count += 1

    file_to_read = '../exports/extracted/endToEndDelayJitter/' + makeFullScenarioName(testName, numCLIs, nodeTypes, nodeSplit) + '.csv'
    with open(file_to_read, mode='r') as readFile:
        csv_reader = csv.reader(readFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
        line_count = 0
        for row in csv_reader:
            if line_count == 1:
                meanE2edValues = row
                break
            line_count += 1 
    
    meanUtilValues = [round((x/linkBitrate)*100,3) for x in meanTPValues]

    x = np.array([a for a,_ in sorted(zip(meanUtilValues, meanE2edValues))])
    y = np.array([round(b*1000,3) for _,b in sorted(zip(meanUtilValues, meanE2edValues))])

    fig, ax1 = plt.subplots(1, figsize=(16,12))
    ax1.plot(x, y, 'o-', label='Measured Data')
    plt.xlabel('Mean Link Utilization [%]')
    plt.ylabel('End To End Delay Jitter [ms]')

    popt, pcov = scipy.optimize.curve_fit(expFunc, x, y, p0=pZero, maxfev=1000000, bounds=(0,np.inf))
    with np.printoptions(precision=2):
        print(testName + ' with ' + str(nodeSplit) + ': ' + str(popt))
        # regLine = np.linspace(0, max(meanUtilValues), 100)
        regLine = np.linspace(0, 100, 100)
        theLabel = 'Exponential Fit'
        ax1.plot(regLine, expFunc(regLine, *popt), '-', label=theLabel)
    plt.legend()

    textstr = makeEquationString(popt) + '\n'
    textstr += 'MSE: ' + str(np.mean((y-expFunc(x, *popt))**2)) + '\n'
    ss_res = np.dot((y - expFunc(x, *popt)),(y - expFunc(x, *popt)))
    ymean = np.mean(y)
    ss_tot = np.dot((y-ymean),(y-ymean))
    textstr += 'R2: ' + str(1-ss_res/ss_tot)
    props = dict(boxstyle='round', facecolor='white', alpha=0.2)
    ax1.text(0.03, 0.74, textstr, transform=ax1.transAxes, fontsize=22, verticalalignment='top', bbox=props)

    prePath = '../exports/plots/' + makeFullScenarioName(testName, numCLIs, nodeTypes, nodeSplit) + '/'
    if not os.path.exists(prePath):
        os.makedirs(prePath)
    outPath = prePath + 'delayJitterVsUtilization.pdf'
    fig.savefig(outPath, dpi=100, bbox_inches='tight')
    outPath2 = prePath + 'delayJitterVsUtilization.png'
    fig.savefig(outPath2, dpi=100, bbox_inches='tight', format='png')
    plt.close('all')

def plotRttJitterVsUtilizationExp(testName, numCLIs, nodeTypes, nodeSplit, linkBitrate, pZero):
    meanTPValues = []
    meanE2edValues = []
    file_to_read = '../exports/extracted/throughput' + downlink[0] + '/' + makeFullScenarioName(testName, numCLIs, nodeTypes, nodeSplit) + '.csv'
    with open(file_to_read, mode='r') as readFile:
        csv_reader = csv.reader(readFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
        line_count = 0
        for row in csv_reader:
            if line_count == 1:
                meanTPValues = row
                break
            line_count += 1

    file_to_read = '../exports/extracted/rttJitter/' + makeFullScenarioName(testName, numCLIs, nodeTypes, nodeSplit) + '.csv'
    with open(file_to_read, mode='r') as readFile:
        csv_reader = csv.reader(readFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
        line_count = 0
        for row in csv_reader:
            if line_count == 1:
                meanE2edValues = row
                break
            line_count += 1 
    
    meanUtilValues = [round((x/linkBitrate)*100,3) for x in meanTPValues]

    x = np.array([a for a,_ in sorted(zip(meanUtilValues, meanE2edValues))])
    y = np.array([round(b*1000,3) for _,b in sorted(zip(meanUtilValues, meanE2edValues))])

    fig, ax1 = plt.subplots(1, figsize=(16,12))
    ax1.plot(x, y, 'o-', label='Measured Data')
    plt.xlabel('Mean Link Utilization [%]')
    plt.ylabel('RTT Jitter [ms]')

    popt, pcov = scipy.optimize.curve_fit(expFunc, x, y, p0=pZero, maxfev=1000000, bounds=(0,np.inf))
    with np.printoptions(precision=2):
        print(testName + ' with ' + str(nodeSplit) + ': ' + str(popt))
        # regLine = np.linspace(0, max(meanUtilValues), 100)
        regLine = np.linspace(0, 100, 100)
        theLabel = 'Exponential Fit'
        ax1.plot(regLine, expFunc(regLine, *popt), '-', label=theLabel)
    plt.legend()

    textstr = makeEquationString(popt) + '\n'
    textstr += 'MSE: ' + str(np.mean((y-expFunc(x, *popt))**2)) + '\n'
    ss_res = np.dot((y - expFunc(x, *popt)),(y - expFunc(x, *popt)))
    ymean = np.mean(y)
    ss_tot = np.dot((y-ymean),(y-ymean))
    textstr += 'R2: ' + str(1-ss_res/ss_tot)
    props = dict(boxstyle='round', facecolor='white', alpha=0.2)
    ax1.text(0.03, 0.74, textstr, transform=ax1.transAxes, fontsize=22, verticalalignment='top', bbox=props)

    prePath = '../exports/plots/' + makeFullScenarioName(testName, numCLIs, nodeTypes, nodeSplit) + '/'
    if not os.path.exists(prePath):
        os.makedirs(prePath)
    outPath = prePath + 'rttJitterVsUtilization.pdf'
    fig.savefig(outPath, dpi=100, bbox_inches='tight')
    outPath2 = prePath + 'rttJitterVsUtilization.png'
    fig.savefig(outPath2, dpi=100, bbox_inches='tight', format='png')
    plt.close('all')

def plotPacketLossVsUtilizationExp(testName, numCLIs, nodeTypes, nodeSplit, linkBitrate, pZero):
    meanTPValues = []
    meanPacketLossValues = []
    file_to_read = '../exports/extracted/throughput' + downlink[0] + '/' + makeFullScenarioName(testName, numCLIs, nodeTypes, nodeSplit) + '.csv'
    with open(file_to_read, mode='r') as readFile:
        csv_reader = csv.reader(readFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
        line_count = 0
        for row in csv_reader:
            if line_count == 1:
                meanTPValues = row
                break
            line_count += 1

    file_to_read = '../exports/extracted/packetLossRate/' + makeFullScenarioName(testName, numCLIs, nodeTypes, nodeSplit) + '.csv'
    with open(file_to_read, mode='r') as readFile:
        csv_reader = csv.reader(readFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
        line_count = 0
        for row in csv_reader:
            if line_count == 1:
                meanPacketLossValues = row
                break
            line_count += 1 
    
    meanUtilValues = [round((x/linkBitrate)*100,3) for x in meanTPValues]

    packetLossPerc = [x*100 for x in meanPacketLossValues]

    x = np.array([a for a,_ in sorted(zip(meanUtilValues, packetLossPerc))])
    y = np.array([round(b,3) for _,b in sorted(zip(meanUtilValues, packetLossPerc))])

    fig, ax1 = plt.subplots(1, figsize=(16,12))
    ax1.plot(x, y, 'o-', label='Measured Data')
    plt.xlabel('Mean Link Utilization [%]')
    plt.ylabel('Packet Loss [%]')
    print(len(x))
    print(len(y))
    popt, pcov = scipy.optimize.curve_fit(expFunc, x, y, p0=pZero, maxfev=1000000)
    with np.printoptions(precision=2):
        print(testName + ' with ' + str(nodeSplit) + ': ' + str(popt))
        # regLine = np.linspace(0, max(meanUtilValues), 100)
        regLine = np.linspace(0, 100, 100)
        theLabel = 'Exponential Fit'
        ax1.plot(regLine, expFunc(regLine, *popt), '-', label=theLabel)
    plt.legend()

    textstr = makeEquationString(popt) + '\n'
    textstr += 'MSE: ' + str(np.mean((y-expFunc(x, *popt))**2)) + '\n'
    ss_res = np.dot((y - expFunc(x, *popt)),(y - expFunc(x, *popt)))
    ymean = np.mean(y)
    ss_tot = np.dot((y-ymean),(y-ymean))
    textstr += 'R2: ' + str(1-ss_res/ss_tot)
    props = dict(boxstyle='round', facecolor='white', alpha=0.2)
    ax1.text(0.03, 0.74, textstr, transform=ax1.transAxes, fontsize=22, verticalalignment='top', bbox=props)

    prePath = '../exports/plots/' + makeFullScenarioName(testName, numCLIs, nodeTypes, nodeSplit) + '/'
    if not os.path.exists(prePath):
        os.makedirs(prePath)
    outPath = prePath + 'packetLossVsUtilization.pdf'
    fig.savefig(outPath, dpi=100, bbox_inches='tight')
    outPath2 = prePath + 'packetLossVsUtilization.png'
    fig.savefig(outPath2, dpi=100, bbox_inches='tight', format='png')
    plt.close('all')

def plotTcpPacketLossVsUtilizationExp(testName, numCLIs, nodeTypes, nodeSplit, linkBitrate, pZero, constOffset):
    meanTPValues = []
    meanPacketLossValuesDupAck = []
    meanPacketLossValuesRto = []
    numSentPackets = []
    file_to_read = '../exports/extracted/throughput' + downlink[0] + '/' + makeFullScenarioName(testName, numCLIs, nodeTypes, nodeSplit) + '.csv'
    with open(file_to_read, mode='r') as readFile:
        csv_reader = csv.reader(readFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
        line_count = 0
        for row in csv_reader:
            if line_count == 1:
                meanTPValues = row
                break
            line_count += 1

    file_to_read = '../exports/extracted/dupAcks/' + makeFullScenarioName(testName, numCLIs, nodeTypes, nodeSplit) + '_srv.csv'
    with open(file_to_read, mode='r') as readFile:
        csv_reader = csv.reader(readFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
        line_count = 0
        for row in csv_reader:
            if line_count == 1:
                meanPacketLossValuesDupAck = [float(x) for x in row]
                break
            line_count += 1 
    
    file_to_read = '../exports/extracted/numRtos/' + makeFullScenarioName(testName, numCLIs, nodeTypes, nodeSplit) + '_srv.csv'
    with open(file_to_read, mode='r') as readFile:
        csv_reader = csv.reader(readFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
        line_count = 0
        for row in csv_reader:
            if line_count == 1:
                meanPacketLossValuesRto = [float(x) for x in row]
                break
            line_count += 1

    file_to_read = '../exports/extracted/txPkNumPackets/' + makeFullScenarioName(testName, numCLIs, nodeTypes, nodeSplit) + '_srv.csv'
    with open(file_to_read, mode='r') as readFile:
        csv_reader = csv.reader(readFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
        line_count = 0
        for row in csv_reader:
            if line_count == 1:
                numSentPackets = [float(x) for x in row]
                break
            line_count += 1 
    
    meanUtilValues = [round((x/linkBitrate)*100,3) for x in meanTPValues]

    meanPacketLossValues = [sum(x) for x in zip(meanPacketLossValuesDupAck, meanPacketLossValuesRto)]
    packetLossRatio = [(a/b)*100 for a,b in zip(meanPacketLossValues, numSentPackets)]

    x = np.array([a for a,_ in sorted(zip(meanUtilValues, packetLossRatio))])
    y = np.array([round(b,3) for _,b in sorted(zip(meanUtilValues, packetLossRatio))])

    fig, ax1 = plt.subplots(1, figsize=(16,12))
    ax1.plot(x, y, 'o-', label='Measured Data')
    plt.xlabel('Mean Link Utilization [%]')
    plt.ylabel('TCP Packet Loss [%]')
    popt, pcov = scipy.optimize.curve_fit(expFunc, x, y, p0=pZero, maxfev=1000000, bounds=(0, np.inf))
    popt[2] += constOffset
    print(popt)
    with np.printoptions(precision=2):
        print(testName + ' with ' + str(nodeSplit) + ': ' + str(popt))
        regLine = np.linspace(0, 100, 100)
        theLabel = 'Exponential Fit'
        ax1.plot(regLine, expFunc(regLine, *popt), '-', label=theLabel)
    plt.legend()

    textstr = makeEquationString(popt) + '\n'
    textstr += 'MSE: ' + str(np.mean((y-expFunc(x, *popt))**2)) + '\n'
    ss_res = np.dot((y - expFunc(x, *popt)),(y - expFunc(x, *popt)))
    ymean = np.mean(y)
    ss_tot = np.dot((y-ymean),(y-ymean))
    textstr += 'R2: ' + str(1-ss_res/ss_tot)
    props = dict(boxstyle='round', facecolor='white', alpha=0.2)
    ax1.text(0.03, 0.74, textstr, transform=ax1.transAxes, fontsize=22, verticalalignment='top', bbox=props)

    prePath = '../exports/plots/' + makeFullScenarioName(testName, numCLIs, nodeTypes, nodeSplit) + '/'
    if not os.path.exists(prePath):
        os.makedirs(prePath)
    outPath = prePath + 'packetLossVsUtilization.pdf'
    fig.savefig(outPath, dpi=100, bbox_inches='tight')
    outPath2 = prePath + 'packetLossVsUtilization.png'
    fig.savefig(outPath2, dpi=100, bbox_inches='tight', format='png')
    plt.close('all')

def plotE2edAndQLVsUtilizationExp(testName, numCLIs, nodeTypes, nodeSplit, linkBitrate, pZero):
    meanTPValues = []
    meanE2edValues = []
    e2edstdDevValues = []
    e2edci95hValues = []
    # e2edminValues = []
    # e2edmaxValues = []
    meanQLValues = []
    qlstdDevValues = []
    qlci95hValues = []
    # qlminValues = []
    # qlmaxValues = []
    file_to_read = '../exports/extracted/throughput' + downlink[0] + '/' + makeFullScenarioName(testName, numCLIs, nodeTypes, nodeSplit) + '.csv'
    with open(file_to_read, mode='r') as readFile:
        csv_reader = csv.reader(readFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
        line_count = 0
        for row in csv_reader:
            if line_count == 1:
                meanTPValues = row
                break
            line_count += 1

    file_to_read = '../exports/extracted/endToEndDelay/' + makeFullScenarioName(testName, numCLIs, nodeTypes, nodeSplit) + '.csv'
    with open(file_to_read, mode='r') as readFile:
        csv_reader = csv.reader(readFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
        line_count = 0
        for row in csv_reader:
            if line_count == 1:
                meanE2edValues = row
            elif line_count == 2:
                e2edstdDevValues = row
            elif line_count == 3:
                e2edci95hValues = row
            # elif line_count == 4:
            #     e2edminValues = row
            # elif line_count == 5:
            #     e2edmaxValues = row
                break
            line_count += 1
    
    file_to_read = '../exports/extracted/queueLength/' + makeFullScenarioName(testName, numCLIs, nodeTypes, nodeSplit) + '.csv'
    with open(file_to_read, mode='r') as readFile:
        csv_reader = csv.reader(readFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
        line_count = 0
        for row in csv_reader:
            if line_count == 1:
                meanQLValues = row
            elif line_count == 2:
                qlstdDevValues = row
            elif line_count == 3:
                qlci95hValues = row
            # elif line_count == 4:
            #     qlminValues = row
            # elif line_count == 5:
            #     qlmaxValues = row
                break
            line_count += 1 
    
    meanUtilValues = [round((x/linkBitrate)*100,3) for x in meanTPValues]

    x = np.array([a for a,_ in sorted(zip(meanUtilValues, meanE2edValues))])
    e2edy = np.array([round(b*1000,3) for _,b in sorted(zip(meanUtilValues, meanE2edValues))])
    qly = np.array([b for _,b in sorted(zip(meanUtilValues, meanQLValues))])
    # e2edsortedstdDevValues = [round(b*1000,6) for _,b in sorted(zip(meanUtilValues, e2edstdDevValues))]
    e2edsortedci95hValues = [round(b*1000,6) for _,b in sorted(zip(meanUtilValues, e2edci95hValues))]
    # e2edsortedminValues = [round(b*1000,6) for _,b in sorted(zip(meanUtilValues, e2edminValues))]
    # e2edsortedmaxValues = [round(b*1000,6) for _,b in sorted(zip(meanUtilValues, e2edmaxValues))]
    qlsortedci95hValues = [b for _,b in sorted(zip(meanUtilValues, qlci95hValues))]
    # print(e2edsortedstdDevValues)
    # print(e2edsortedci95hValues)

    fig, ax1 = plt.subplots(1, figsize=(16,12))
    ax1.errorbar(x, e2edy, yerr=e2edsortedci95hValues, fmt='-', ecolor='red')
    # ax1.fill_between(x, e2edsortedminValues, e2edsortedmaxValues, facecolor='grey', alpha=0.2, label='Delay Range')
    plt.xlabel('Mean Link Utilization [%]')
    plt.ylabel('Mean End To End Delay [ms]')

    # popt, pcov = scipy.optimize.curve_fit(expFunc, x, y, p0=pZero, maxfev=1000000, bounds=(0,np.inf))
    # with np.printoptions(precision=2):
    #     print(testName + ' with ' + str(nodeSplit) + ': ' + str(popt))
    #     # regLine = np.linspace(0, max(meanUtilValues), 100)
    #     regLine = np.linspace(0, 100, 100)
    #     theLabel = 'Exponential Fit'
    #     ax1.plot(regLine, expFunc(regLine, *popt), '-', label=theLabel, color='orange')
    # plt.legend()

    # ax1.set_ylim(0,1.3*max(expFunc(regLine[-1], *popt), max(y)))

    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

    color = 'tab:green'
    ax2.set_ylabel('Mean Queue Length in Downlink', color=color)  # we already handled the x-label with ax1
    ax2.errorbar(x, qly, yerr=qlsortedci95hValues, fmt='-', ecolor='red', color=color)
    ax2.tick_params(axis='y', labelcolor=color)

    # textstr = makeEquationString(popt) + '\n'
    # textstr += 'MSE: ' + str(np.mean((y-expFunc(x, *popt))**2)) + '\n'
    # ss_res = np.dot((y - expFunc(x, *popt)),(y - expFunc(x, *popt)))
    # ymean = np.mean(y)
    # ss_tot = np.dot((y-ymean),(y-ymean))
    # textstr += 'R2: ' + str(1-ss_res/ss_tot)
    # props = dict(boxstyle='round', facecolor='white', alpha=0.2)
    # ax1.text(0.03, 0.64, textstr, transform=ax1.transAxes, fontsize=22, verticalalignment='top', bbox=props)

    prePath = '../exports/plots/' + makeFullScenarioName(testName, numCLIs, nodeTypes, nodeSplit) + '/'
    if not os.path.exists(prePath):
        os.makedirs(prePath)
    outPath = prePath + 'delayAndQueueLengthVsUtilization.pdf'
    fig.savefig(outPath, dpi=100, bbox_inches='tight')
    outPath2 = prePath + 'delayAndQueueLengthVsUtilization.png'
    fig.savefig(outPath2, dpi=100, bbox_inches='tight', format='png')
    plt.close('all')

def plotRttAndQLVsUtilizationExp(testName, numCLIs, nodeTypes, nodeSplit, linkBitrate, pZero):
    meanTPValues = []
    meanE2edValues = []
    e2edstdDevValues = []
    e2edci95hValues = []
    meanQLValues = []
    qlstdDevValues = []
    qlci95hValues = []

    file_to_read = '../exports/extracted/throughput' + downlink[0] + '/' + makeFullScenarioName(testName, numCLIs, nodeTypes, nodeSplit) + '.csv'
    with open(file_to_read, mode='r') as readFile:
        csv_reader = csv.reader(readFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
        line_count = 0
        for row in csv_reader:
            if line_count == 1:
                meanTPValues = row
                break
            line_count += 1

    file_to_read = '../exports/extracted/rtt/' + makeFullScenarioName(testName, numCLIs, nodeTypes, nodeSplit) + '.csv'
    with open(file_to_read, mode='r') as readFile:
        csv_reader = csv.reader(readFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
        line_count = 0
        for row in csv_reader:
            if line_count == 1:
                meanE2edValues = row
            elif line_count == 2:
                e2edstdDevValues = row
            elif line_count == 3:
                e2edci95hValues = row
                break
            line_count += 1
    
    file_to_read = '../exports/extracted/queueLength/' + makeFullScenarioName(testName, numCLIs, nodeTypes, nodeSplit) + '.csv'
    with open(file_to_read, mode='r') as readFile:
        csv_reader = csv.reader(readFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
        line_count = 0
        for row in csv_reader:
            if line_count == 1:
                meanQLValues = row
            elif line_count == 2:
                qlstdDevValues = row
            elif line_count == 3:
                qlci95hValues = row
                break
            line_count += 1 
    
    meanUtilValues = [round((x/linkBitrate)*100,3) for x in meanTPValues]

    x = np.array([a for a,_ in sorted(zip(meanUtilValues, meanE2edValues))])
    e2edy = np.array([round(b*1000,3) for _,b in sorted(zip(meanUtilValues, meanE2edValues))])
    qly = np.array([b for _,b in sorted(zip(meanUtilValues, meanQLValues))])
    # e2edsortedstdDevValues = [round(b*1000,6) for _,b in sorted(zip(meanUtilValues, e2edstdDevValues))]
    e2edsortedci95hValues = [round(b*1000,6) for _,b in sorted(zip(meanUtilValues, e2edci95hValues))]
    # e2edsortedminValues = [round(b*1000,6) for _,b in sorted(zip(meanUtilValues, e2edminValues))]
    # e2edsortedmaxValues = [round(b*1000,6) for _,b in sorted(zip(meanUtilValues, e2edmaxValues))]
    qlsortedci95hValues = [b for _,b in sorted(zip(meanUtilValues, qlci95hValues))]
    # print(e2edsortedstdDevValues)
    # print(e2edsortedci95hValues)

    fig, ax1 = plt.subplots(1, figsize=(16,12))
    ax1.errorbar(x, e2edy, yerr=e2edsortedci95hValues, fmt='-', ecolor='red')
    # ax1.fill_between(x, e2edsortedminValues, e2edsortedmaxValues, facecolor='grey', alpha=0.2, label='Delay Range')
    plt.xlabel('Mean Link Utilization [%]')
    plt.ylabel('Mean RTT [ms]')

    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

    color = 'tab:green'
    ax2.set_ylabel('Mean Queue Length in Downlink', color=color)  # we already handled the x-label with ax1
    ax2.errorbar(x, qly, yerr=qlsortedci95hValues, fmt='-', ecolor='red', color=color)
    ax2.tick_params(axis='y', labelcolor=color)

    prePath = '../exports/plots/' + makeFullScenarioName(testName, numCLIs, nodeTypes, nodeSplit) + '/'
    if not os.path.exists(prePath):
        os.makedirs(prePath)
    outPath = prePath + 'rttAndQueueLengthVsUtilization.pdf'
    fig.savefig(outPath, dpi=100, bbox_inches='tight')
    outPath2 = prePath + 'rttAndQueueLengthVsUtilization.png'
    fig.savefig(outPath2, dpi=100, bbox_inches='tight', format='png')
    plt.close('all')

def plotE2edVsQLExp(testName, numCLIs, nodeTypes, nodeSplit, linkBitrate, pZero):
    meanE2edValues = []
    e2edstdDevValues = []
    e2edci95hValues = []
    meanQLValues = []
    qlstdDevValues = []
    qlci95hValues = []

    file_to_read = '../exports/extracted/endToEndDelay/' + makeFullScenarioName(testName, numCLIs, nodeTypes, nodeSplit) + '.csv'
    with open(file_to_read, mode='r') as readFile:
        csv_reader = csv.reader(readFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
        line_count = 0
        for row in csv_reader:
            if line_count == 1:
                meanE2edValues = row
            elif line_count == 2:
                e2edstdDevValues = row
            elif line_count == 3:
                e2edci95hValues = row
                break
            line_count += 1
    
    file_to_read = '../exports/extracted/queueLength/' + makeFullScenarioName(testName, numCLIs, nodeTypes, nodeSplit) + '.csv'
    with open(file_to_read, mode='r') as readFile:
        csv_reader = csv.reader(readFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
        line_count = 0
        for row in csv_reader:
            if line_count == 1:
                meanQLValues = row
            elif line_count == 2:
                qlstdDevValues = row
            elif line_count == 3:
                qlci95hValues = row
                break
            line_count += 1 

    x = np.array([a for a,_ in sorted(zip(meanQLValues, meanE2edValues))])
    y = np.array([round(b*1000,3) for _,b in sorted(zip(meanQLValues, meanE2edValues))])
    e2edsortedci95hValues = [round(b*1000,6) for _,b in sorted(zip(meanQLValues, e2edci95hValues))]

    fig, ax1 = plt.subplots(1, figsize=(16,12))
    ax1.errorbar(x, y, yerr=e2edsortedci95hValues, xerr=qlci95hValues, fmt='-', ecolor='red')

    plt.xlabel('Mean Queue Length in Downlink')
    plt.ylabel('Mean End To End Delay [ms]')


    prePath = '../exports/plots/' + makeFullScenarioName(testName, numCLIs, nodeTypes, nodeSplit) + '/'
    if not os.path.exists(prePath):
        os.makedirs(prePath)
    outPath = prePath + 'delayVsQueueLength.pdf'
    fig.savefig(outPath, dpi=100, bbox_inches='tight')
    outPath2 = prePath + 'delayVsQueueLength.png'
    fig.savefig(outPath2, dpi=100, bbox_inches='tight', format='png')
    plt.close('all')

def plotRttVsQLExp(testName, numCLIs, nodeTypes, nodeSplit, linkBitrate, pZero):
    meanE2edValues = []
    e2edstdDevValues = []
    e2edci95hValues = []
    meanQLValues = []
    qlstdDevValues = []
    qlci95hValues = []

    file_to_read = '../exports/extracted/rtt/' + makeFullScenarioName(testName, numCLIs, nodeTypes, nodeSplit) + '.csv'
    with open(file_to_read, mode='r') as readFile:
        csv_reader = csv.reader(readFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
        line_count = 0
        for row in csv_reader:
            if line_count == 1:
                meanE2edValues = row
            elif line_count == 2:
                e2edstdDevValues = row
            elif line_count == 3:
                e2edci95hValues = row
                break
            line_count += 1
    
    file_to_read = '../exports/extracted/queueLength/' + makeFullScenarioName(testName, numCLIs, nodeTypes, nodeSplit) + '.csv'
    with open(file_to_read, mode='r') as readFile:
        csv_reader = csv.reader(readFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
        line_count = 0
        for row in csv_reader:
            if line_count == 1:
                meanQLValues = row
            elif line_count == 2:
                qlstdDevValues = row
            elif line_count == 3:
                qlci95hValues = row
                break
            line_count += 1 

    x = np.array([a for a,_ in sorted(zip(meanQLValues, meanE2edValues))])
    y = np.array([round(b*1000,3) for _,b in sorted(zip(meanQLValues, meanE2edValues))])
    e2edsortedci95hValues = [round(b*1000,6) for _,b in sorted(zip(meanQLValues, e2edci95hValues))]

    fig, ax1 = plt.subplots(1, figsize=(16,12))
    ax1.errorbar(x, y, yerr=e2edsortedci95hValues, xerr=qlci95hValues, fmt='-', ecolor='red')

    plt.xlabel('Mean Queue Length in Downlink [packets]')
    plt.ylabel('Mean RTT [ms]')


    prePath = '../exports/plots/' + makeFullScenarioName(testName, numCLIs, nodeTypes, nodeSplit) + '/'
    if not os.path.exists(prePath):
        os.makedirs(prePath)
    outPath = prePath + 'rttVsQueueLength.pdf'
    fig.savefig(outPath, dpi=100, bbox_inches='tight')
    outPath2 = prePath + 'rttVsQueueLength.png'
    fig.savefig(outPath2, dpi=100, bbox_inches='tight', format='png')
    plt.close('all')


def plotRttVsUsedCliBandExp(testName, numCLIs, nodeTypes, nodeSplit, linkBitrate, pZero):
    numClients = []
    meanTPValues = []
    meanE2edValues = []
    stdDevValues = []
    ci95hValues = []
    minValues = []
    maxValues = []
    file_to_read = '../exports/extracted/throughput' + downlink[0] + '/' + makeFullScenarioName(testName, numCLIs, nodeTypes, nodeSplit) + '.csv'
    with open(file_to_read, mode='r') as readFile:
        csv_reader = csv.reader(readFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
        line_count = 0
        for row in csv_reader:
            print(row)
            if line_count == 0:
                numClients = row
            elif line_count == 1:
                meanTPValues = row
                # break
            line_count += 1

    file_to_read = '../exports/extracted/rtt/' + makeFullScenarioName(testName, numCLIs, nodeTypes, nodeSplit) + '.csv'
    with open(file_to_read, mode='r') as readFile:
        csv_reader = csv.reader(readFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
        line_count = 0
        for row in csv_reader:
            if line_count == 1:
                meanE2edValues = row
            elif line_count == 2:
                stdDevValues = row
            elif line_count == 3:
                ci95hValues = row
            elif line_count == 4:
                minValues = row
            elif line_count == 5:
                maxValues = row
                break
            line_count += 1 
    
    meanUtilValues = [round((a/b),3) for a,b in zip(meanTPValues,numClients)]

    x = np.array([a for a,_ in sorted(zip(meanUtilValues, meanE2edValues))])
    y = np.array([round(b*1000,3) for _,b in sorted(zip(meanUtilValues, meanE2edValues))])
    sortedstdDevValues = [round(b*1000,6) for _,b in sorted(zip(meanUtilValues, stdDevValues))]
    sortedci95hValues = [round(b*1000,6) for _,b in sorted(zip(meanUtilValues, ci95hValues))]
    sortedminValues = [round(b*1000,6) for _,b in sorted(zip(meanUtilValues, minValues))]
    sortedmaxValues = [round(b*1000,6) for _,b in sorted(zip(meanUtilValues, maxValues))]

    print(sortedstdDevValues)
    print(sortedci95hValues)

    fig, ax1 = plt.subplots(1, figsize=(16,12))
    ax1.errorbar(x, y, yerr=sortedci95hValues, fmt='-', ecolor='red', label='Measured Data')
    ax1.fill_between(x, sortedminValues, sortedmaxValues, facecolor='grey', alpha=0.2, label='Delay Range')
    plt.xlabel('Mean Client bandwidth [kbps]')
    plt.ylabel('Mean RTT [ms]')

    popt, pcov = scipy.optimize.curve_fit(expFunc, x, y, p0=pZero, maxfev=1000000, bounds=(0,np.inf))
    with np.printoptions(precision=2):
        print(testName + ' with ' + str(nodeSplit) + ': ' + str(popt))
        # regLine = np.linspace(0, max(meanUtilValues), 100)
        regLine = np.linspace(0, 100, 100)
        theLabel = 'Exponential Fit'
        ax1.plot(regLine, expFunc(regLine, *popt), '-', label=theLabel, color='orange')
    plt.legend()

    ax1.set_ylim(0,1.3*max(expFunc(regLine[-1], *popt), max(y)))

    textstr = makeEquationString(popt) + '\n'
    textstr += 'MSE: ' + str(np.mean((y-expFunc(x, *popt))**2)) + '\n'
    ss_res = np.dot((y - expFunc(x, *popt)),(y - expFunc(x, *popt)))
    ymean = np.mean(y)
    ss_tot = np.dot((y-ymean),(y-ymean))
    textstr += 'R2: ' + str(1-ss_res/ss_tot)
    props = dict(boxstyle='round', facecolor='white', alpha=0.2)
    ax1.text(0.03, 0.64, textstr, transform=ax1.transAxes, fontsize=22, verticalalignment='top', bbox=props)

    prePath = '../exports/plots/' + makeFullScenarioName(testName, numCLIs, nodeTypes, nodeSplit) + '/'
    if not os.path.exists(prePath):
        os.makedirs(prePath)
    outPath = prePath + 'rttVsUsedCliBand.pdf'
    fig.savefig(outPath, dpi=100, bbox_inches='tight')
    outPath2 = prePath + 'rttVsUsedCliBand.png'
    fig.savefig(outPath2, dpi=100, bbox_inches='tight', format='png')
    plt.close('all')

def negExpFunc(x, a, b, c):
    return a * np.exp(-b*x) + c

def plotRttVsAvailCliBandExp(testName, numCLIs, nodeTypes, nodeSplit, linkBitrate, pZero):
    numClients = []
    meanTPValues = []
    meanE2edValues = []
    stdDevValues = []
    ci95hValues = []
    minValues = []
    maxValues = []
    file_to_read = '../exports/extracted/throughput' + downlink[0] + '/' + makeFullScenarioName(testName, numCLIs, nodeTypes, nodeSplit) + '.csv'
    with open(file_to_read, mode='r') as readFile:
        csv_reader = csv.reader(readFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
        line_count = 0
        for row in csv_reader:
            print(row)
            if line_count == 0:
                numClients = row
            elif line_count == 1:
                meanTPValues = row
                # break
            line_count += 1

    file_to_read = '../exports/extracted/rtt/' + makeFullScenarioName(testName, numCLIs, nodeTypes, nodeSplit) + '.csv'
    with open(file_to_read, mode='r') as readFile:
        csv_reader = csv.reader(readFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
        line_count = 0
        for row in csv_reader:
            if line_count == 1:
                meanE2edValues = row
            elif line_count == 2:
                stdDevValues = row
            elif line_count == 3:
                ci95hValues = row
            elif line_count == 4:
                minValues = row
            elif line_count == 5:
                maxValues = row
                break
            line_count += 1 
    
    meanUtilValues = [round((linkBitrate/a),3) for a in numClients]

    x = np.array([a for a,_ in sorted(zip(meanUtilValues, meanE2edValues))])
    y = np.array([round(b*1000,3) for _,b in sorted(zip(meanUtilValues, meanE2edValues))])
    sortedstdDevValues = [round(b*1000,6) for _,b in sorted(zip(meanUtilValues, stdDevValues))]
    sortedci95hValues = [round(b*1000,6) for _,b in sorted(zip(meanUtilValues, ci95hValues))]
    sortedminValues = [round(b*1000,6) for _,b in sorted(zip(meanUtilValues, minValues))]
    sortedmaxValues = [round(b*1000,6) for _,b in sorted(zip(meanUtilValues, maxValues))]

    print(sortedstdDevValues)
    print(sortedci95hValues)

    fig, ax1 = plt.subplots(1, figsize=(16,12))
    ax1.errorbar(x, y, yerr=sortedci95hValues, fmt='-', ecolor='red', label='Measured Data')
    ax1.fill_between(x, sortedminValues, sortedmaxValues, facecolor='grey', alpha=0.2, label='Delay Range')
    plt.xlabel('Mean Client bandwidth [kbps]')
    plt.ylabel('Mean RTT [ms]')

    popt, pcov = scipy.optimize.curve_fit(negExpFunc, x, y, p0=pZero, maxfev=1000000, bounds=(0,np.inf))
    with np.printoptions(precision=5):
        print(testName + ' with ' + str(nodeSplit) + ': ' + str(popt))
        regLine = np.linspace(0, max(x), 100)
        # regLine = np.linspace(0, 100, 100)
        theLabel = 'Exponential Fit'
        print(popt)
        ax1.plot(regLine, negExpFunc(regLine, *popt), '-', label=theLabel, color='orange')
    plt.legend()

    # ax1.set_ylim(0,1.3*max(negExpFunc(regLine[-1], *popt), max(y)))

    textstr = makeEquationString(popt) + '\n'
    textstr += 'MSE: ' + str(np.mean((y-negExpFunc(x, *popt))**2)) + '\n'
    ss_res = np.dot((y - negExpFunc(x, *popt)),(y - negExpFunc(x, *popt)))
    ymean = np.mean(y)
    ss_tot = np.dot((y-ymean),(y-ymean))
    textstr += 'R2: ' + str(1-ss_res/ss_tot)
    props = dict(boxstyle='round', facecolor='white', alpha=0.2)
    ax1.text(0.03, 0.64, textstr, transform=ax1.transAxes, fontsize=22, verticalalignment='top', bbox=props)

    prePath = '../exports/plots/' + makeFullScenarioName(testName, numCLIs, nodeTypes, nodeSplit) + '/'
    if not os.path.exists(prePath):
        os.makedirs(prePath)
    outPath = prePath + 'rttVsAvailCliBand.pdf'
    fig.savefig(outPath, dpi=100, bbox_inches='tight')
    outPath2 = prePath + 'rttVsAvailCliBand.png'
    fig.savefig(outPath2, dpi=100, bbox_inches='tight', format='png')
    plt.close('all')


# expNameLabel = {'singleAppLSTest_FileDownload2-5MB' : 'Variable link speed',
#                 'singleAppStressTest_FileDownload2-5MB' : 'Variable # clients',
#                 'singleAppLSTest_NewLiveVideoClient' : 'Variable link speed',
#                 'singleAppStressTest_NewLiveVideoClient' : 'Variable # clients',
#                 'singleAppLSTest_SSH' : 'Variable link speed',
#                 'singleAppStressTest_SSH' : 'Variable # clients',
#                 'singleAppLSTest_Video' : 'Variable link speed',
#                 'singleAppStressTest_Video' : 'Variable # clients',
#                 'singleAppLSTest_VoIP' : 'Variable link speed',
#                 'singleAppStressTest_VoIP' : 'Variable # clients',}


def plotRttVsAvailCliBandComp(testName1, sumNodes1, nodeTypes1, nodeSplit1, testName2, numCLIs2, nodeTypes2, nodeSplit2, linkBitrate2, pZero1, pZero2, manual):
    tps = []
    meanTPs = []
    meanE2EDs = []
    file_to_read = '../exports/extracted/lsMeanTPMeanRTT/' + makeFullScenarioName(testName1, sumNodes1, nodeTypes1, nodeSplit1) + '.csv'
    with open(file_to_read, mode='r') as readFile:
        csv_reader = csv.reader(readFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                tps = row
            elif line_count == 1:
                meanTPs = row
            elif line_count == 2:
                meanE2EDs = row
            line_count += 1 

    fig, ax1 = plt.subplots(1, figsize=(16,12))
    print('Min mean RTT ' + testName1 + ' = ' + str(min(meanE2EDs)) + '; Min avail cli band: ' + str(min(tps)))
    ax1.plot(tps, [x*1000 for x in meanE2EDs], 'o', label='Variable Link Speed (VLS)')
    
    popt, pcov = scipy.optimize.curve_fit(negExpFunc, tps, [x*1000 for x in meanE2EDs], p0=pZero1, maxfev=1000000, bounds=(0,np.inf))
    
    with np.printoptions(precision=2):
        print('Variable link speed test ' + testName1 + ' with ' + str(nodeSplit2) + ': ' + str(popt))
        # regLine = np.linspace(0, max(meanUtilValues), 100)
        # print(tps[-1])
        regLine = np.linspace(0, tps[-1], 1000)
        # print(*popt)
        # print(*pZero1)
        ax1.plot(regLine, negExpFunc(regLine, *popt), '-', label='VLS Automatic fit', color='yellow')

    y = np.array([x*1000 for x in meanE2EDs])
    x = np.array(tps)
    textstr = 'VLS Automatic Fit:\n'   
    textstr += makeEquationString(popt) + '\n'
    textstr += 'MSE: ' + str(np.mean((y-negExpFunc(x, *popt))**2)) + '\n'
    ss_res = np.dot((y - negExpFunc(x, *popt)),(y - negExpFunc(x, *popt)))
    ymean = np.mean(y)
    ss_tot = np.dot((y-ymean),(y-ymean))
    textstr += 'R2: ' + str(1-ss_res/ss_tot) + '\n'
    # ax1.plot(regLine, negExpFunc(regLine, *pZero1), '-', label='VLS Manual fit', color='red')

    numClients = []
    meanTPValues = []
    meanE2edValues = []
    stdDevValues = []
    ci95hValues = []
    minValues = []
    maxValues = []
    file_to_read = '../exports/extracted/throughput' + downlink[0] + '/' + makeFullScenarioName(testName2, numCLIs2, nodeTypes2, nodeSplit2) + '.csv'
    with open(file_to_read, mode='r') as readFile:
        csv_reader = csv.reader(readFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
        line_count = 0
        for row in csv_reader:
            # print(row)
            if line_count == 0:
                numClients = row
            elif line_count == 1:
                meanTPValues = row
                break
            line_count += 1

    file_to_read = '../exports/extracted/rtt/' + makeFullScenarioName(testName2, numCLIs2, nodeTypes2, nodeSplit2) + '.csv'
    with open(file_to_read, mode='r') as readFile:
        csv_reader = csv.reader(readFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
        line_count = 0
        for row in csv_reader:
            if line_count == 1:
                meanE2edValues = row
            elif line_count == 2:
                stdDevValues = row
            elif line_count == 3:
                ci95hValues = row
            elif line_count == 4:
                minValues = row
            elif line_count == 5:
                maxValues = row
                break
            line_count += 1 

    meanUtilValues = [round((linkBitrate2/a),3) for a in numClients]

    print('Min mean RTT ' + testName2 + ' = ' + str(min(meanE2edValues)) + '; Min avail cli band: ' + str(min(meanUtilValues)))

    x = np.array([a for a,_ in sorted(zip(meanUtilValues, meanE2edValues))])
    y = np.array([round(b*1000,3) for _,b in sorted(zip(meanUtilValues, meanE2edValues))])

    ax1.plot(x, y, 'o', label='Variable # Clients (VNC)')

    popt, pcov = scipy.optimize.curve_fit(negExpFunc, x, y, p0=pZero2, maxfev=1000000, bounds=(0,np.inf))
    
    with np.printoptions(precision=2):
        print('Variable number of clients test ' + testName2 + ' with ' + str(nodeSplit2) + ': ' + str(popt))
        # regLine = np.linspace(0, max(meanUtilValues), 100)
        # print(tps[-1])
        regLine = np.linspace(x[0], x[-1], 1000)
        # print(*popt)
        # print(*pZero2)
        ax1.plot(regLine, negExpFunc(regLine, *popt), '-', label='VNC Automatic fit', color='green')
        textstr += 'VNC Automatic Fit:\n'   
        textstr += makeEquationString(popt) + '\n'
        y = np.array(y)
        x = np.array(x)
        textstr += 'MSE: ' + str(np.mean((y-negExpFunc(x, *popt))**2)) + '\n'
        ss_res = np.dot((y - negExpFunc(x, *popt)),(y - negExpFunc(x, *popt)))
        ymean = np.mean(y)
        ss_tot = np.dot((y-ymean),(y-ymean))
        textstr += 'R2: ' + str(1-ss_res/ss_tot) + '\n'
    print('Manual set ' + testName2 + ' with ' + str(nodeSplit2) + ': ' + str(manual))
    regLine = np.linspace(0, x[-1], 1000)
    ax1.plot(regLine, negExpFunc(regLine, *manual), '-', label='VNC Manual fit', color='red')
    textstr += 'VNC Manual Fit:\n'   
    textstr += makeEquationString(manual) + '\n'
    textstr += 'MSE: ' + str(np.mean((y-negExpFunc(x, *manual))**2)) + '\n'
    ss_res = np.dot((y - negExpFunc(x, *manual)),(y - negExpFunc(x, *manual)))
    ymean = np.mean(y)
    ss_tot = np.dot((y-ymean),(y-ymean))
    textstr += 'R2: ' + str(1-ss_res/ss_tot)

    props = dict(boxstyle='round', facecolor='white', alpha=0.2)
    ax1.text(0, -0.18, textstr, transform=ax1.transAxes, fontsize=22, verticalalignment='top', bbox=props)

    plt.legend()
    plt.xlabel('Avail Cli Bandwidth [kbps]')
    plt.ylabel('Mean Client RTT Delay [ms]')
    prePath = '../exports/plots/' + makeFullScenarioName(testName1, sumNodes1, nodeTypes1, nodeSplit1) + '/'
    if not os.path.exists(prePath):
        os.makedirs(prePath)
    outPath = prePath + 'rttVsAvailCliBandComp.pdf'
    print(outPath)
    fig.savefig(outPath, dpi=100, bbox_inches='tight')
    outPath2 = prePath + 'rttVsAvailCliBandComp.png'
    fig.savefig(outPath2, dpi=100, bbox_inches='tight', format='png')
    plt.close('all')


def plotPaperDelayRTTVsAvailCliBandComp(testName1, sumNodes1, nodeTypes1, nodeSplit1, testName2, numCLIs2, nodeTypes2, nodeSplit2, linkBitrate2, pZero1, pZero2, manual):
    # tps = []
    # meanTPs = []
    # meanE2EDs = []
    # file_to_read = '../exports/extracted/lsMeanTPMeanRTT/' + makeFullScenarioName(testName1, sumNodes1, nodeTypes1, nodeSplit1) + '.csv'
    # with open(file_to_read, mode='r') as readFile:
    #     csv_reader = csv.reader(readFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
    #     line_count = 0
    #     for row in csv_reader:
    #         if line_count == 0:
    #             tps = row
    #         elif line_count == 1:
    #             meanTPs = row
    #         elif line_count == 2:
    #             meanE2EDs = row
    #         line_count += 1 

    fig, ax1 = plt.subplots(1, figsize=(16,12))
    # print('Min mean RTT ' + testName1 + ' = ' + str(min(meanE2EDs)) + '; Min avail cli band: ' + str(min(tps)))
    # ax1.plot(tps, [x*1000 for x in meanE2EDs], 'o', label='Variable Link Speed (VLS)')
    
    # popt, pcov = scipy.optimize.curve_fit(negExpFunc, tps, [x*1000 for x in meanE2EDs], p0=pZero1, maxfev=1000000, bounds=(0,np.inf))
    
    # with np.printoptions(precision=2):
    #     print('Variable link speed test ' + testName1 + ' with ' + str(nodeSplit2) + ': ' + str(popt))
    #     # regLine = np.linspace(0, max(meanUtilValues), 100)
    #     # print(tps[-1])
    #     regLine = np.linspace(0, tps[-1], 1000)
    #     # print(*popt)
    #     # print(*pZero1)
    #     ax1.plot(regLine, negExpFunc(regLine, *popt), '-', label='VLS Automatic fit', color='yellow')

    # y = np.array([x*1000 for x in meanE2EDs])
    # x = np.array(tps)
    # textstr = 'VLS Automatic Fit:\n'   
    # textstr += makeEquationString(popt) + '\n'
    # textstr += 'MSE: ' + str(np.mean((y-negExpFunc(x, *popt))**2)) + '\n'
    # ss_res = np.dot((y - negExpFunc(x, *popt)),(y - negExpFunc(x, *popt)))
    # ymean = np.mean(y)
    # ss_tot = np.dot((y-ymean),(y-ymean))
    # textstr += 'R2: ' + str(1-ss_res/ss_tot) + '\n'
    # # ax1.plot(regLine, negExpFunc(regLine, *pZero1), '-', label='VLS Manual fit', color='red')

    numClients = []
    # meanTPValues = []
    # meanE2edValues = []
    # stdDevValues = []
    # ci95hValues = []
    # minValues = []
    # maxValues = []
    file_to_read = '../exports/extracted/throughput' + downlink[0] + '/' + makeFullScenarioName(testName2, numCLIs2, nodeTypes2, nodeSplit2) + '.csv'
    with open(file_to_read, mode='r') as readFile:
        csv_reader = csv.reader(readFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
        line_count = 0
        for row in csv_reader:
    #         # print(row)
            if line_count == 0:
                numClients = row
    #         elif line_count == 1:
    #             meanTPValues = row
    #             break
            line_count += 1

    file_to_read = '../exports/extracted/rtt/' + makeFullScenarioName(testName2, numCLIs2, nodeTypes2, nodeSplit2) + '.csv'
    with open(file_to_read, mode='r') as readFile:
        csv_reader = csv.reader(readFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
        line_count = 0
        for row in csv_reader:
            if line_count == 1:
                meanE2edValues = row
            elif line_count == 2:
                stdDevValues = row
            elif line_count == 3:
                ci95hValues = row
            elif line_count == 4:
                minValues = row
            elif line_count == 5:
                maxValues = row
                break
            line_count += 1 

    meanUtilValues = [round((linkBitrate2/a),3) for a in numClients]

    print('Min mean RTT ' + testName2 + ' = ' + str(min(meanE2edValues)) + '; Min avail cli band: ' + str(min(meanUtilValues)))

    x = np.array([a for a,_ in sorted(zip(meanUtilValues, meanE2edValues))])
    y = np.array([round(0.5*b*1000,3) for _,b in sorted(zip(meanUtilValues, meanE2edValues))])

    ax1.plot(x, y, 'o', label='Simulation Results')

    # popt, pcov = scipy.optimize.curve_fit(negExpFunc, x, y, p0=pZero2, maxfev=1000000, bounds=(0,np.inf))
    
    # with np.printoptions(precision=2):
        # print('Variable number of clients test ' + testName2 + ' with ' + str(nodeSplit2) + ': ' + str(popt))
        # regLine = np.linspace(0, max(meanUtilValues), 100)
        # print(tps[-1])
        # regLine = np.linspace(x[0], x[-1], 1000)
        # print(*popt)
        # print(*pZero2)
        # ax1.plot(regLine, negExpFunc(regLine, *popt), '-', label='VNC Automatic fit', color='green')
        # textstr += 'VNC Automatic Fit:\n'   
        # textstr += makeEquationString(popt) + '\n'
        # y = np.array(y)
        # x = np.array(x)
        # textstr += 'MSE: ' + str(np.mean((y-negExpFunc(x, *popt))**2)) + '\n'
        # ss_res = np.dot((y - negExpFunc(x, *popt)),(y - negExpFunc(x, *popt)))
        # ymean = np.mean(y)
        # ss_tot = np.dot((y-ymean),(y-ymean))
        # textstr += 'R2: ' + str(1-ss_res/ss_tot) + '\n'
    print('Manual set ' + testName2 + ' with ' + str(nodeSplit2) + ': ' + str(manual))
    regLine = np.linspace(0, x[-1], 1000)
    ax1.plot(regLine, negExpFunc(regLine, *manual), '-', label='Exponential Fit', color='red')
    # textstr = 'VNC Manual Fit:\n'   
    # textstr += makeEquationString(manual) + '\n'
    # textstr += 'MSE: ' + str(np.mean((y-negExpFunc(x, *manual))**2)) + '\n'
    # ss_res = np.dot((y - negExpFunc(x, *manual)),(y - negExpFunc(x, *manual)))
    # ymean = np.mean(y)
    # ss_tot = np.dot((y-ymean),(y-ymean))
    # textstr += 'R2: ' + str(1-ss_res/ss_tot)

    # props = dict(boxstyle='round', facecolor='white', alpha=0.2)
    # ax1.text(0, -0.18, textstr, transform=ax1.transAxes, fontsize=22, verticalalignment='top', bbox=props)

    plt.legend()
    plt.xlabel('Available Client Bandwidth [kbps]')
    plt.ylabel('Mean Client Delay [ms]')
    prePath = '../exports/plots/' + makeFullScenarioName(testName1, sumNodes1, nodeTypes1, nodeSplit1) + '/'
    if not os.path.exists(prePath):
        os.makedirs(prePath)
    outPath = prePath + 'paperDelayVsAvailCliBandComp.pdf'
    print(outPath)
    fig.savefig(outPath, dpi=100, bbox_inches='tight')
    outPath2 = prePath + 'paperDelayVsAvailCliBandComp.png'
    fig.savefig(outPath2, dpi=100, bbox_inches='tight', format='png')
    plt.close('all')


def plotE2edVsAvailCliBandComp(testName1, sumNodes1, nodeTypes1, nodeSplit1, testName2, numCLIs2, nodeTypes2, nodeSplit2, linkBitrate2, pZero1, pZero2, manual):
    tps = []
    meanTPs = []
    meanE2EDs = []
    file_to_read = '../exports/extracted/lsMeanTPMeanE2ED/' + makeFullScenarioName(testName1, sumNodes1, nodeTypes1, nodeSplit1) + '.csv'
    with open(file_to_read, mode='r') as readFile:
        csv_reader = csv.reader(readFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                tps = row
            elif line_count == 1:
                meanTPs = row
            elif line_count == 2:
                meanE2EDs = row
            line_count += 1 

    fig, ax1 = plt.subplots(1, figsize=(16,12))
    print('Min mean RTT ' + testName1 + ' = ' + str(min(meanE2EDs)) + '; Min avail cli band: ' + str(min(tps)))
    ax1.plot(tps, [x*1000 for x in meanE2EDs], 'o', label='Variable Link Speed (VLS)')
    popt, pcov = scipy.optimize.curve_fit(negExpFunc, tps, [x*1000 for x in meanE2EDs], p0=pZero1, maxfev=1000000, bounds=(0,np.inf))
    with np.printoptions(precision=2):
        print(testName2 + ' with ' + str(nodeSplit2) + ': ' + str(popt))
        # regLine = np.linspace(0, max(meanUtilValues), 100)
        print(tps[-1])
        regLine = np.linspace(tps[0]-300, 10000, 1000)
        print(*popt)
        print(*pZero1)
        ax1.plot(regLine, negExpFunc(regLine, *popt), '-', label='VLS Automatic fit', color='yellow')
    y = np.array([x*1000 for x in meanE2EDs])
    x = np.array(tps)
    textstr = 'VLS Automatic Fit:\n'   
    textstr += makeEquationString(popt) + '\n'
    textstr += 'MSE: ' + str(np.mean((y-negExpFunc(x, *popt))**2)) + '\n'
    ss_res = np.dot((y - negExpFunc(x, *popt)),(y - negExpFunc(x, *popt)))
    ymean = np.mean(y)
    ss_tot = np.dot((y-ymean),(y-ymean))
    textstr += 'R2: ' + str(1-ss_res/ss_tot) + '\n'
    
    numClients = []
    meanTPValues = []
    meanE2edValues = []
    stdDevValues = []
    ci95hValues = []
    minValues = []
    maxValues = []
    file_to_read = '../exports/extracted/throughput' + downlink[0] + '/' + makeFullScenarioName(testName2, numCLIs2, nodeTypes2, nodeSplit2) + '.csv'
    with open(file_to_read, mode='r') as readFile:
        csv_reader = csv.reader(readFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
        line_count = 0
        for row in csv_reader:
            # print(row)
            if line_count == 0:
                numClients = row
            elif line_count == 1:
                meanTPValues = row
                break
            line_count += 1

    file_to_read = '../exports/extracted/endToEndDelay/' + makeFullScenarioName(testName2, numCLIs2, nodeTypes2, nodeSplit2) + '.csv'
    with open(file_to_read, mode='r') as readFile:
        csv_reader = csv.reader(readFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
        line_count = 0
        for row in csv_reader:
            if line_count == 1:
                meanE2edValues = row
            elif line_count == 2:
                stdDevValues = row
            elif line_count == 3:
                ci95hValues = row
            elif line_count == 4:
                minValues = row
            elif line_count == 5:
                maxValues = row
                break
            line_count += 1 

    meanUtilValues = [round((linkBitrate2/a),3) for a in numClients]

    print('Min mean RTT ' + testName2 + ' = ' + str(min(meanE2edValues)) + '; Min avail cli band: ' + str(min(meanUtilValues)))

    x = np.array([a for a,_ in sorted(zip(meanUtilValues, meanE2edValues))])
    y = np.array([round(b*1000,3) for _,b in sorted(zip(meanUtilValues, meanE2edValues))])

    ax1.plot(x, y, 'o', label='Variable # Clients (VNC)')

    popt, pcov = scipy.optimize.curve_fit(negExpFunc, x, y, p0=pZero2, maxfev=1000000, bounds=(0,np.inf))
    
    with np.printoptions(precision=2):
        print(testName2 + ' with ' + str(nodeSplit2) + ': ' + str(popt))
        # regLine = np.linspace(0, max(meanUtilValues), 100)
        print(tps[-1])
        regLine = np.linspace(x[0], x[-1], 1000)
        ax1.plot(regLine, negExpFunc(regLine, *popt), '-', label='VNC Automatic fit', color='green')
        textstr += 'VNC Automatic Fit:\n'   
        textstr += makeEquationString(popt) + '\n'
        y = np.array(y)
        x = np.array(x)
        textstr += 'MSE: ' + str(np.mean((y-negExpFunc(x, *popt))**2)) + '\n'
        ss_res = np.dot((y - negExpFunc(x, *popt)),(y - negExpFunc(x, *popt)))
        ymean = np.mean(y)
        ss_tot = np.dot((y-ymean),(y-ymean))
        textstr += 'R2: ' + str(1-ss_res/ss_tot) + '\n'
    regLine = np.linspace(0, x[-1], 1000)
    ax1.plot(regLine, negExpFunc(regLine, *manual), '-', label='VNC Manual fit', color='red')
    textstr += 'VNC Manual Fit:\n'   
    textstr += makeEquationString(manual) + '\n'
    textstr += 'MSE: ' + str(np.mean((y-negExpFunc(x, *manual))**2)) + '\n'
    ss_res = np.dot((y - negExpFunc(x, *manual)),(y - negExpFunc(x, *manual)))
    ymean = np.mean(y)
    ss_tot = np.dot((y-ymean),(y-ymean))
    textstr += 'R2: ' + str(1-ss_res/ss_tot)

    props = dict(boxstyle='round', facecolor='white', alpha=0.2)
    ax1.text(0, -0.18, textstr, transform=ax1.transAxes, fontsize=22, verticalalignment='top', bbox=props)

    plt.legend()
    plt.xlabel('Avail Cli Bandwidth [kbps]')
    plt.ylabel('Mean Client End-To-End Delay [ms]')
    prePath = '../exports/plots/' + makeFullScenarioName(testName1, sumNodes1, nodeTypes1, nodeSplit1) + '/'
    if not os.path.exists(prePath):
        os.makedirs(prePath)
    outPath = prePath + 'e2edVsAvailCliBandComp.pdf'
    fig.savefig(outPath, dpi=100, bbox_inches='tight')
    outPath2 = prePath + 'e2edVsAvailCliBandComp.png'
    fig.savefig(outPath2, dpi=100, bbox_inches='tight', format='png')
    plt.close('all')


def plotPaperDelayE2edVsAvailCliBandComp(testName1, sumNodes1, nodeTypes1, nodeSplit1, testName2, numCLIs2, nodeTypes2, nodeSplit2, linkBitrate2, pZero1, pZero2, manual):
    # tps = []
    # meanTPs = []
    # meanE2EDs = []
    # file_to_read = '../exports/extracted/lsMeanTPMeanE2ED/' + makeFullScenarioName(testName1, sumNodes1, nodeTypes1, nodeSplit1) + '.csv'
    # with open(file_to_read, mode='r') as readFile:
    #     csv_reader = csv.reader(readFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
    #     line_count = 0
    #     for row in csv_reader:
    #         if line_count == 0:
    #             tps = row
    #         elif line_count == 1:
    #             meanTPs = row
    #         elif line_count == 2:
    #             meanE2EDs = row
    #         line_count += 1 

    fig, ax1 = plt.subplots(1, figsize=(16,12))
    # print('Min mean RTT ' + testName1 + ' = ' + str(min(meanE2EDs)) + '; Min avail cli band: ' + str(min(tps)))
    # ax1.plot(tps, [x*1000 for x in meanE2EDs], 'o', label='Variable Link Speed (VLS)')
    # popt, pcov = scipy.optimize.curve_fit(negExpFunc, tps, [x*1000 for x in meanE2EDs], p0=pZero1, maxfev=1000000, bounds=(0,np.inf))
    # with np.printoptions(precision=2):
    #     print(testName2 + ' with ' + str(nodeSplit2) + ': ' + str(popt))
    #     # regLine = np.linspace(0, max(meanUtilValues), 100)
    #     print(tps[-1])
    #     regLine = np.linspace(tps[0]-300, 10000, 1000)
    #     print(*popt)
    #     print(*pZero1)
    #     ax1.plot(regLine, negExpFunc(regLine, *popt), '-', label='VLS Automatic fit', color='yellow')
    # y = np.array([x*1000 for x in meanE2EDs])
    # x = np.array(tps)
    # textstr = 'VLS Automatic Fit:\n'   
    # textstr += makeEquationString(popt) + '\n'
    # textstr += 'MSE: ' + str(np.mean((y-negExpFunc(x, *popt))**2)) + '\n'
    # ss_res = np.dot((y - negExpFunc(x, *popt)),(y - negExpFunc(x, *popt)))
    # ymean = np.mean(y)
    # ss_tot = np.dot((y-ymean),(y-ymean))
    # textstr += 'R2: ' + str(1-ss_res/ss_tot) + '\n'
    
    numClients = []
    meanTPValues = []
    meanE2edValues = []
    stdDevValues = []
    ci95hValues = []
    minValues = []
    maxValues = []
    file_to_read = '../exports/extracted/throughput' + downlink[0] + '/' + makeFullScenarioName(testName2, numCLIs2, nodeTypes2, nodeSplit2) + '.csv'
    with open(file_to_read, mode='r') as readFile:
        csv_reader = csv.reader(readFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
        line_count = 0
        for row in csv_reader:
            # print(row)
            if line_count == 0:
                numClients = row
            # elif line_count == 1:
            #     meanTPValues = row
            #     break
            line_count += 1

    file_to_read = '../exports/extracted/endToEndDelay/' + makeFullScenarioName(testName2, numCLIs2, nodeTypes2, nodeSplit2) + '.csv'
    with open(file_to_read, mode='r') as readFile:
        csv_reader = csv.reader(readFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
        line_count = 0
        for row in csv_reader:
            if line_count == 1:
                meanE2edValues = row
            elif line_count == 2:
                stdDevValues = row
            elif line_count == 3:
                ci95hValues = row
            elif line_count == 4:
                minValues = row
            elif line_count == 5:
                maxValues = row
                break
            line_count += 1 

    meanUtilValues = [round((linkBitrate2/a),3) for a in numClients]

    print('Min mean RTT ' + testName2 + ' = ' + str(min(meanE2edValues)) + '; Min avail cli band: ' + str(min(meanUtilValues)))

    x = np.array([a for a,_ in sorted(zip(meanUtilValues, meanE2edValues))])
    y = np.array([round(b*1000,3) for _,b in sorted(zip(meanUtilValues, meanE2edValues))])

    ax1.plot(x, y, 'o', label='Simulation Results')

    # popt, pcov = scipy.optimize.curve_fit(negExpFunc, x, y, p0=pZero2, maxfev=1000000, bounds=(0,np.inf))
    
    # with np.printoptions(precision=2):
    #     print(testName2 + ' with ' + str(nodeSplit2) + ': ' + str(popt))
    #     # regLine = np.linspace(0, max(meanUtilValues), 100)
    #     print(tps[-1])
    #     regLine = np.linspace(x[0], x[-1], 1000)
    #     ax1.plot(regLine, negExpFunc(regLine, *popt), '-', label='VNC Automatic fit', color='green')
    #     textstr += 'VNC Automatic Fit:\n'   
    #     textstr += makeEquationString(popt) + '\n'
    #     y = np.array(y)
    #     x = np.array(x)
    #     textstr += 'MSE: ' + str(np.mean((y-negExpFunc(x, *popt))**2)) + '\n'
    #     ss_res = np.dot((y - negExpFunc(x, *popt)),(y - negExpFunc(x, *popt)))
    #     ymean = np.mean(y)
    #     ss_tot = np.dot((y-ymean),(y-ymean))
    #     textstr += 'R2: ' + str(1-ss_res/ss_tot) + '\n'
    regLine = np.linspace(0, x[-1], 1000)
    ax1.plot(regLine, negExpFunc(regLine, *manual), '-', label='Exponential Fit', color='red')
    # textstr = 'VNC Manual Fit:\n'   
    # textstr += makeEquationString(manual) + '\n'
    # textstr += 'MSE: ' + str(np.mean((y-negExpFunc(x, *manual))**2)) + '\n'
    # ss_res = np.dot((y - negExpFunc(x, *manual)),(y - negExpFunc(x, *manual)))
    # ymean = np.mean(y)
    # ss_tot = np.dot((y-ymean),(y-ymean))
    # textstr += 'R2: ' + str(1-ss_res/ss_tot)

    # props = dict(boxstyle='round', facecolor='white', alpha=0.2)
    # ax1.text(0, -0.18, textstr, transform=ax1.transAxes, fontsize=22, verticalalignment='top', bbox=props)

    plt.legend()
    plt.xlabel('Avail Cli Bandwidth [kbps]')
    plt.ylabel('Mean Client End-To-End Delay [ms]')
    prePath = '../exports/plots/' + makeFullScenarioName(testName1, sumNodes1, nodeTypes1, nodeSplit1) + '/'
    if not os.path.exists(prePath):
        os.makedirs(prePath)
    outPath = prePath + 'paperDelayVsAvailCliBandComp.pdf'
    fig.savefig(outPath, dpi=100, bbox_inches='tight')
    outPath2 = prePath + 'paperDelayVsAvailCliBandComp.png'
    fig.savefig(outPath2, dpi=100, bbox_inches='tight', format='png')
    plt.close('all')

# plotLSLinkSpeedMeanE2EDScatter('singleAppLSTest_SSH', 40, ['hostVID', 'hostFDO', 'hostSSH', 'hostVIP'], [0,0,1,0])
# plotLSLinkSpeedMeanE2EDScatter('singleAppLSTest_VoIP', 51, ['hostVID', 'hostFDO', 'hostSSH', 'hostVIP'], [0,0,0,1])
# plotLSLinkSpeedMeanE2EDScatter('singleAppLSTest_Video', 60, ['hostVID', 'hostFDO', 'hostSSH', 'hostVIP'], [1,0,0,0])
# plotLSLinkSpeedMeanE2EDScatter('singleAppLSTest_NewLiveVideoClient', 60, ['hostVID', 'hostFDO', 'hostSSH', 'hostVIP'], [1,0,0,0])
# plotLSLinkSpeedMeanE2EDScatter('singleAppLSTest_FileDownload2-5MB', 60, ['hostVID', 'hostFDO', 'hostSSH', 'hostVIP'], [0,1,0,0])


# plotE2edVsUtilizationExp('singleAppStressTest_VoIP', [1,5,10,15,20,25,30,35,40,45,50,55,60], ['hostVID', 'hostFDO', 'hostSSH', 'hostVIP'], [0,0,0,60], 10000, [1,1,0])
# plotE2edVsUtilizationExp('singleAppStressTest_SSH', [10,20,30,40,50,60,70,80,90,100,110,120,130,140,150,160,170,180,190,200,210,220,230,240,250,260,270,280,290,300], ['hostVID', 'hostFDO', 'hostSSH', 'hostVIP'], [0,0,300,0], 10000, [1,1,0])
# plotE2edVsUtilizationExp('singleAppStressTest_SSH_crossTraffic', [x for x in range(11,41)], ['hostVID', 'hostFDO', 'hostSSH', 'hostVIP'], [0,0,10,30], 10000, [1,0.1,0])
# plotE2edVsUtilizationExp('singleAppStressTest_SSH_crossTraffic', [x for x in range(11,31)], ['hostVID', 'hostFDO', 'hostSSH', 'hostVIP'], [20,0,10,0], 10000, [1,0.1,0])
# plotE2edVsUtilizationExp('singleAppStressTest_SSH_crossTraffic', [x for x in range(11,31)], ['hostVID', 'hostFDO', 'hostSSH', 'hostVIP'], [0,20,10,0], 10000, [1,0.1,0])

# plotE2edVsUtilizationExp('singleAppStressTest_VoIP', [1,5,10,15,20,21,22,23,24,25,26,27,28,29,30,35,40,45,50,55,60], ['hostVID', 'hostFDO', 'hostSSH', 'hostVIP'], [0,0,0,60], 10000, [1, 0.01, 0])
# plotE2edVsUtilizationExp('singleAppStressTest_VoIP_oneTenth', [x for x in range(1,7)], ['hostVID', 'hostFDO', 'hostSSH', 'hostVIP'], [0,0,0,6], 1000, [1,0.01,0])
# plotE2edVsUtilizationExp('singleAppStressTest_VoIP_oneTenth', [x for x in range(1,16)], ['hostVID', 'hostFDO', 'hostSSH', 'hostVIP'], [0,0,0,15], 1000, [0.01,0.01,0])
# plotPacketLossVsUtilizationExp('singleAppStressTest_VoIP', [1,5,10,15,20,21,22,23,24,25,26,27,28,29,30,35,40,45,50,55,60], ['hostVID', 'hostFDO', 'hostSSH', 'hostVIP'], [0,0,0,60], 10000, [0.01, 0.01, 0])
# plotPacketLossVsUtilizationExp('singleAppStressTest_VoIP_oneTenth', [x for x in range(1,7)], ['hostVID', 'hostFDO', 'hostSSH', 'hostVIP'], [0,0,0,6], 1000, [0.0001,0.0001,0])
# plotPacketLossVsUtilizationExp('singleAppStressTest_VoIP_oneTenth', [x for x in range(1,16)], ['hostVID', 'hostFDO', 'hostSSH', 'hostVIP'], [0,0,0,15], 1000, [0.0001,1,0])
# plotE2edJitterVsUtilizationExp('singleAppStressTest_VoIP', [1,5,10,15,20,21,22,23,24,25,26,27,28,29,30,35,40,45,50,55,60], ['hostVID', 'hostFDO', 'hostSSH', 'hostVIP'], [0,0,0,60], 10000, [0.01, 0.01, 0])
# plotE2edJitterVsUtilizationExp('singleAppStressTest_VoIP_oneTenth', [x for x in range(1,7)], ['hostVID', 'hostFDO', 'hostSSH', 'hostVIP'], [0,0,0,6], 1000, [0.0001,0.0001,0])
# plotE2edJitterVsUtilizationExp('singleAppStressTest_VoIP_oneTenth', [x for x in range(1,16)], ['hostVID', 'hostFDO', 'hostSSH', 'hostVIP'], [0,0,0,15], 1000, [0.0001,0.0001,0])


# plotE2edVsUtilizationExp('singleAppStressTest_SSH_smallLink', [10,20,30,40,50,60,70,80,90,100,110,120,130,140,150,160,170,180,190,200,210,220,230,240,250,260,270,280,290,300,310,320,330,340,350,360,370,380,390,400], ['hostVID', 'hostFDO', 'hostSSH', 'hostVIP'], [0,0,400,0], 800, [1,0.1,0])
# plotTcpPacketLossVsUtilizationExp('singleAppStressTest_SSH_smallLink', [10,20,30,40,50,60,70,80,90,100,110,120,130,140,150,160,170,180,190,200,210,220,230,240,250,260,270,280,290,300,310,320,330,340,350,360,370,380,390,400], ['hostVID', 'hostFDO', 'hostSSH', 'hostVIP'], [0,0,400,0], 800, [2,0.01,100],0)
# plotE2edJitterVsUtilizationExp('singleAppStressTest_SSH_smallLink', [10,20,30,40,50,60,70,80,90,100,110,120,130,140,150,160,170,180,190,200,210,220,230,240,250,260,270,280,290,300,310,320,330,340,350,360,370,380,390,400], ['hostVID', 'hostFDO', 'hostSSH', 'hostVIP'], [0,0,400,0], 800, [2,0.01,100])
# plotE2edAndQLVsUtilizationExp('singleAppStressTest_SSH_smallLink', [10,20,30,40,50,60,70,80,90,100,110,120,130,140,150,160,170,180,190,200,210,220,230,240,250,260,270,280,290,300,310,320,330,340,350,360,370,380,390,400], ['hostVID', 'hostFDO', 'hostSSH', 'hostVIP'], [0,0,400,0], 800, [1,0.1,0])
# plotE2edVsQLExp('singleAppStressTest_SSH_smallLink', [10,20,30,40,50,60,70,80,90,100,110,120,130,140,150,160,170,180,190,200,210,220,230,240,250,260,270,280,290,300,310,320,330,340,350,360,370,380,390,400], ['hostVID', 'hostFDO', 'hostSSH', 'hostVIP'], [0,0,400,0], 800, [1,0.1,0])

# plotE2edVsUtilizationExp('singleAppStressTest_NewLiveVideoClient', [1,2,3,4,5,6,7,8,9,10,15,20,25,30,35,40,45,50,55,60,65,70,75,80,85,90,95,100,105,110,115,120,125,130,135,140,145,150], ['hostVID', 'hostFDO', 'hostSSH', 'hostVIP'], [150,0,0,0], 10000, [1,1,0.25])
# plotTcpPacketLossVsUtilizationExp('singleAppStressTest_NewLiveVideoClient', [1,2,3,4,5,6,7,8,9,10,15,20,25,30,35,40,45,50,55,60,65,70,75,80,85,90,95,100,105,110,115,120,125,130,135,140,145,150], ['hostVID', 'hostFDO', 'hostSSH', 'hostVIP'], [150,0,0,0], 10000, [1,1,0.25], 0)
# plotE2edJitterVsUtilizationExp('singleAppStressTest_NewLiveVideoClient', [1,2,3,4,5,6,7,8,9,10,15,20,25,30,35,40,45,50,55,60,65,70,75,80,85,90,95,100,105,110,115,120,125,130,135,140,145,150], ['hostVID', 'hostFDO', 'hostSSH', 'hostVIP'], [150,0,0,0], 10000, [1,1,0.25])

# plotE2edVsUtilizationExp('singleAppStressTest_VideoV2', [1,5,10,15,20,25,30,35,40,45,50,55,60,65,70,75,80,85,90,95,100,105,110,115,120,125,130,135,140,145,150], ['hostVID', 'hostFDO', 'hostSSH', 'hostVIP'], [150,0,0,0], 10000, [5.92e-17, 3.97e-01, 3])
# plotTcpPacketLossVsUtilizationExp('singleAppStressTest_VideoV2', [1,5,10,15,20,25,30,35,40,45,50,55,60,65,70,75,80,85,90,95,100,105,110,115,120,125,130,135,140,145,150], ['hostVID', 'hostFDO', 'hostSSH', 'hostVIP'], [150,0,0,0], 10000, [1,0.1,0], 0)
# plotE2edJitterVsUtilizationExp('singleAppStressTest_VideoV2', [1,5,10,15,20,25,30,35,40,45,50,55,60,65,70,75,80,85,90,95,100,105,110,115,120,125,130,135,140,145,150], ['hostVID', 'hostFDO', 'hostSSH', 'hostVIP'], [150,0,0,0], 10000, [1,0.1,0])

# plotE2edVsUtilizationExp('singleAppStressTest_FileDownload2-5MB', [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40], ['hostVID', 'hostFDO', 'hostSSH', 'hostVIP'], [0,40,0,0], 10000, [0.01,0.01,1])
# plotTcpPacketLossVsUtilizationExp('singleAppStressTest_FileDownload2-5MB', [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40], ['hostVID', 'hostFDO', 'hostSSH', 'hostVIP'], [0,40,0,0], 10000, [0.0001, 0.1, 0.06], 0.007)
# plotE2edJitterVsUtilizationExp('singleAppStressTest_FileDownload2-5MB', [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40], ['hostVID', 'hostFDO', 'hostSSH', 'hostVIP'], [0,40,0,0], 10000, [0.0001, 0.1, 0.06])

# plotE2edAndQLVsUtilizationExp('singleAppStressTest_VoIP', [1,5,10,15,20,21,22,23,24,25,26,27,28,29,30,35,40,45,50,55,60], ['hostVID', 'hostFDO', 'hostSSH', 'hostVIP'], [0,0,0,60], 10000, [1,0.1,0])
# plotE2edAndQLVsUtilizationExp('singleAppStressTest_SSH_smallLink', [10,20,30,40,50,60,70,80,90,100,110,120,130,140,150,160,170,180,190,200,210,220,230,240,250,260,270,280,290,300,310,320,330,340,350,360,370,380,390,400], ['hostVID', 'hostFDO', 'hostSSH', 'hostVIP'], [0,0,400,0], 800, [1,0.1,0])
# plotE2edAndQLVsUtilizationExp('singleAppStressTest_FileDownload2-5MB', [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40], ['hostVID', 'hostFDO', 'hostSSH', 'hostVIP'], [0,40,0,0], 10000, [1,0.1,0])
# plotE2edAndQLVsUtilizationExp('singleAppStressTest_VideoV2', [1,5,10,15,20,25,30,35,40,45,50,55,60,65,70,75,80,85,90,95,100,105,110,115,120,125,130,135,140,145,150], ['hostVID', 'hostFDO', 'hostSSH', 'hostVIP'], [150,0,0,0], 10000, [1,0.1,0])
# plotE2edAndQLVsUtilizationExp('singleAppStressTest_NewLiveVideoClient', [1,2,3,4,5,6,7,8,9,10,15,20,25,30,35,40,45,50,55,60,65,70,75,80,85,90,95,100,105,110,115,120,125,130,135,140,145,150], ['hostVID', 'hostFDO', 'hostSSH', 'hostVIP'], [150,0,0,0], 10000, [1,0.1,0])

# plotRttAndQLVsUtilizationExp('singleAppStressTest_SSH_smallLink', [10,20,30,40,50,60,70,80,90,100,110,120,130,140,150,160,170,180,190,200,210,220,230,240,250,260,270,280,290,300,310,320,330,340,350,360,370,380,390,400], ['hostVID', 'hostFDO', 'hostSSH', 'hostVIP'], [0,0,400,0], 800, [1,0.1,0])
# plotRttAndQLVsUtilizationExp('singleAppStressTest_FileDownload2-5MB', [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40], ['hostVID', 'hostFDO', 'hostSSH', 'hostVIP'], [0,40,0,0], 10000, [1,0.1,0])
# plotRttAndQLVsUtilizationExp('singleAppStressTest_VideoV2', [1,5,10,15,20,25,30,35,40,45,50,55,60,65,70,75,80,85,90,95,100,105,110,115,120,125,130,135,140,145,150], ['hostVID', 'hostFDO', 'hostSSH', 'hostVIP'], [150,0,0,0], 10000, [1,0.1,0])
# plotRttAndQLVsUtilizationExp('singleAppStressTest_NewLiveVideoClient', [1,2,3,4,5,6,7,8,9,10,15,20,25,30,35,40,45,50,55,60,65,70,75,80,85,90,95,100,105,110,115,120,125,130,135,140,145,150], ['hostVID', 'hostFDO', 'hostSSH', 'hostVIP'], [150,0,0,0], 10000, [1,0.1,0])

# plotRttVsQLExp('singleAppStressTest_SSH_smallLink', [10,20,30,40,50,60,70,80,90,100,110,120,130,140,150,160,170,180,190,200,210,220,230,240,250,260,270,280,290,300,310,320,330,340,350,360,370,380,390,400], ['hostVID', 'hostFDO', 'hostSSH', 'hostVIP'], [0,0,400,0], 800, [1,0.1,0])
# plotRttVsQLExp('singleAppStressTest_FileDownload2-5MB', [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40], ['hostVID', 'hostFDO', 'hostSSH', 'hostVIP'], [0,40,0,0], 10000, [1,0.1,0])
# plotRttVsQLExp('singleAppStressTest_VideoV2', [1,5,10,15,20,25,30,35,40,45,50,55,60,65,70,75,80,85,90,95,100,105,110,115,120,125,130,135,140,145,150], ['hostVID', 'hostFDO', 'hostSSH', 'hostVIP'], [150,0,0,0], 10000, [1,0.1,0])
# plotRttVsQLExp('singleAppStressTest_NewLiveVideoClient', [1,2,3,4,5,6,7,8,9,10,15,20,25,30,35,40,45,50,55,60,65,70,75,80,85,90,95,100,105,110,115,120,125,130,135,140,145,150], ['hostVID', 'hostFDO', 'hostSSH', 'hostVIP'], [150,0,0,0], 10000, [1,0.1,0])

# plotRttJitterVsUtilizationExp('singleAppStressTest_SSH_smallLink', [10,20,30,40,50,60,70,80,90,100,110,120,130,140,150,160,170,180,190,200,210,220,230,240,250,260,270,280,290,300,310,320,330,340,350,360,370,380,390,400], ['hostVID', 'hostFDO', 'hostSSH', 'hostVIP'], [0,0,400,0], 800, [1,0.1,0])
# plotRttJitterVsUtilizationExp('singleAppStressTest_FileDownload2-5MB', [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40], ['hostVID', 'hostFDO', 'hostSSH', 'hostVIP'], [0,40,0,0], 10000, [1,0.1,0])
# plotRttJitterVsUtilizationExp('singleAppStressTest_VideoV2', [1,5,10,15,20,25,30,35,40,45,50,55,60,65,70,75,80,85,90,95,100,105,110,115,120,125,130,135,140,145,150], ['hostVID', 'hostFDO', 'hostSSH', 'hostVIP'], [150,0,0,0], 10000, [1,0.1,0])
# plotRttJitterVsUtilizationExp('singleAppStressTest_NewLiveVideoClient', [1,2,3,4,5,6,7,8,9,10,15,20,25,30,35,40,45,50,55,60,65,70,75,80,85,90,95,100,105,110,115,120,125,130,135,140,145,150], ['hostVID', 'hostFDO', 'hostSSH', 'hostVIP'], [150,0,0,0], 10000, [1,0.1,0])

# plotRttVsUtilizationExp('singleAppStressTest_SSH_smallLink', [10,20,30,40,50,60,70,80,90,100,110,120,130,140,150,160,170,180,190,200,210,220,230,240,250,260,270,280,290,300,310,320,330,340,350,360,370,380,390,400], ['hostVID', 'hostFDO', 'hostSSH', 'hostVIP'], [0,0,400,0], 800, [1,0.1,0])
# plotRttVsUtilizationExp('singleAppStressTest_FileDownload2-5MB', [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40], ['hostVID', 'hostFDO', 'hostSSH', 'hostVIP'], [0,40,0,0], 10000, [1,0.1,0])
# plotRttVsUtilizationExp('singleAppStressTest_VideoV2', [1,5,10,15,20,25,30,35,40,45,50,55,60,65,70,75,80,85,90,95,100,105,110,115,120,125,130,135,140,145,150], ['hostVID', 'hostFDO', 'hostSSH', 'hostVIP'], [150,0,0,0], 10000, [1,0.1,0])
# plotRttVsUtilizationExp('singleAppStressTest_NewLiveVideoClient', [1,2,3,4,5,6,7,8,9,10,15,20,25,30,35,40,45,50,55,60,65,70,75,80,85,90,95,100,105,110,115,120,125,130,135,140,145,150], ['hostVID', 'hostFDO', 'hostSSH', 'hostVIP'], [150,0,0,0], 10000, [0.001,0.1,0])

# plotE2edVsQLExp('singleAppStressTest_VoIP', [1,5,10,15,20,21,22,23,24,25,26,27,28,29,30,35,40,45,50,55,60], ['hostVID', 'hostFDO', 'hostSSH', 'hostVIP'], [0,0,0,60], 10000, [1,0.1,0])

# plotRttVsUsedCliBandExp('singleAppStressTest_VideoV2', [1,5,10,15,20,25,30,35,40,45,50,55,60,65,70,75,80,85,90,95,100,105,110,115,120,125,130,135,140,145,150], ['hostVID', 'hostFDO', 'hostSSH', 'hostVIP'], [150,0,0,0], 10000, [0,0,0])
# plotRttVsAvailCliBandExp('singleAppStressTest_VideoV2', [1,5,10,15,20,25,30,35,40,45,50,55,60,65,70,75,80,85,90,95,100,105,110,115,120,125,130,135,140,145,150], ['hostVID', 'hostFDO', 'hostSSH', 'hostVIP'], [150,0,0,0], 10000, [0,0,0])
# plotRttVsAvailCliBandExp('singleAppStressTest_FileDownload2-5MB', [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40], ['hostVID', 'hostFDO', 'hostSSH', 'hostVIP'], [0,40,0,0], 10000, [0.01,0.01,0])

# plotRttVsAvailCliBandComp('singleAppLSTest_Video', 60, ['hostVID', 'hostFDO', 'hostSSH', 'hostVIP'], [1,0,0,0], 'singleAppStressTest_VideoV2', [1,5,10,15,20,25,30,35,40,45,50,55,60,65,70,75,80,85,90,95,100,105,110,115,120,125,130,135,140,145,150], ['hostVID', 'hostFDO', 'hostSSH', 'hostVIP'], [150,0,0,0], 10000, [1, 0.01, 0], [1, 0.1, 0], [1600,0.0013,10])
# plotRttVsAvailCliBandComp('singleAppLSTest_NewLiveVideoClient', 60, ['hostVID', 'hostFDO', 'hostSSH', 'hostVIP'], [1,0,0,0], 'singleAppStressTest_NewLiveVideoClient', [1,2,3,4,5,6,7,8,9,10,15,20,25,30,35,40,45,50,55,60,65,70,75,80,85,90,95,100,105,110,115,120,125,130,135,140,145,150], ['hostVID', 'hostFDO', 'hostSSH', 'hostVIP'], [150,0,0,0], 10000, [1, 0.01, 0], [1, 0.1, 0], [500, 0.0011, 60])
# plotRttVsAvailCliBandComp('singleAppLSTest_SSH', 40, ['hostVID', 'hostFDO', 'hostSSH', 'hostVIP'], [0,0,1,0], 'singleAppStressTest_SSH_smallLink', [10,20,30,40,50,60,70,80,90,100,110,120,130,140,150,160,170,180,190,200,210,220,230,240,250,260,270,280,290,300,310,320,330,340,350,360,370,380,390,400], ['hostVID', 'hostFDO', 'hostSSH', 'hostVIP'], [0,0,400,0], 800, [1, 0.01, 0], [1, 0.1, 0], [900, 0.288, 1])
# plotRttVsAvailCliBandComp('singleAppLSTest_FileDownload2-5MB', 60, ['hostVID', 'hostFDO', 'hostSSH', 'hostVIP'], [0,1,0,0], 'singleAppStressTest_FileDownload2-5MB', [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40], ['hostVID', 'hostFDO', 'hostSSH', 'hostVIP'], [0,40,0,0], 10000, [1,0.01,0], [1,0.01,0], [600, 0.0006, 20])
# plotE2edVsAvailCliBandComp('singleAppLSTest_VoIP', 51, ['hostVID', 'hostFDO', 'hostSSH', 'hostVIP'], [0,0,0,1], 'singleAppStressTest_VoIP', [1,5,10,15,20,21,22,23,24,25,26,27,28,29,30,35,40,45,50,55,60], ['hostVID', 'hostFDO', 'hostSSH', 'hostVIP'], [0,0,0,60], 10000, [1, 0.01, 0], [1, 0.01, 0], [30, 0.00435, 0])

plotPaperDelayRTTVsAvailCliBandComp('singleAppLSTest_Video', 60, ['hostVID', 'hostFDO', 'hostSSH', 'hostVIP'], [1,0,0,0], 'singleAppStressTest_VideoV2', [1,5,10,15,20,25,30,35,40,45,50,55,60,65,70,75,80,85,90,95,100,105,110,115,120,125,130,135,140,145,150], ['hostVID', 'hostFDO', 'hostSSH', 'hostVIP'], [150,0,0,0], 10000, [1, 0.01, 0], [1, 0.1, 0], [800,0.0013,5]) #Video
plotPaperDelayRTTVsAvailCliBandComp('singleAppLSTest_NewLiveVideoClient', 60, ['hostVID', 'hostFDO', 'hostSSH', 'hostVIP'], [1,0,0,0], 'singleAppStressTest_NewLiveVideoClient', [1,2,3,4,5,6,7,8,9,10,15,20,25,30,35,40,45,50,55,60,65,70,75,80,85,90,95,100,105,110,115,120,125,130,135,140,145,150], ['hostVID', 'hostFDO', 'hostSSH', 'hostVIP'], [150,0,0,0], 10000, [1, 0.01, 0], [1, 0.1, 0], [250, 0.0011, 30]) #Live
plotPaperDelayRTTVsAvailCliBandComp('singleAppLSTest_SSH', 40, ['hostVID', 'hostFDO', 'hostSSH', 'hostVIP'], [0,0,1,0], 'singleAppStressTest_SSH_smallLink', [10,20,30,40,50,60,70,80,90,100,110,120,130,140,150,160,170,180,190,200,210,220,230,240,250,260,270,280,290,300,310,320,330,340,350,360,370,380,390,400], ['hostVID', 'hostFDO', 'hostSSH', 'hostVIP'], [0,0,400,0], 800, [1, 0.01, 0], [1, 0.1, 0], [450, 0.288, 0.5]) #SSH
plotPaperDelayRTTVsAvailCliBandComp('singleAppLSTest_FileDownload2-5MB', 60, ['hostVID', 'hostFDO', 'hostSSH', 'hostVIP'], [0,1,0,0], 'singleAppStressTest_FileDownload2-5MB', [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40], ['hostVID', 'hostFDO', 'hostSSH', 'hostVIP'], [0,40,0,0], 10000, [1,0.01,0], [1,0.01,0], [300, 0.0006, 10]) #File
plotPaperDelayE2edVsAvailCliBandComp('singleAppLSTest_VoIP', 51, ['hostVID', 'hostFDO', 'hostSSH', 'hostVIP'], [0,0,0,1], 'singleAppStressTest_VoIP', [1,5,10,15,20,21,22,23,24,25,26,27,28,29,30,35,40,45,50,55,60], ['hostVID', 'hostFDO', 'hostSSH', 'hostVIP'], [0,0,0,60], 10000, [1, 0.01, 0], [1, 0.01, 0], [30, 0.00435, 0]) #VoIP