import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import csv
import math
import statistics
from scipy import stats

font = {'family' : 'normal',
        'weight' : 'normal',
        'size'   : 30}

matplotlib.rc('font', **font)
matplotlib.rc('lines', linewidth=2.0)
matplotlib.rc('lines', markersize=8)

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

def boxPlotVideoEndTimes(testNames, numCLIs):
    fig, ax1 = plt.subplots(1, figsize=(16,12))
    videoEndTimes = []
    cliNums = []
    iterator = 0
    for testName in testNames:
        cliNums.extend(numCLIs[iterator])
        for numCLI in numCLIs[iterator]:
            # File that will be read
            fullScenarioName = str(testName) + '_' + str(numCLI)
            file_to_read = '../exports/vpsValues/' + str(fullScenarioName) + '.csv'
            print("Results from run: " + file_to_read)

            # Read the CSV
            df = pd.read_csv(file_to_read)
            # print(df["Video Stop Time"].tolist())[value for value in the_list if value != val]
            videoEndTimes.append([x for x in df["Video Stop Time"].tolist() if x != -1])
            quartiles = np.percentile([x for x in df["Video Stop Time"].tolist() if x != -1],[25,75]).tolist()
            # print(quartiles[1])
            # print(quartiles[1] + 1.5*(quartiles[1]-quartiles[0]))
            # print(statistics.mean([x for x in df["Video Stop Time"].tolist() if x != -1])+statistics.stdev([x for x in df["Video Stop Time"].tolist() if x != -1]))
        iterator += 1

    ax1.boxplot(videoEndTimes, positions=cliNums, autorange=True, widths=5)
    plt.xticks(rotation=60)
    ax1.set_xlabel('Number of Clients')
    ax1.set_ylabel('Video playback end [simsec]')
    fig.savefig('../exports/plots/'+str(testNames)+'_boxVideoEnds.pdf', dpi=100, bbox_inches='tight')

def prepPlotMeanThroughputs(testNames, numCLIs, cutoffType, delay):
    fig, ax1 = plt.subplots(1, figsize=(16,12))
    meanThroughputsR0R1 = []
    errR0R1 = [[],[]]
    meanThroughputsR1R0 = []
    errR1R0 = [[],[]]
    cliNums = []
    iterator = 0
    for testName in testNames:
        cliNums.extend(numCLIs[iterator])
        for numCLI in numCLIs[iterator]:
            cutoffTime = 250 # set custom cutoff here
            if cutoffType != 'customTime':
                # # File that will be read
                # fullScenarioName = str(testName) + '_' + str(numCLI)
                # file_to_read = '../exports/vpsValues/' + str(fullScenarioName) + '.csv'
                # print("Results from run: " + file_to_read)
                # # Read the CSV
                # df = pd.read_csv(file_to_read)
                # # print(df["Video Stop Time"].tolist())[value for value in the_list if value != val]
                # endTimesArray = [x for x in df["Video Stop Time"].tolist() if x != -1] # Excluded invalid clients
                # quartiles = np.percentile(endTimesArray,[25,75]).tolist()
                # mean = statistics.mean(endTimesArray)
                # standDev = statistics.stdev(endTimesArray)
                
                if cutoffType == "osdatm":
                    cutoffTime = mean+standDev
                elif cutoffType == "75p":
                    cutoffTime = quartiles[1]
                elif cutoffType == "mveo":
                    cutoffTime = quartiles[1] + 1.5*(quartiles[1] - quartiles[0])
                elif cutoffType == "100s":
                    cutoffTime = 100
            fullScenarioName = str(testName) + '_' + str(numCLI)
            file_to_read = '../exports/old/psThroughputs/' + str(fullScenarioName) + '.csv'
            print("Results from run: " + file_to_read)
            # Read the CSV
            df = pd.read_csv(file_to_read)
            cutR0R1 = [float(x)/1000 for x in df['Throughput r0r1'].tolist()[:int(cutoffTime)+1]]
            cutR1R0 = [float(x)/1000 for x in df['Throughput r1r0'].tolist()[:int(cutoffTime)+1]]

            meanTPR0R1 = statistics.mean(cutR0R1)
            lowerErrR0R1, upperErrR0R1 = stats.t.interval(0.95, len(cutR0R1)-1, loc=meanTPR0R1, scale=stats.sem(cutR0R1))
            meanTPR1R0 = statistics.mean(cutR1R0)
            lowerErrR1R0, upperErrR1R0 = stats.t.interval(0.95, len(cutR1R0)-1, loc=meanTPR1R0, scale=stats.sem(cutR1R0))

            meanThroughputsR0R1.append(meanTPR0R1)
            errR0R1[0].append(meanTPR0R1 - lowerErrR0R1)
            errR0R1[1].append(upperErrR0R1 - meanTPR0R1)
            meanThroughputsR1R0.append(meanTPR1R0)
            errR1R0[0].append(meanTPR1R0 - lowerErrR1R0)
            errR1R0[1].append(upperErrR1R0 - meanTPR1R0)

        iterator += 1
    color='tab:blue'
    if delay:
        cliNums = [int(x.split('_')[1])/1000000 for x in cliNums]
        ax1.plot(sorted(cliNums), [x for _,x in sorted(zip(cliNums,meanThroughputsR1R0))], marker='o', ls='-', label='Downlink', color=color)
        ax1.plot(sorted(cliNums), [x for _,x in sorted(zip(cliNums,meanThroughputsR0R1))], marker='o', ls='-.', label='Uplink', color=color)
        ax1.set_xlabel('Link delay [ms]')
    else:
        ax1.errorbar(sorted(cliNums), [x for _,x in sorted(zip(cliNums,meanThroughputsR1R0))], [x for _,x in sorted(zip(cliNums,errR1R0))], marker='o', ls='-', label='Downlink', color=color)
        ax1.errorbar(sorted(cliNums), [x for _,x in sorted(zip(cliNums,meanThroughputsR0R1))], [x for _,x in sorted(zip(cliNums,errR0R1))], marker='o', ls='-.', label='Uplink', color=color)
        ax1.set_xlabel('Number of Clients in Experiment')
    ax1.set_ylabel('Mean Throughput [mbps]', color=color)
    ax1.set_xlim(0,1.05*max(cliNums))
    ax1.set_ylim(0,1.05*max(meanThroughputsR1R0))
    ax1.tick_params(axis='y', labelcolor=color)
    plt.legend()
    # plt.legend(loc=(0.25,0.8))
    # plt.xticks(rotation='vertical')

    # fig.savefig('../exports/plots/'+str(testNames)+'_meanTPwithCutoff=' + cutoffType + '.pdf', dpi=100, bbox_inches='tight')
    return fig,ax1

