import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import csv
import math
import statistics
from scipy import stats
import scipy
import os
import copy

font = {'weight' : 'normal',
        'size'   : 40}

matplotlib.rc('font', **font)
matplotlib.rc('lines', linewidth=2.0)
matplotlib.rc('lines', markersize=8)

def plotMap(alphas, betas, data, dataName, outFileName, minV, maxV):
    fig, ax = plt.subplots(1, figsize=(16,12))
    print(dataName, minV, maxV)
    norm = matplotlib.colors.Normalize(vmin=minV, vmax=maxV)
    cmap = plt.cm.get_cmap(name='viridis',lut=1024)
    # print(data)
    im = ax.imshow(np.array(data), norm=norm, cmap=cmap)
    cbar = ax.figure.colorbar(im, ax=ax, norm=norm, cmap=cmap)
    cbar.ax.set_ylabel(dataName, rotation=-90, va="bottom")
    cbar.set_clim(minV, maxV)
    ax.set_yticks(np.arange(len(alphas)))
    ax.set_xticks(np.arange(len(betas)))
    ax.set_yticklabels([round(x,2) for x in alphas])
    ax.set_xticklabels([round(x,2) for x in betas])
    labels = ax.get_xticklabels() # get x labels
    # for i,l in enumerate(labels):
    #     if(i%3 != 0): labels[i] = '' # skip even labels
    ax.set_xticklabels(labels, rotation=90) # set new labels
    labels = ax.get_yticklabels() # get y labels
    # for i,l in enumerate(labels):
    #     if(i%3 != 0): labels[i] = '' # skip even labels
    ax.set_yticklabels(labels, rotation=0) # set new labels
    plt.ylabel("Alpha")
    plt.xlabel("Beta")
    if not os.path.exists('plots/'):
        os.makedirs('plots/')
    outPath = 'plots/' + outFileName + '.pdf'
    fig.savefig(outPath, dpi=100, bbox_inches='tight')
    plt.close('all')