def plotTP(testName, numCLI):
    fullScenarioName = str(testName) + '_' + str(numCLI)
    file_to_read = '../exports/psThroughputs/' + str(fullScenarioName) + '.csv'
    print("Results from run: " + file_to_read)
    # Read the CSV
    df = pd.read_csv(file_to_read)
    tpR0R1 = [float(x)/1000 for x in df['Throughput r0r1'].tolist()]
    tpR1R0 = [float(x)/1000 for x in df['Throughput r1r0'].tolist()]
    times = range(1,len(tpR1R0)+1,1)
    print(list(times))
    fig, ax1 = plt.subplots(1, figsize=(16,12))
    ax1.plot(times, tpR1R0, label="Downlink", marker='o', ls='-')
    ax1.plot(times, tpR0R1, label="Uplink", marker='o', ls='-')
    ax1.set_ylabel('Throughput [mbps]')
    ax1.set_xlabel('Simulation Time [s]')
    ax1.set_xlim(0,1.05*times[-1])
    ax1.set_ylim(0,1.05*max(tpR1R0))
    plt.legend()
    fig.savefig('../exports/plots/'+str(testName)+'_throughputs.pdf', dpi=100, bbox_inches='tight')


def prepPlotLU(testNames, numCLIs, cutoffType, delay):
    fig, ax1 = plt.subplots(1, figsize=(16,12))
    meanThroughputsR0R1 = []
    errR0R1 = [[],[]]
    meanThroughputsR1R0 = []
    errR1R0 = [[],[]]
    cliNums = []
    iterator = 0
    for testName in testNames:
        cliNums.extend(numCLIs[iterator])
        for numCLI in numCLIs[iterator]:
            cutoffTime = 250 # set custom cutoff here
            if cutoffType != 'customTime':
                # File that will be read
                fullScenarioName = str(testName) + '_' + str(numCLI)
                file_to_read = '../exports/vpsValues/' + str(fullScenarioName) + '.csv'
                print("Results from run: " + file_to_read)
                # Read the CSV
                df = pd.read_csv(file_to_read)
                # print(df["Video Stop Time"].tolist())[value for value in the_list if value != val]
                endTimesArray = [x for x in df["Video Stop Time"].tolist() if x != -1] # Excluded invalid clients
                quartiles = np.percentile(endTimesArray,[25,75]).tolist()
                mean = statistics.mean(endTimesArray)
                standDev = statistics.stdev(endTimesArray)
                
                if cutoffType == "osdatm":
                    cutoffTime = mean+standDev
                elif cutoffType == "75p":
                    cutoffTime = quartiles[1]
                elif cutoffType == "mveo":
                    cutoffTime = quartiles[1] + 1.5*(quartiles[1] - quartiles[0])
                elif cutoffType == "100s":
                    cutoffTime = 100

            fullScenarioName = str(testName) + '_' + str(numCLI)
            file_to_read = '../exports/psThroughputs/' + str(fullScenarioName) + '.csv'
            print("Results from run: " + file_to_read)
            # Read the CSV
            df = pd.read_csv(file_to_read)
            cutR0R1 = [float(x)/1000 for x in df['Throughput r0r1'].tolist()[:int(cutoffTime)+1]]
            cutR1R0 = [float(x)/1000 for x in df['Throughput r1r0'].tolist()[:int(cutoffTime)+1]]

            meanTPR0R1 = statistics.mean(cutR0R1)
            lowerErrR0R1, upperErrR0R1 = stats.t.interval(0.95, len(cutR0R1)-1, loc=meanTPR0R1, scale=stats.sem(cutR0R1))
            meanTPR1R0 = statistics.mean(cutR1R0)
            lowerErrR1R0, upperErrR1R0 = stats.t.interval(0.95, len(cutR1R0)-1, loc=meanTPR1R0, scale=stats.sem(cutR1R0))
            
            meanThroughputsR0R1.append(meanTPR0R1)
            errR0R1[0].append(meanTPR0R1 - lowerErrR0R1)
            errR0R1[1].append(upperErrR0R1 - meanTPR0R1)
            meanThroughputsR1R0.append(meanTPR1R0)
            errR1R0[0].append(meanTPR1R0 - lowerErrR1R0)
            errR1R0[1].append(upperErrR1R0 - meanTPR1R0)

        iterator += 1
    color='tab:blue'
    if delay:
        cliNums = [int(x.split('_')[1])/1000000 for x in cliNums]
        ax1.plot(sorted(cliNums), [x for _,x in sorted(zip(cliNums,meanThroughputsR1R0))], marker='o', ls='-', label='Downlink', color=color)
        ax1.plot(sorted(cliNums), [x for _,x in sorted(zip(cliNums,meanThroughputsR0R1))], marker='o', ls='-.', label='Uplink', color=color)
        ax1.set_xlabel('Link delay [ms]')
    else:
        ax1.errorbar(sorted(cliNums), [x for _,x in sorted(zip(cliNums,meanThroughputsR1R0))], [x for _,x in sorted(zip(cliNums,errR1R0))], marker='o', ls='-', label='Downlink', color=color)
        ax1.errorbar(sorted(cliNums), [x for _,x in sorted(zip(cliNums,meanThroughputsR0R1))], [x for _,x in sorted(zip(cliNums,errR0R1))], marker='o', ls='-.', label='Uplink', color=color)
        ax1.set_xlabel('Number of Clients in Experiment')
    ax1.set_ylabel('Link Utilisation [%]', color=color)
    ax1.set_xlim(0,1.05*max(cliNums))
    ax1.set_ylim(0,1.05*max(meanThroughputsR1R0))
    ax1.tick_params(axis='y', labelcolor=color)
    plt.legend()
    # plt.legend(loc=(0.45,0.08))
    # plt.xticks(rotation='vertical')

    # fig.savefig('../exports/plots/'+str(testNames)+'_meanTPwithCutoff=' + cutoffType + '.pdf', dpi=100, bbox_inches='tight')
    return fig,ax1

def prepPlotMOS(fig,ax1,testNames,numCLIs, delay):
    avgMosVals = []
    errMosVals = [[],[]]
    cliNums = []
    iterator = 0
    for testName in testNames:
        cliNums.extend(numCLIs[iterator])
        for numCLI in numCLIs[iterator]:
            # File that will be read
            fullScenarioName = str(testName) + '_' + str(numCLI)
            file_to_read = '../exports/old/mosValues/' + str(fullScenarioName) + '.csv'
            print("Results from run: " + file_to_read)

            # Read the CSV
            df = pd.read_csv(file_to_read)
            mosVals = [float(x) for x in df["MOS Value"].tolist()]
            meanMos = statistics.mean(mosVals)
            lowerErr, upperErr = stats.t.interval(0.95, len(mosVals)-1, loc=statistics.mean(mosVals), scale=stats.sem(mosVals))
            avgMosVals.append(meanMos)
            print(meanMos)
            errMosVals[0].append(meanMos - lowerErr) # https://en.wikipedia.org/wiki/Error_bar - use 95% confidence interval
            errMosVals[1].append(upperErr - meanMos) # https://en.wikipedia.org/wiki/Error_bar - use 95% confidence interval
            # errMosVals.append(stats.sem(mosVals)) # https://en.wikipedia.org/wiki/Error_bar - use standard error, or rather standard error of the mean
        iterator += 1
    ax = None
    color = 'tab:blue'
    if ax1 == None:
        fig, ax = plt.subplots(1, figsize=(16,12))
    else:
        color = 'tab:red'
        ax = ax1.twinx()
    if delay:
        cliNums = [int(x.split('_')[1])/1000000 for x in cliNums]
        ax.plot(sorted(cliNums), [x for _,x in sorted(zip(cliNums,avgMosVals))], marker='o', color=color)
    else:
        ax.errorbar(sorted(cliNums), [x for _,x in sorted(zip(cliNums,avgMosVals))], [x for _,x in sorted(zip(cliNums,errMosVals))], color=color)
    ax.set_ylabel('Mean MOS Value', color=color)
    ax.tick_params(axis='y', labelcolor=color)
    ax.set_ylim(0.95,5.05)
    if ax1 == None:
        ax.set_xlabel('Number of Clients in Experiment')
        ax.set_xlim(0,1.05*max(cliNums))
    return fig, ax