def plotAlphaBeta(fileName):
    print(fileName)
    alpha = []
    beta = []
    # assignments = []
    objFunc = []
    minMos = []
    maxMos = []
    avgMos = []
    mosFairness = []

    file_to_read = fileName+'.csv'
    with open(file_to_read, mode='r') as readFile:
        csv_reader = csv.reader(readFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                alpha = row
            elif line_count == 1:
                beta = row
            # elif line_count == 2:
            #     assignments = row
            elif line_count == 3:
                objFunc = row
            elif line_count == 4:
                minMos = row
            elif line_count == 5:
                maxMos = row
            elif line_count == 6:
                avgMos = row
            elif line_count == 7:
                mosFairness = row
            line_count += 1 
    
    alphas = sorted(list(set(alpha)))
    betas = sorted(list(set(beta)))
    objFuncMap = []
    minMosMap = []
    maxMosMap = []
    avgMosMap = []
    mosFairnessMap = []
    # print(len(objFunc))
    for i in range(len(alphas)):
        objFuncMap.append([])
        minMosMap.append([])
        maxMosMap.append([])
        avgMosMap.append([])
        mosFairnessMap.append([])
        for j in range(len(betas)):
            objFuncMap[i].append(-1)
            minMosMap[i].append(-1)
            maxMosMap[i].append(-1)
            avgMosMap[i].append(-1)
            mosFairnessMap[i].append(-1)
    for k in range(len(objFunc)):
        objFuncMap[alphas.index(alpha[k])][betas.index(beta[k])] = objFunc[k]
        minMosMap[alphas.index(alpha[k])][betas.index(beta[k])] = eval(minMos[k])[2]
        maxMosMap[alphas.index(alpha[k])][betas.index(beta[k])] = eval(maxMos[k])[2]
        avgMosMap[alphas.index(alpha[k])][betas.index(beta[k])] = avgMos[k]
        mosFairnessMap[alphas.index(alpha[k])][betas.index(beta[k])] = mosFairness[k]

    plotMap(alphas, betas, objFuncMap, 'Objective Function', fileName+'ObjFunc', min(objFunc)-0.01, max(objFunc))
    plotMap(alphas, betas, minMosMap, 'Minimal MOS Score', fileName+'MinMos', min([eval(x)[2] for x in minMos])-0.01, max([eval(x)[2] for x in minMos]))
    plotMap(alphas, betas, maxMosMap, 'Maximal MOS Score', fileName+'MaxMos', min([eval(x)[2] for x in maxMos])-0.01, max([eval(x)[2] for x in maxMos]))
    plotMap(alphas, betas, avgMosMap, 'Mean MOS Score', fileName+'AvgMos', min(avgMos)-0.01, max(avgMos))
    plotMap(alphas, betas, mosFairnessMap, 'MOS Fairness', fileName+'MosFairness', min(mosFairness)-0.01, max(mosFairness))

    # plotMap(alphas, betas, objFuncMap, 'Objective Function', fileName+'ObjFunc', 0.0, 1.0)
    # plotMap(alphas, betas, minMosMap, 'Minimal Utility', fileName+'MinMos', 1.0, 5.0)
    # plotMap(alphas, betas, maxMosMap, 'Maximal Utility', fileName+'MaxMos', 1.0, 5.0)
    # plotMap(alphas, betas, avgMosMap, 'Mean Utility', fileName+'AvgMos', 1.0, 5.0)
    # plotMap(alphas, betas, mosFairnessMap, 'QoE Fairness', fileName+'MosFairness', 0.0, 1.0)


def plotAlpha(fileName):
    print(fileName)
    alpha = []
    # beta = []
    assignments = []
    objFunc = []
    minMos = []
    maxMos = []
    avgMos = []
    mosFairness = []
    meanBandSlice = []
    estimDelaySlice = []
    estMosSlice = []

    file_to_read = fileName+'.csv'
    with open(file_to_read, mode='r') as readFile:
        csv_reader = csv.reader(readFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                alpha = row
            # elif line_count == 1:
            #     beta = row
            elif line_count == 2:
                assignments = row
            elif line_count == 3:
                objFunc = row
            elif line_count == 4:
                minMos = row
            elif line_count == 5:
                maxMos = row
            elif line_count == 6:
                avgMos = row
            elif line_count == 7:
                mosFairness = row
            elif line_count == 8:
                meanBandSlice = row
            elif line_count == 9:
                estimDelaySlice = row
            elif line_count == 10:
                estMosSlice = row
            line_count += 1

    alphas = [round(x,2) for x in alpha]

    fig, ax1 = plt.subplots(1, figsize=(16,12))
    ax1.plot(alphas, [eval(x)[2] for x in minMos], label='Minimal Utility', marker='o', ls='--')
    ax1.plot(alphas, [eval(x)[2] for x in maxMos], label='Maximal Utility', marker='o', ls='--')
    ax1.plot(alphas, avgMos, label='Mean Utility', marker='o', ls='-')
    ax1.set_ylim(0.95,5.05)
    ax1.set_ylabel('Utility')
    ax1.set_xlabel('Alpha Parameter')
    plt.legend()
    plt.grid(True)
    if not os.path.exists('plots/alphaTests/'+fileName+'/'):
        os.makedirs('plots/alphaTests/'+fileName+'/')
    outPath = 'plots/alphaTests/'+fileName+'/mos.pdf'
    fig.savefig(outPath, dpi=100, bbox_inches='tight')
    outPath = 'plots/alphaTests/'+fileName+'/mos.png'
    fig.savefig(outPath, dpi=100, bbox_inches='tight')
    plt.close('all')

    fig, ax1 = plt.subplots(1, figsize=(16,12))
    ax1.plot(alphas, mosFairness, label='QoE Fairness', marker='o', ls='-')
    ax1.plot(alphas, objFunc, label='Objective Function', marker='o', ls='-')
    ax1.set_ylim(-0.01,1.01)
    ax1.set_ylabel('Value')
    ax1.set_xlabel('Alpha Parameter')
    plt.legend()
    plt.grid(True)
    outPath = 'plots/alphaTests/'+fileName+'/fairnessObjective.pdf'
    fig.savefig(outPath, dpi=100, bbox_inches='tight')
    outPath = 'plots/alphaTests/'+fileName+'/fairnessObjective.png'
    fig.savefig(outPath, dpi=100, bbox_inches='tight')
    plt.close('all')

    fig, ax1 = plt.subplots(1, figsize=(16,12))
    for x in eval(assignments[0]):
        sliceXass = []
        for ass in assignments:
            sliceXass.append(eval(ass)[x])
        ax1.plot(alphas, sliceXass, label='Slice ' + x, marker='o', ls='-')
    ax1.set_ylim(0,80)
    ax1.set_ylabel('Assigned Resource Blocks')
    ax1.set_xlabel('Alpha Parameter')
    plt.legend()
    plt.grid(True)
    outPath = 'plots/alphaTests/'+fileName+'/rbAssignment.pdf'
    fig.savefig(outPath, dpi=100, bbox_inches='tight')
    outPath = 'plots/alphaTests/'+fileName+'/rbAssignment.png'
    fig.savefig(outPath, dpi=100, bbox_inches='tight')
    plt.close('all')

    fig, ax1 = plt.subplots(1, figsize=(16,12))
    for x in eval(estMosSlice[0]):
        for y in eval(estMosSlice[0])[x]:
            cliTypeMeanMos = []
            for run in estMosSlice:
                cliTypeMeanMos.append(eval(run)[x][y])
            # print(x, y, cliTypeMeanMos)
            ax1.plot(alphas, cliTypeMeanMos, label=x + ' -> ' + y, marker='o', ls='-')
    ax1.plot(alphas, avgMos, label='Mean Utility', marker='o', ls='-')
    ax1.set_ylim(0.95,5.05)
    ax1.set_ylabel('Utility')
    ax1.set_xlabel('Alpha Parameter')
    plt.legend()
    plt.grid(True)
    outPath = 'plots/alphaTests/'+fileName+'/meanCliTypeMos.pdf'
    fig.savefig(outPath, dpi=100, bbox_inches='tight')
    outPath = 'plots/alphaTests/'+fileName+'/meanCliTypeMos.png'
    fig.savefig(outPath, dpi=100, bbox_inches='tight')
    plt.close('all')
    
    fig, ax1 = plt.subplots(1, figsize=(16,12))
    for x in eval(meanBandSlice[0]):
        for y in eval(meanBandSlice[0])[x]:
            cliTypeMeanBand = []
            for run in meanBandSlice:
                cliTypeMeanBand.append(eval(run)[x][y])
            # print(x, y, cliTypeMeanMos)
            ax1.plot(alphas, cliTypeMeanBand, label=x + ' -> ' + y, marker='o', ls='-')
    # ax1.set_ylim(0,800)
    ax1.set_ylabel('Mean Bandwidth per Client [kbps]')
    ax1.set_xlabel('Alpha Parameter')
    plt.legend()
    plt.grid(True)
    outPath = 'plots/alphaTests/'+fileName+'/meanCliTypeBand.pdf'
    fig.savefig(outPath, dpi=100, bbox_inches='tight')
    outPath = 'plots/alphaTests/'+fileName+'/meanCliTypeBand.png'
    fig.savefig(outPath, dpi=100, bbox_inches='tight')
    plt.close('all')

    fig, ax1 = plt.subplots(1, figsize=(16,12))
    for x in eval(estimDelaySlice[0]):
        for y in eval(estimDelaySlice[0])[x]:
            cliTypeMeanEstDelay = []
            for run in estimDelaySlice:
                cliTypeMeanEstDelay.append(eval(run)[x][y])
            # print(x, y, cliTypeMeanMos)
            ax1.plot(alphas, cliTypeMeanEstDelay, label=x + ' -> ' + y, marker='o', ls='-')
    # ax1.set_ylim(0,800)
    ax1.set_ylabel('Estimated Client Delay [ms]')
    ax1.set_xlabel('Alpha Parameter')
    plt.legend()
    plt.grid(True)
    outPath = 'plots/alphaTests/'+fileName+'/meanCliTypeEstDelay.pdf'
    fig.savefig(outPath, dpi=100, bbox_inches='tight')
    outPath = 'plots/alphaTests/'+fileName+'/meanCliTypeEstDelay.png'
    fig.savefig(outPath, dpi=100, bbox_inches='tight')
    plt.close('all')

def plotVariousCliNumTests(fileName):
    print(fileName)
    clientConfigs = []
    assignments = []
    objFunc = []
    minMos = []
    maxMos = []
    avgMos = []
    mosFairness = []
    meanBandSlice = []
    estimDelaySlice = []
    estMosSlice = []

    file_to_read = fileName+'.csv'
    with open(file_to_read, mode='r') as readFile:
        csv_reader = csv.reader(readFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                clientConfigs = row
            elif line_count == 1:
                assignments = row
            elif line_count == 2:
                objFunc = row
            elif line_count == 3:
                minMos = row
            elif line_count == 4:
                maxMos = row
            elif line_count == 5:
                avgMos = row
            elif line_count == 6:
                mosFairness = row
            elif line_count == 7:
                meanBandSlice = row
            elif line_count == 8:
                estimDelaySlice = row
            elif line_count == 9:
                estMosSlice = row
            line_count += 1
    
    print(eval(assignments[0]))
    print(eval(clientConfigs[0]))
    print(eval(meanBandSlice[0]))
    print(eval(estimDelaySlice[0]))
    print(eval(estMosSlice[0]))


    testNum = range(len(clientConfigs))

    if not os.path.exists('plots/variousCliNumTests/'+fileName+'/'):
        os.makedirs('plots/variousCliNumTests/'+fileName+'/')

    fig, ax1 = plt.subplots(1, figsize=(16,12))
    ax1.plot(testNum, mosFairness, label='QoE Fairness', marker='o', ls='-')
    ax1.plot(testNum, objFunc, label='Objective Function', marker='o', ls='-')
    ax1.set_ylim(-0.01,1.01)
    ax1.set_ylabel('Value')
    ax1.set_xlabel('Test Number')
    plt.legend()
    plt.grid(True)
    outPath = 'plots/variousCliNumTests/'+fileName+'/fairnessObjective.pdf'
    fig.savefig(outPath, dpi=100, bbox_inches='tight')
    outPath = 'plots/variousCliNumTests/'+fileName+'/fairnessObjective.png'
    fig.savefig(outPath, dpi=100, bbox_inches='tight')
    plt.close('all')

    fig, ax1 = plt.subplots(1, figsize=(16,12))
    for x in eval(assignments[0]):
        sliceXass = []
        for ass in assignments:
            sliceXass.append(eval(ass)[x])
        ax1.plot(testNum, sliceXass, label='Slice ' + x, marker='o', ls='-')
    ax1.set_ylim(0,80)
    ax1.set_ylabel('Assigned Resource Blocks')
    ax1.set_xlabel('Test Number')
    plt.legend()
    plt.grid(True)
    outPath = 'plots/variousCliNumTests/'+fileName+'/rbAssignment.pdf'
    fig.savefig(outPath, dpi=100, bbox_inches='tight')
    outPath = 'plots/variousCliNumTests/'+fileName+'/rbAssignment.png'
    fig.savefig(outPath, dpi=100, bbox_inches='tight')
    plt.close('all')

    fig, ax1 = plt.subplots(1, figsize=(16,12))
    ax1.plot(testNum, [eval(x)[2] for x in minMos], label='Minimal Utility', marker='o', ls='--')
    ax1.plot(testNum, [eval(x)[2] for x in maxMos], label='Maximal Utility', marker='o', ls='--')
    ax1.plot(testNum, avgMos, label='Mean Utility', marker='o', ls='-')
    ax1.set_ylim(0.95,5.05)
    ax1.set_ylabel('Utility')
    ax1.set_xlabel('Test Number')
    plt.legend()
    plt.grid(True)
    outPath = 'plots/variousCliNumTests/'+fileName+'/mos.pdf'
    fig.savefig(outPath, dpi=100, bbox_inches='tight')
    outPath = 'plots/variousCliNumTests/'+fileName+'/mos.png'
    fig.savefig(outPath, dpi=100, bbox_inches='tight')
    plt.close('all')

    fig, ax1 = plt.subplots(1, figsize=(16,12))
    for x in eval(estMosSlice[0]):
        for y in eval(estMosSlice[0])[x]:
            cliTypeMeanMos = []
            for run in estMosSlice:
                cliTypeMeanMos.append(eval(run)[x][y])
            # print(x, y, cliTypeMeanMos)
            ax1.plot(testNum, cliTypeMeanMos, label=x + ' -> ' + y, marker='o', ls='-')
    ax1.plot(testNum, avgMos, label='Mean Utility', marker='o', ls='-')
    ax1.set_ylim(0.95,5.05)
    ax1.set_ylabel('Utility')
    ax1.set_xlabel('Test Number')
    plt.legend()
    plt.grid(True)
    outPath = 'plots/variousCliNumTests/'+fileName+'/meanCliTypeMos.pdf'
    fig.savefig(outPath, dpi=100, bbox_inches='tight')
    outPath = 'plots/variousCliNumTests/'+fileName+'/meanCliTypeMos.png'
    fig.savefig(outPath, dpi=100, bbox_inches='tight')
    plt.close('all')
    
    fig, ax1 = plt.subplots(1, figsize=(16,12))
    for x in eval(meanBandSlice[0]):
        for y in eval(meanBandSlice[0])[x]:
            cliTypeMeanBand = []
            for run in meanBandSlice:
                cliTypeMeanBand.append(eval(run)[x][y])
            # print(x, y, cliTypeMeanMos)
            ax1.plot(testNum, cliTypeMeanBand, label=x + ' -> ' + y, marker='o', ls='-')
    # ax1.set_ylim(0,800)
    ax1.set_ylabel('Mean Bandwidth per Client [kbps]')
    ax1.set_xlabel('Test Number')
    plt.legend()
    plt.grid(True)
    outPath = 'plots/variousCliNumTests/'+fileName+'/meanCliTypeBand.pdf'
    fig.savefig(outPath, dpi=100, bbox_inches='tight')
    outPath = 'plots/variousCliNumTests/'+fileName+'/meanCliTypeBand.png'
    fig.savefig(outPath, dpi=100, bbox_inches='tight')
    plt.close('all')

    fig, ax1 = plt.subplots(1, figsize=(16,12))
    for x in eval(estimDelaySlice[0]):
        for y in eval(estimDelaySlice[0])[x]:
            cliTypeMeanEstDelay = []
            for run in estimDelaySlice:
                cliTypeMeanEstDelay.append(eval(run)[x][y])
            # print(x, y, cliTypeMeanMos)
            ax1.plot(testNum, cliTypeMeanEstDelay, label=x + ' -> ' + y, marker='o', ls='-')
    # ax1.set_ylim(0,800)
    ax1.set_ylabel('Estimated Client Delay [ms]')
    ax1.set_xlabel('Test Number')
    plt.legend()
    plt.grid(True)
    outPath = 'plots/variousCliNumTests/'+fileName+'/meanCliTypeEstDelay.pdf'
    fig.savefig(outPath, dpi=100, bbox_inches='tight')
    outPath = 'plots/variousCliNumTests/'+fileName+'/meanCliTypeEstDelay.png'
    fig.savefig(outPath, dpi=100, bbox_inches='tight')
    plt.close('all')

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


def prepareConfigINI(overallTestName, cliConfig, sliConfig, alpha, metric, minMax):
    numSlices = len(list(sliConfig))
    configString = '[Config ' + prepConfigName(overallTestName, cliConfig, sliConfig, alpha, metric, minMax)
    configString += ']\ndescription = \"Automatically generated config\"\n'
    configString += 'extends = baselineTestNS_' + str(numSlices) + 'sli_base\n\n'
    for sli in cliConfig:
        for cli in cliConfig[sli]:
            configString += '*.n' + cli[-3:] + ' = ' + str(cliConfig[sli][cli]) + '\n'
    configString += '\n'
    for sli in sliConfig:
        configString += '**.conn' + sli[-3:] + '.datarate = ' + str(int(sliConfig[sli])) + 'Mbps\n'
    print(overallTestName, alpha, metric, cliConfig, end=' ')
    return configString

def prepConfigName2sli(overallTestName, cliConfig, sliConfig, alpha, metric, minMax):
    numSlices = len(list(sliConfig))
    configName = overallTestName + '_' + str(numSlices) + 'sli_LVD-BWS_' + str(int(alpha*10)) + 'alpha_'
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

def prepareConfigINI2sli(overallTestName, cliConfig, sliConfig, alpha, metric, minMax):
    numSlices = len(list(sliConfig))
    configString = '[Config ' + prepConfigName(overallTestName, cliConfig, sliConfig, alpha, metric, minMax)
    configString += ']\ndescription = \"Automatically generated config\"\n'
    configString += 'extends = baselineTestNS_' + str(numSlices) + 'sli_LVD-BWS_base\n\n'
    for sli in cliConfig:
        for cli in cliConfig[sli]:
            configString += '*.n' + cli[-3:] + ' = ' + str(cliConfig[sli][cli]) + '\n'
    configString += '\n'
    for sli in sliConfig:
        configString += '**.conn' + sli[-3:] + '.datarate = ' + str(int(sliConfig[sli])) + 'Mbps\n'
    # print(overallTestName, alpha, metric, cliConfig, end=' ')
    return configString

def prepareConfigs(algoResName, algoType, alphas, testName):
    fileName = algoResName + algoType + 'alphas' + str(alphas)
    # print(fileName)
    chosenAlphaList = []
    clientConfigs = []
    assignments = []
    objFunc = []
    minMos = []
    maxMos = []
    avgMos = []
    mosFairness = []
    meanBandSlice = []
    estimDelaySlice = []
    estMosSlice = []

    file_to_read = fileName+'.csv'
    with open(file_to_read, mode='r') as readFile:
        csv_reader = csv.reader(readFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                chosenAlphaList = row
            elif line_count == 1:
                clientConfigs = row
            elif line_count == 2:
                assignments = row
            elif line_count == 3:
                objFunc = row
            elif line_count == 4:
                minMos = row
            elif line_count == 5:
                maxMos = row
            elif line_count == 6:
                avgMos = row
            elif line_count == 7:
                mosFairness = row
            elif line_count == 8:
                meanBandSlice = row
            elif line_count == 9:
                estimDelaySlice = row
            elif line_count == 10:
                estMosSlice = row
            line_count += 1
    resConfig = ''
    for i in range(len(chosenAlphaList)):
        resConfig += prepareConfigINI2sli('optimizationAlgo'+algoType, eval(clientConfigs[i]), eval(assignments[i]), chosenAlphaList[i], 'ndf', 'ndf')
        resConfig += '\n\n'
        # print('./runSimCampaign.sh -i optimizationAlgoTest.ini -c',  prepConfigName2sli('optimizationAlgo'+algoType, eval(clientConfigs[i]), eval(assignments[i]), chosenAlphaList[i], 'ndf', 'ndf'), '-t 1')
        # print('./export_results_individual_NS.sh -f 0 -l 0 -r 5 -s', prepConfigName2sli('optimizationAlgo'+algoType, eval(clientConfigs[i]), eval(assignments[i]), chosenAlphaList[i], 'ndf', 'ndf'), '-o ../../../analysis/' + prepConfigName2sli('optimizationAlgo'+algoType, eval(clientConfigs[i]), eval(assignments[i]), chosenAlphaList[i], 'ndf', 'ndf'), '-t', prepConfigName2sli('optimizationAlgo'+algoType, eval(clientConfigs[i]), eval(assignments[i]), chosenAlphaList[i], 'ndf', 'ndf'), '-d', prepConfigName2sli('optimizationAlgo'+algoType, eval(clientConfigs[i]), eval(assignments[i]), chosenAlphaList[i], 'ndf', 'ndf'))
        hostList = ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP']
        tempCurrConfig = eval(clientConfigs[i])
        currConfig = {}
        for sli in tempCurrConfig:
            for cli in tempCurrConfig[sli]:
                currConfig[cli] = tempCurrConfig[sli][cli]
        
        print('extractAll(\'' + prepConfigName2sli('optimizationAlgo'+algoType, eval(clientConfigs[i]), eval(assignments[i]), chosenAlphaList[i], 'ndf', 'ndf') + '\',', str(hostList) + ',', str([currConfig[x] for x in hostList]) + ', 2)')
        
        # print(clientConfigs[i], assignments[i])

    
    # print(resConfig)
    # if not os.path.exists('simConfigStubs/'):
    #     os.makedirs('simConfigStubs/')
    # with open('simConfigStubs/'+algoResName + algoType + 'alphas' + str(alphas)+'ndf'+'ndf'+'.txt', mode='w') as writeFile:
    #     writeFile.write(resConfig)

prepareConfigs('2sliLVD_BWSTestVariousCliNums[5-20-50-75-100]', 'Fairness1', [0.0, 0.5, 1.0], 'optimizationAlgo')

def extractHighestMetricResult(algoResName, algoType, alphas, metric, minMax):
    resConfig = ''
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
    for alpha in alphas:
        fileName = algoResName + algoType + 'alpha' + str(alpha)
        # print(fileName)
        clientConfigs = []
        assignments = []
        objFunc = []
        minMos = []
        maxMos = []
        avgMos = []
        mosFairness = []
        meanBandSlice = []
        estimDelaySlice = []
        estMosSlice = []

        file_to_read = fileName+'.csv'
        with open(file_to_read, mode='r') as readFile:
            csv_reader = csv.reader(readFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
            line_count = 0
            for row in csv_reader:
                if line_count == 0:
                    clientConfigs = row
                elif line_count == 1:
                    assignments = row
                elif line_count == 2:
                    objFunc = row
                elif line_count == 3:
                    minMos = row
                elif line_count == 4:
                    maxMos = row
                elif line_count == 5:
                    avgMos = row
                elif line_count == 6:
                    mosFairness = row
                elif line_count == 7:
                    meanBandSlice = row
                elif line_count == 8:
                    estimDelaySlice = row
                elif line_count == 9:
                    estMosSlice = row
                line_count += 1
        
        consideredValueList = []

        if metric == 'fairness':
            consideredValueList = mosFairness
        elif metric == 'mean':
            consideredValueList = avgMos
        elif metric == 'min':
            consideredValueList = [eval(x)[2] for x in minMos]
        else:
            print('Value not found. Quitting...')
            return
        
        
        chosenIndex = -1

        if minMax == 'min':
            chosenIndex = consideredValueList.index(min(consideredValueList))
            resConfig += prepareConfigINI('optimizationAlgo'+algoType, eval(clientConfigs[chosenIndex]), eval(assignments[chosenIndex]), alpha, metric, minMax)
            
            print(min(consideredValueList))
        elif minMax == 'max':
            chosenIndex = consideredValueList.index(max(consideredValueList))
            resConfig += prepareConfigINI('optimizationAlgo'+algoType, eval(clientConfigs[chosenIndex]), eval(assignments[chosenIndex]), alpha, metric, minMax)
            print(max(consideredValueList))
        else:
            print('Unknown whether to take min or max ' + metric + ' metric value. Quitting...')
            return
        print(chosenIndex)
        chosenAlphaList.append(alpha)
        chosenMetric.append(metric)
        chosenMinMax.append(minMax)
        chosenCliConfigs.append(clientConfigs[chosenIndex])
        chosenAssignments.append(assignments[chosenIndex])
        chosenObjFunc.append(objFunc[chosenIndex])
        chosenMinMos.append(minMos[chosenIndex])
        chosenMaxMos.append(maxMos[chosenIndex])
        chosenAvgMos.append(avgMos[chosenIndex])
        chosenMosFairness.append(mosFairness[chosenIndex])
        chosenMeanBandSlice.append(meanBandSlice[chosenIndex])
        chosenEstimDelaySlice.append(estimDelaySlice[chosenIndex])
        chosenEstMosSlice.append(estMosSlice[chosenIndex])
        resConfig += '\n\n'
            
    # print(resConfig)
    if not os.path.exists('simConfigStubs/'):
        os.makedirs('simConfigStubs/')
    with open('simConfigStubs/'+algoResName + algoType + 'alphas' + str(alphas)+metric+minMax+'.txt', mode='w') as writeFile:
        writeFile.write(resConfig)
        # print('')
    if not os.path.exists('selectedConfigsRes/'):
        os.makedirs('selectedConfigsRes/')
    with open('selectedConfigsRes/'+algoResName + algoType + 'alphas' + str(alphas)+metric+minMax+'.csv', mode='w') as writeFile:
            fw = csv.writer(writeFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
            fw.writerow(chosenAlphaList)
            fw.writerow(chosenMetric)
            fw.writerow(chosenMinMax)
            fw.writerow(chosenCliConfigs)
            fw.writerow(chosenAssignments)
            fw.writerow(chosenObjFunc)
            fw.writerow(chosenMinMos)
            fw.writerow(chosenMaxMos)
            fw.writerow(chosenAvgMos)
            fw.writerow(chosenMosFairness)
            fw.writerow(chosenMeanBandSlice)
            fw.writerow(chosenEstimDelaySlice)
            fw.writerow(chosenEstMosSlice)


# plotAlphaBeta('5sliAlphaBetaTest')
# plotAlphaBeta('2sliLVD_DESAlphaBetaTest')
# plotAlphaBeta('2sliLVD_BWSAlphaBetaTest')
# plotAlphaBeta('5sliAlphaBetaTest2')
# plotAlphaBeta('2sliLVD_DESAlphaBetaTest2')
# plotAlphaBeta('2sliLVD_BWSAlphaBetaTest2')
# plotAlphaBeta('5sliAlphaBetaTest3')
# plotAlphaBeta('2sliLVD_DESAlphaBetaTest3')
# plotAlphaBeta('2sliLVD_BWSAlphaBetaTest3')
# plotAlphaBeta('5sliAlphaBetaTest4')

# plotAlpha('5sliAlphaBetaTest5')
# plotAlpha('5sliAlphaBetaTest6')
# plotAlpha('5sliAlphaBetaTest7')

# plotAlpha('2sliLVD_DESAlphaTest1')
# plotAlpha('2sliLVD_BWSAlphaTest1')

# plotAlpha('2sliLVD_DESAlphaTest2')
# plotAlpha('2sliLVD_BWSAlphaTest2')

# plotAlpha('5sliAlphaTest50eachMinMos1')
# plotAlpha('5sliAlphaTestFewFileMinMos1')
# plotAlpha('5sliAlphaTestFewLiveMinMos1')
# plotAlpha('5sliAlphaTestFewVoDMinMos1')
# plotAlpha('5sliAlphaTestFewVoIPMinMos1')
# plotAlpha('5sliAlphaTestFewSSHMinMos1')

# plotAlpha('5sliAlphaTest50eachFairness1')
# plotAlpha('5sliAlphaTestFewFileFairness1')
# plotAlpha('5sliAlphaTestFewLiveFairness1')
# plotAlpha('5sliAlphaTestFewVoDFairness1')
# plotAlpha('5sliAlphaTestFewVoIPFairness1')
# plotAlpha('5sliAlphaTestFewSSHFairness1')

# plotVariousCliNumTests('5sliTestVariousCliNums[5-20-50-75-100]Fairness1alpha0.0')
# plotVariousCliNumTests('5sliTestVariousCliNums[5-20-50-75-100]Fairness1alpha0.2')
# plotVariousCliNumTests('5sliTestVariousCliNums[5-20-50-75-100]Fairness1alpha0.4')
# plotVariousCliNumTests('5sliTestVariousCliNums[5-20-50-75-100]Fairness1alpha0.5')
# plotVariousCliNumTests('5sliTestVariousCliNums[5-20-50-75-100]Fairness1alpha0.6')
# plotVariousCliNumTests('5sliTestVariousCliNums[5-20-50-75-100]Fairness1alpha0.8')
# plotVariousCliNumTests('5sliTestVariousCliNums[5-20-50-75-100]Fairness1alpha1.0')

# plotVariousCliNumTests('5sliTestVariousCliNums[5-20-50-75-100]MinMos1alpha0.0')
# plotVariousCliNumTests('5sliTestVariousCliNums[5-20-50-75-100]MinMos1alpha0.2')
# plotVariousCliNumTests('5sliTestVariousCliNums[5-20-50-75-100]MinMos1alpha0.4')
# plotVariousCliNumTests('5sliTestVariousCliNums[5-20-50-75-100]MinMos1alpha0.5')
# plotVariousCliNumTests('5sliTestVariousCliNums[5-20-50-75-100]MinMos1alpha0.6')
# plotVariousCliNumTests('5sliTestVariousCliNums[5-20-50-75-100]MinMos1alpha0.8')
# plotVariousCliNumTests('5sliTestVariousCliNums[5-20-50-75-100]MinMos1alpha1.0')

# extractHighestMetricResult('5sliTestVariousCliNums[5-20-50-75-100]', 'Fairness1', [0.0, 0.5, 1.0], 'fairness', 'max')
# extractHighestMetricResult('5sliTestVariousCliNums[5-20-50-75-100]', 'Fairness1', [0.0, 0.5, 1.0], 'min', 'max')
# extractHighestMetricResult('5sliTestVariousCliNums[5-20-50-75-100]', 'Fairness1', [0.0, 0.5, 1.0], 'mean', 'max')
# extractHighestMetricResult('5sliTestVariousCliNums[5-20-50-75-100]', 'Fairness1', [0.0, 0.5, 1.0], 'fairness', 'min')
# extractHighestMetricResult('5sliTestVariousCliNums[5-20-50-75-100]', 'Fairness1', [0.0, 0.5, 1.0], 'min', 'min')
# extractHighestMetricResult('5sliTestVariousCliNums[5-20-50-75-100]', 'Fairness1', [0.0, 0.5, 1.0], 'mean', 'min')