def plotMOScdf(testName, numCLI):
    avgMosVals = []
    errMosVals = [[],[]]
    cliNums = []
    iterator = 0
    # File that will be read
    fullScenarioName = str(testName) + '_' + str(numCLI)
    file_to_read = '../exports/mosValues/' + str(fullScenarioName) + '.csv'
    print("Results from run: " + file_to_read)

    # Read the CSV
    df = pd.read_csv(file_to_read)
    mosVals = [statistics.mean([float(y) for y in x.replace('[','').replace(']','').split(', ')]) for x in df["MOS Value"].tolist()]
    print(mosVals)

    fig, ax = partialCDFBegin()
    partialCDFPlotData(fig, ax, mosVals, 'All Clients','o-', 'r')
    partialCDFEnd(fig,ax,'', 'Mean MOS Value', '../exports/plots/'+str(testName)+'_mosCDF.pdf')

    # ax = None
    # color = 'tab:blue'
    # if ax1 == None:
    #     fig, ax = plt.subplots(1, figsize=(16,12))
    # else:
    #     color = 'tab:red'
    #     ax = ax1.twinx()
    # if delay:
    #     cliNums = [int(x.split('_')[1])/1000000 for x in cliNums]
    #     ax.plot(sorted(cliNums), [x for _,x in sorted(zip(cliNums,avgMosVals))], marker='o', color=color)
    # else:
    #     ax.errorbar(sorted(cliNums), [x for _,x in sorted(zip(cliNums,avgMosVals))], [x for _,x in sorted(zip(cliNums,errMosVals))], color=color)
    # ax.set_ylabel('Mean MOS Value', color=color)
    # ax.tick_params(axis='y', labelcolor=color)
    # ax.set_ylim(0.95,5.05)
    # if ax1 == None:
    #     ax.set_xlabel('Number of Clients in Experiment')
    #     ax.set_xlim(0,1.05*max(cliNums))
    # return fig, ax

def prepPlotVBR(fig,ax1,testNames,numCLIs):
    meanVbrVals = []
    errVbrVals = [[],[]]
    cliNums = []
    iterator = 0
    for testName in testNames:
        cliNums.extend(numCLIs[iterator])
        for numCLI in numCLIs[iterator]:
            # File that will be read
            fullScenarioName = str(testName) + '_' + str(numCLI)
            file_to_read = '../exports/vbrValues/' + str(fullScenarioName) + '.csv'
            print("Results from run: " + file_to_read)

            # Read the CSV
            df = pd.read_csv(file_to_read)
            bitrateList = df["Video Bitrates"].tolist()
            vbrVals = []
            for elem in bitrateList:
                vbrVals.extend([int(x) for x in elem.replace('[','').replace(']','').replace(' ','').split(',')[1:]])
            meanVbr = statistics.mean(vbrVals)
            lowerErr, upperErr = stats.t.interval(0.95, len(vbrVals)-1, loc=statistics.mean(vbrVals), scale=stats.sem(vbrVals))
            meanVbrVals.append(meanVbr)
            errVbrVals[0].append(meanVbr - lowerErr) # https://en.wikipedia.org/wiki/Error_bar - use 95% confidence interval
            errVbrVals[1].append(upperErr - meanVbr) # https://en.wikipedia.org/wiki/Error_bar - use 95% confidence interval
        iterator += 1
    ax = None
    color = 'tab:blue'
    if ax1 == None:
        fig, ax = plt.subplots(1, figsize=(16,12))
    else:
        color = 'tab:red'
        ax = ax1.twinx()
    ax.errorbar(sorted(cliNums), [x for _,x in sorted(zip(cliNums,meanVbrVals))], [x for _,x in sorted(zip(cliNums,errVbrVals))], color=color)
    ax.set_ylabel('Mean Video Bitrate (kbps)', color=color)
    ax.tick_params(axis='y', labelcolor=color)
    ax.set_ylim(0.95*500,1.05*3000)
    if ax1 == None:
        ax.set_xlabel('Number of Clients in Experiment')
        ax.set_xlim(0,1.05*max(cliNums))
    return fig, ax

def prepPlotVSST(fig,ax1,testNames,numCLIs):
    meanVst = []
    meanVet = []
    errVstVals = [[],[]]
    errVetVals = [[],[]]
    cliNums = []
    iterator = 0
    for testName in testNames:
        cliNums.extend(numCLIs[iterator])
        for numCLI in numCLIs[iterator]:
            # File that will be read
            fullScenarioName = str(testName) + '_' + str(numCLI)
            file_to_read = '../exports/vpsValues/' + str(fullScenarioName) + '.csv'
            print("Results from run: " + file_to_read)

            # Read the CSV
            df = pd.read_csv(file_to_read)
            # print(df)
            vst = [] # Video playback start times
            vet = [] # Video playback end times
            for cliNum in range(len(df)):
                vst.append(float(df['Video Start Time'].iat[cliNum])) # Extract video playback start time
                vet.append(float(df['Video Stop Time'].iat[cliNum])) # Extract video playback end time
            meanVst.append(statistics.mean(vst))
            meanVet.append(statistics.mean(vet))
            lowerErrVst, upperErrVst = stats.t.interval(0.95, len(vst)-1, loc=statistics.mean(vst), scale=stats.sem(vst))
            lowerErrVet, upperErrVet = stats.t.interval(0.95, len(vet)-1, loc=statistics.mean(vet), scale=stats.sem(vet))
            errVstVals[0].append(statistics.mean(vst) - lowerErrVst) # https://en.wikipedia.org/wiki/Error_bar - use 95% confidence interval
            errVstVals[1].append(upperErrVst - statistics.mean(vst)) # https://en.wikipedia.org/wiki/Error_bar - use 95% confidence interval
            errVetVals[0].append(statistics.mean(vet) - lowerErrVet) # https://en.wikipedia.org/wiki/Error_bar - use 95% confidence interval
            errVetVals[1].append(upperErrVet - statistics.mean(vet)) # https://en.wikipedia.org/wiki/Error_bar - use 95% confidence interval
        iterator += 1
    ax = None
    color = 'tab:blue'
    if ax1 == None:
        fig, ax = plt.subplots(1, figsize=(16,12))
    else:
        color = 'tab:red'
        ax = ax1.twinx()
    ax.errorbar(sorted(cliNums), [x for _,x in sorted(zip(cliNums,meanVst))], [x for _,x in sorted(zip(cliNums,errVstVals))], marker='o', ls='-', label='Video Playback Start', color=color)
    ax.errorbar(sorted(cliNums), [x for _,x in sorted(zip(cliNums,meanVet))], [x for _,x in sorted(zip(cliNums,errVetVals))], marker='o', ls='-.', label='Video Playback End', color=color)
    ax.set_ylabel('Simulation Time [s]', color=color)
    ax.tick_params(axis='y', labelcolor=color)
    ax.set_ylim(0,1.05*250)
    plt.legend(loc=(0.45,0.7))
    if ax1 == None:
        ax.set_xlabel('Number of Clients in Experiment')
        ax.set_xlim(0,1.05*max(cliNums))
    return fig, ax

def prepPlotST(fig,ax1,testNames,numCLIs):
    meanStVals = []
    errStVals = [[],[]]
    cliNums = []
    iterator = 0
    for testName in testNames:
        cliNums.extend(numCLIs[iterator])
        for numCLI in numCLIs[iterator]:
            # File that will be read
            fullScenarioName = str(testName) + '_' + str(numCLI)
            file_to_read = '../exports/vpsValues/' + str(fullScenarioName) + '.csv'
            print("Results from run: " + file_to_read)

            # Read the CSV
            df = pd.read_csv(file_to_read)
            stt = [] # Video stalling times
            # print(df)
            for cliNum in range(len(df)):
                # Extract stalling durations

                tempSTT = [x.replace('[','').replace(']','').replace(' ','').split(',') for x in df['Stallings'].iat[cliNum].split('], [')]
                sttFloats = []
                if len(tempSTT[0]) > 1:
                    for elem in tempSTT:
                        sttFloats.append(float(elem[2]))
                if len(sttFloats) > 0: stt.extend(sttFloats)
            if len(stt) > 0:
                meanStVals.append(statistics.mean(stt))
                lowerErr, upperErr = stats.t.interval(0.95, len(stt)-1, loc=statistics.mean(stt), scale=stats.sem(stt))
                errStVals[0].append(statistics.mean(stt) - lowerErr) # https://en.wikipedia.org/wiki/Error_bar - use 95% confidence interval
                errStVals[1].append(upperErr - statistics.mean(stt)) # https://en.wikipedia.org/wiki/Error_bar - use 95% confidence interval
            else:
                meanStVals.append(0)
                errStVals[0].append(0) # https://en.wikipedia.org/wiki/Error_bar - use 95% confidence interval
                errStVals[1].append(0) # https://en.wikipedia.org/wiki/Error_bar - use 95% confidence interval
        iterator += 1
    ax = None
    color = 'tab:blue'
    if ax1 == None:
        fig, ax = plt.subplots(1, figsize=(16,12))
    else:
        color = 'tab:red'
        ax = ax1.twinx()
    ax.errorbar(sorted(cliNums), [x for _,x in sorted(zip(cliNums,meanStVals))], [x for _,x in sorted(zip(cliNums,errStVals))], color=color)
    ax.set_ylabel('Mean Stalling Duration [s]', color=color)
    ax.tick_params(axis='y', labelcolor=color)
    ax.set_ylim(min([x-y for x,y in zip(meanStVals, errStVals[0])]),1.05*(max([sum(x) for x in zip(meanStVals, errStVals[1])])))
    if ax1 == None:
        ax.set_xlabel('Number of Clients in Experiment')
        ax.set_xlim(0,1.05*max(cliNums))
    return fig, ax

def plotMOSandTP(testNames, numCLIs, cutoffType, delay):
    fig, ax1 = prepPlotMeanThroughputs(testNames, numCLIs, cutoffType, delay)
    fig, ax2 = prepPlotMOS(fig, ax1, testNames, numCLIs, delay)
    if delay:
        fig.savefig('../exports/plots/'+str(testNames)+'_meanMOSandTPsDelay' + str(numCLIs[0][0].split('_')[0]) + '.pdf', dpi=100, bbox_inches='tight')
    else:
        fig.savefig('../exports/plots/'+str(testNames)+'_meanMOSandTPs.pdf', dpi=100, bbox_inches='tight')

def plotMOSandLU(testNames, numCLIs, cutoffType, delay):
    fig, ax1 = prepPlotLU(testNames, numCLIs, cutoffType, delay)
    fig, ax2 = prepPlotMOS(fig, ax1, testNames, numCLIs, delay)
    if delay:
        fig.savefig('../exports/plots/'+str(testNames)+'__meanMOSandLUsDelay' + str(numCLIs[0][0].split('_')[0]) + '.pdf', dpi=100, bbox_inches='tight')
    else:
        fig.savefig('../exports/plots/'+str(testNames)+'_meanMOSandLUs.pdf', dpi=100, bbox_inches='tight')

def plotVBRandLU(testNames, numCLIs, cutoffType):
    fig, ax1 = prepPlotLU(testNames, numCLIs, cutoffType, False)
    fig, ax2 = prepPlotVBR(fig, ax1, testNames, numCLIs)

    fig.savefig('../exports/plots/'+str(testNames)+'_meanVBRandLUs.pdf', dpi=100, bbox_inches='tight')

def plotVBRandTP(testNames, numCLIs, cutoffType):
    fig, ax1 = prepPlotMeanThroughputs(testNames, numCLIs, cutoffType, False)
    fig, ax2 = prepPlotVBR(fig, ax1, testNames, numCLIs)
    fig.savefig('../exports/plots/'+str(testNames)+'_meanVBRandTPs.pdf', dpi=100, bbox_inches='tight')

def plotMOSandVBR(testNames, numCLIs):
    fig, ax1 = prepPlotVBR(None, None, testNames, numCLIs)
    fig, ax2 = prepPlotMOS(fig, ax1, testNames, numCLIs, False)
    
    fig.savefig('../exports/plots/'+str(testNames)+'_avgMOSandAvgVBR.pdf', dpi=100, bbox_inches='tight')

def plotVSSTandST(testNames, numCLIs):
    fig, ax1 = prepPlotVSST(None, None, testNames, numCLIs)
    fig, ax2 = prepPlotST(fig, ax1, testNames, numCLIs)

    fig.savefig('../exports/plots/'+str(testNames)+'_meanVSSTandST.pdf', dpi=100, bbox_inches='tight')

def plotSTandMOS(testNames, numCLIs):
    fig, ax1 = prepPlotST(None, None, testNames, numCLIs)
    fig, ax2 = prepPlotMOS(fig, ax1, testNames, numCLIs, False)

    fig.savefig('../exports/plots/'+str(testNames)+'_meanVSTandMOS.pdf', dpi=100, bbox_inches='tight')

def plotMOSandTPDelay(testNames, numCLIs, cutoffType):
    fig, ax1 = prepPlotMeanThroughputs(testNames, numCLIs, cutoffType, False)
    fig, ax2 = prepPlotMOS(fig, ax1, testNames, numCLIs, False)
    fig.savefig('../exports/plots/'+str(testNames)+'_meanMOSandTPs.pdf', dpi=100, bbox_inches='tight')

def plotMOSandDelay(testNames, numCLIs, cutoffType):
    fig, ax1 = prepPlotLU(testNames, numCLIs, cutoffType, False)
    fig, ax2 = prepPlotMOS(fig, ax1, testNames, numCLIs, False)
    fig.savefig('../exports/plots/'+str(testNames)+'_meanMOSandLUs.pdf', dpi=100, bbox_inches='tight')

def plotThroughputsBoxTest(testNames, numCLIs):
    fig, ax1 = plt.subplots(1, figsize=(16,12))
    r1r0Info = []
    cliNums = []
    iterator = 0
    for testName in testNames:
        cliNums.extend(numCLIs[iterator])
        for numCLI in numCLIs[iterator]:
            fullScenarioName = str(testName) + '_' + str(numCLI)
            file_to_read = '../exports/psThroughputs/' + str(fullScenarioName) + '.csv'
            print("Results from run: " + file_to_read)

            # Read the CSV
            df = pd.read_csv(file_to_read)
            # print(df)
            # r0r1 = [float(x.replace('[','').replace(']','').replace(' ','')) for x in list(df)[0].split(',')]
            r1r0 = [float(x.replace('[','').replace(']','').replace(' ','')) for x in list(df)[1].split(',')]
            r1r0 = r1r0[:150]
            # r1r0 = list(filter(lambda a: a != 0, r1r0))
            # print(r0r1)
            # print(r1r0)
            r1r0Info.append(r1r0)
    # print(len(r1r0Info))
    # print(len(r1r0Info))
    ax1.boxplot(r1r0Info, positions=cliNums, autorange=True, widths=5)
    ax1.plot(cliNums, [statistics.median(x) for x in r1r0Info], '-o', color='r')
    ax1.plot(cliNums, [statistics.mean(x) for x in r1r0Info], '-o', color='g')
    plt.xticks(rotation=60)
    ax1.set_xlabel('Number of Clients')
    ax1.set_ylabel('Throughput [kbps]')
    fig.savefig('../exports/plots/'+str(testNames)+'_tpsBoxr1r0.pdf', dpi=100, bbox_inches='tight')

testNames = []
numCLIList = []

### TCP Video Client Plots ###
# testNames.append("tcpVideoClientTest")
# testNames.append("tcpVideoClientTestV2")
# numCLIList.append([10,20,30,40,50,60,70,80,90,100,110,120,130,140,150,160,170,180,190,200,210,220])
# testNames.append("tcpVideoClientTest_ext1")
# numCLIList.append([2,4,6,8,12,14,16,18,22,24,26,28,32,34,36,38])
# testNames.append("tcpVideoClientTest_ext2")
# numCLIList.append([102,104,106,108,112,114,116,118,122,124,126,128])
# testNames.append("tcpVideoClientTest_ext3")
# numCLIList.append([230,240,250,260,270,280,290,300])

# testNames.append("tcpVideoClientTestV3a")
# numCLIList.append([10,20,30,40,50,60,70,80,90,100,110,120,130,140,150,160,170,180,190,200,210,220,240,250,260,270,280,290,300])
# testNames.append("tcpVideoClientTestV3b")
# numCLIList.append([10,20,30,40,50,60,70,80,90,100,110,120,130,140,150,160,170,180,190,200,210,220,240,250,260,270,280,290,300])

# plotMOSandTP(testNames, numCLIList, '100s', False)
# plotMOSandLU(testNames, numCLIList, '100s', False)
# plotVBRandLU(testNames, numCLIList, '100s')
# plotVBRandTP(testNames, numCLIList, '100s')
# plotMOSandVBR(testNames, numCLIList)
# plotVSSTandST(testNames, numCLIList)
# plotSTandMOS(testNames, numCLIList)
# boxPlotVideoEndTimes(testNames, numCLIList)


### File Download Client Plots ###
testNames.append("fileDownloadClientTest")
numCLIList.append([1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40])
testNames.append("fileDownloadClientTest_ext1")
numCLIList.append([60,80,100])
plotMOSandTP(testNames, numCLIList, '100s', False)
# plotMOSandLU(testNames, numCLIList, '100s', False)


### SSH Client Plots ###
## V1 ##
# testNames.append("sshClientTest")
# testNames.append("sshClientTest_ext1")
# numCLIList.append([1,5,10,15,20,30,40,50,60,70,80,90,100,110,120,130,140,150,160,170,180,190,200,210,220,230,240,250,260,270,280,290,300])
# numCLIList.append([1000,1500,2000,2500,3000,3500,4000])
# plotMOSandTP(testNames, numCLIList, 'customTime', False)
# plotMOSandLU(testNames, numCLIList, 'customTime', False)
## V3 ##
# testNames.append("sshClientTestV3")
# tempNumCLIList = []
# for numCli in [50]:
#     for delay in [10,100,1000,10000,100000,1000000,2000000,3000000,4000000,5000000,6000000,7000000,8000000,9000000,10000000,11000000,12000000,13000000,14000000,15000000,16000000,17000000,18000000,19000000,20000000,30000000,40000000,50000000,60000000,70000000,80000000,90000000,100000000,200000000,300000000,400000000,500000000,600000000,700000000,800000000,900000000,1000000000]:
#         tempNumCLIList.append(str(numCli) + "_" + str(delay))
# numCLIList.append(tempNumCLIList)
# plotMOSandTP(testNames, numCLIList, 'customTime', True)
# plotMOSandLU(testNames, numCLIList, 'customTime', True)

### VoIP Client Plots ###
## V1 ##
# testNames.append("voipCliSrvTest")
# numCLIList.append([1,2,3,4,5,10,15,20,30,40,50,60,70,80,90,100,110])
# plotMOSandTP(testNames, numCLIList, 'customTime', False)
# plotMOSandLU(testNames, numCLIList, 'customTime', False)
## V2 ##
# testNames.append("voipCliSrvTestV2")
# testNames.append("voipCliSrvTestV2_ext1")
# tempNumCLIList = []
# for numCli in [1]:
#     for delay in [10,100,1000,10000,100000,1000000,2000000,3000000,4000000,5000000,6000000,7000000,8000000,9000000,10000000,11000000,12000000,13000000,14000000,15000000,16000000,17000000,18000000,19000000,20000000,30000000,40000000,50000000,60000000,70000000,80000000,90000000,100000000,200000000,300000000,400000000,500000000,1000000000]:
#         tempNumCLIList.append(str(numCli) + "_" + str(delay))
# numCLIList.append(tempNumCLIList)
# tempNumCLIList = []
# for numCli in [1]:
#     for delay in [600000000,700000000,800000000,900000000]:
#         tempNumCLIList.append(str(numCli) + "_" + str(delay))
# numCLIList.append(tempNumCLIList)
# plotMOSandTP(testNames, numCLIList, 'customTime', True)
# plotMOSandLU(testNames, numCLIList, 'customTime', True)

# plotTP("baselineTest", 120)
# plotMOScdf("baselineTest", 120)