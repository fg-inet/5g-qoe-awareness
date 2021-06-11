import xml.etree.ElementTree as ET
import numpy as np

import delayEstimation as delEst
import qoeEstimation as qoeEst

import shutil
import random
import matplotlib.pyplot as plt
import matplotlib

font = {'weight' : 'normal',
        'size'   : 30}

matplotlib.rc('font', **font)
matplotlib.rc('lines', linewidth=2.0)
matplotlib.rc('lines', markersize=8)

def getBandForQoECli(host, desQoE):
    qoeEstimator = qoeEst.ClientQoeEstimator(host)
    qoe = np.array([qoeEstimator.estQoEb(x) for x in qoeEstimator.yAxis])
    if host == 'hostLVD':
        desQoE += 0.1
    idx = np.abs(qoe - desQoE).argmin()
    while qoe[idx] < desQoE:
        idx += 1
    return qoeEstimator.yAxis[idx]

def determineResourceToSlice(availBand, trafficMix, reqBitratesPerType):
    aB = availBand
    tempRes = {}
    tempSumRes = 0
    for cT in trafficMix:
        tempRes[cT] = trafficMix[cT] * reqBitratesPerType[cT]
        tempSumRes += tempRes[cT]
    multiplier = aB / tempSumRes
    resAlloc = {}
    for cT in tempRes:
        resAlloc[cT] = multiplier * tempRes[cT]
    return resAlloc

# default: ceilMultiplier = 1.25; guaranteeMultiplier = 1.0
def simpleAdmission(expName, availBand, desiredQoE, trafficMix, maxNumClis, ceilMultiplier, guaranteeMultiplier, sliceConfig, seed):
    random.seed(seed, version=2)
    resultString = ''
    reqBitratesPerType = {}
    ceilBitrates = {}
    assuredBitrates = {}
    numHostsAdmittedPerType = {}
    numHostsRejectedPerType = {}
    numHostsArrivedPerType = {}
    probabilityRanges = {}
    lastProb = 0
    resultString += '--------------------------------------------------------------------------------\n'
    resultString += '--------------------------------------------------------------------------------\n'
    resultString += '-> Experiment ' + expName + ' with requirements:\n'
    resultString += '\tGBR multiplier: ' + str(guaranteeMultiplier) + '\n'
    resultString += '\tMBR multiplier: ' + str(ceilMultiplier) + '\n'
    resultString += '\tNumber of arriving clients: ' + str(maxNumClis) + '\n'
    resultString += '\tTraffic Mix: ' + str(trafficMix) + '\n'
    resultString += '\tAvailable Bandwidth: ' + str(availBand) + 'kbps\n'
    resultString += '\tDesired Target QoE: ' + str(desiredQoE)
    resultString += '\tSlicing Configuration: ' + str(sliceConfig)+ '\n\n'

    resultString += 'Client type requirements:\n'
    for host in trafficMix:
        reqBitratesPerType[host] = int(getBandForQoECli('host'+host, desiredQoE))
        ceilBitrates['host'+host] = int(reqBitratesPerType[host] * ceilMultiplier)
        assuredBitrates['host'+host] = int(reqBitratesPerType[host] * guaranteeMultiplier)
        resultString += '\tFor a QoE of ' + str(desiredQoE) + ' ' + str(host) + ' needs ' + str(reqBitratesPerType[host]) + ' kbps. It translates to a GBR of ' + str(assuredBitrates['host'+host]) + ' kbps and a MBR of ' + str(ceilBitrates['host'+host]) + 'kbps.\n'
        numHostsAdmittedPerType['host'+host] = 0
        numHostsRejectedPerType['host'+host] = 0
        numHostsArrivedPerType['host'+host] = 0
        probabilityRanges[host] = [lastProb*100, (lastProb+trafficMix[host])*100]
        lastProb += trafficMix[host]
    resAlloc = determineResourceToSlice(availBand, trafficMix, reqBitratesPerType)
    sumAdmitted = 0
    sumResourcesUsed = 0

    resultString += '\nSlice settings:\n'
    sliAlloc = {}
    sumResSli = {}
    sliIdent = 0
    appToSli = {}
    for sli in sliceConfig:
        resultString += '\tSlice ' + str(sliIdent) + ' contains the following client types: |'
        sliAlloc[sliIdent] = 0
        for appType in sli:
            sliAlloc[sliIdent] += int(resAlloc[appType])
            appToSli[appType] = sliIdent
            resultString += str(appType) + '|'
        resultString += ' and has ' + str(sliAlloc[sliIdent]) + 'kbps available\n'

        sumResSli[sliIdent] = 0
        sliIdent += 1

    # print(sliAlloc)
    # print(appToSli)
    for i in range(0,maxNumClis):
        ran = random.randint(1,100)
        selHost = ''
        for host in probabilityRanges:
            if ran >= probabilityRanges[host][0] and ran <= probabilityRanges[host][1]:
                selHost = host
        numHostsArrivedPerType['host'+selHost] += 1
        selSli = appToSli[selHost]
        # print(i, selHost, selSli, end=': ')
        tryAdd = sumResSli[selSli] + assuredBitrates['host'+selHost]
        if tryAdd < sliAlloc[selSli]:
            # print('Host Admitted.')
            sumResSli[selSli] = tryAdd
            numHostsAdmittedPerType['host'+selHost] += 1
            sumAdmitted += 1
            sumResourcesUsed += assuredBitrates['host'+selHost]
        else:
            numHostsRejectedPerType['host'+selHost] += 1
            # print('Host rejected!!!')
    
    resultString += '\nAdmission complete:\n'
    resultString += '\tHosts admitted for desired QoE of ' + str(desiredQoE) + ' and link bitrate of ' + str(availBand) + 'kbps is : ' + str(sumAdmitted) + '\n'
    resultString += '\tThis allocation will use ' + str(sumResourcesUsed) + 'kbps out of available ' + str(availBand) + 'kbps\n'
    resultString += '\nFor each host type:\n'
    for host in trafficMix:
        resultString += '\t' + str(host) + ': ' + str(numHostsArrivedPerType['host'+host]) + ' arrived, ' + str(numHostsAdmittedPerType['host'+host]) + ' were admitted (total used '+str(numHostsAdmittedPerType['host'+host]*assuredBitrates['host'+host])+'kbps), and ' + str(numHostsRejectedPerType['host'+host]) + ' were rejected. That corresponds to rejection rate of: ' + str(numHostsRejectedPerType['host'+host]*100/numHostsArrivedPerType['host'+host])+'%\n'

    # print('\n' + resultString)

    # f = open('./admissionData/'+expName+'.txt', 'w')
    # f.write(resultString)
    # f.close()

    return expName, numHostsArrivedPerType, numHostsAdmittedPerType, numHostsRejectedPerType, assuredBitrates, ceilBitrates

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

def plotNumberAdmittedRejected(configData, cN):
    fig, ax = plt.subplots(1, figsize=(16,12))
    xPosition = 0

    ticks = []
    labels = []
    for conf in configData:
        prevHeightArr = 0
        prevHeightAcc = 0
        prevHeightRej = 0
        for host in configData[conf][1]:
            arrClis = configData[conf][1][host]
            admClis = configData[conf][2][host]
            rejClis = configData[conf][3][host]
            # rejRate = round(rejClis*100/arrClis,2)
            cl = colorMapping[host.split('host')[-1]]
            # print(host, arrClis, admClis, rejClis)
            prevHeightArr += arrClis
            prevHeightAcc += admClis
            prevHeightRej += rejClis
            ax.bar(xPosition, prevHeightArr, color=cl, edgecolor='black', hatch='|', zorder=1000-prevHeightArr)
            ax.text(xPosition, (prevHeightArr*2-arrClis)/2, str(arrClis), ha='center', va='center', rotation=0, fontsize=20,bbox=dict(boxstyle="round", edgecolor='White', facecolor='white', alpha=0.5, pad=0.1), zorder=1100)
            ax.bar(xPosition+1, prevHeightAcc, color=cl, edgecolor='black', hatch='/', zorder=1000-prevHeightAcc)
            ax.text(xPosition+1, (prevHeightAcc*2-admClis)/2, str(admClis), ha='center', va='center', rotation=0, fontsize=20,bbox=dict(boxstyle="round", edgecolor='White', facecolor='white', alpha=0.5, pad=0.1), zorder=1100)
            ax.bar(xPosition+2, prevHeightRej, color=cl, edgecolor='black', hatch='x', zorder=100-prevHeightRej)
            ax.text(xPosition+2, (prevHeightRej*2-rejClis)/2, str(rejClis), ha='center', va='center', rotation=0, fontsize=20,bbox=dict(boxstyle="round", edgecolor='White', facecolor='white', alpha=0.5, pad=0.1), zorder=1100)
        ticks.append(xPosition+1)
        lbl = configData[conf][0]
        # print(lbl)
        if 'Base' in lbl:
            lbl = 'No Slicing'
        if 'sli' in lbl:
            lbl = lbl.split('_')[1][0]
            # print(lbl)
            lbl += ' Slices'
        # print(lbl)
        labels.append(lbl)

        xPosition += 3
    for appType in configData[conf][1]:
        ax.bar(-10,5,color=colorMapping[appType.split('host')[-1]], edgecolor='black', label=chooseName(appType))

    ax.bar(-10,5,color='white', edgecolor='black', hatch='|', label='Arrived')
    ax.bar(-10,5,color='white', edgecolor='black', hatch='/', label='Accepted')
    ax.bar(-10,5,color='white', edgecolor='black', hatch='x', label='Rejected')

    ax.set_ylim(0,120)
    ax.set_xlim(-1,xPosition)

    plt.grid(axis='y')
    plt.xticks(ticks, labels, rotation=0)
    plt.legend(fontsize=25, bbox_to_anchor=(1, 1), loc='upper left')
    plt.xlabel('Slicing configuration')
    plt.ylabel('Number of clients')
    fig.savefig('./admissionData/plots/'+cN+'.png', dpi=100, bbox_inches='tight', format='png')

def plotNumberRejectionRate(configData, cN):
    fig, ax = plt.subplots(1, figsize=(16,12))
    xPosition = 0

    ticks = []
    labels = []
    hostRejRate = {}
    hostRejRate['all'] = []
    sli = []
    enum = 0
    for conf in configData:
        sli.append(xPosition)
        totRej = 0
        totArr = 0
        for host in configData[conf][1]:
            arrClis = configData[conf][1][host]
            rejClis = configData[conf][3][host]
            totRej += rejClis
            totArr += arrClis
            rejRate = round(rejClis*100/arrClis,2)
            if host not in hostRejRate:
                hostRejRate[host] = []
            hostRejRate[host].append(rejRate)
        hostRejRate['all'].append(round(totRej*100/totArr,2))
        ticks.append(xPosition)
        lbl = configData[conf][0]
        # print(lbl)
        if 'Base' in lbl:
            lbl = 'No Slicing'
        if 'sli' in lbl:
            lbl = lbl.split('_')[1][0]
            # print(lbl)
            lbl += ' Slices'
        # print(lbl)
        labels.append(lbl)
        xPosition += 1
    for appType in configData[conf][1]:
        ax.plot(sli, hostRejRate[appType], '-o',color=colorMapping[appType.split('host')[-1]], label=chooseName(appType))
    ax.plot(sli, hostRejRate['all'], '-o',color='black', label='Overall')

    ax.set_ylim(0,25)
    ax.set_xlim(-0.1,xPosition-0.9)

    plt.grid(axis='y')
    plt.xticks(ticks, labels, rotation=0)
    plt.legend(fontsize=25, bbox_to_anchor=(1, 1), loc='upper left')
    plt.xlabel('Slicing configuration')
    plt.ylabel('Rejection Rate [%]')
    fig.savefig('./admissionData/plots/'+cN+'RejectionRate.png', dpi=100, bbox_inches='tight', format='png')

    # plt.show()

# targetQoE = [3.5]
# assuredMulti = [1.0,0.85]
# rates = [100]
# maxNumCli = [400]
# ceils = [2.0]
# trafficMix = {'VID' : 0.4, 
#               'LVD' : 0.2, 
#               'FDO' : 0.05, 
#               'VIP' : 0.3, 
#               'SSH' : 0.05}
# seed = 'aNewHope'
# expNamePrefix = 'aNewHopeV1'

targetQoE = [3.5]
assuredMulti = [1.0]
rates = [100]
maxNumCli = [120]
ceils = [1.0]
trafficMix = {'VID' : 0.4, 
              'LVD' : 0.2, 
              'FDO' : 0.05, 
              'VIP' : 0.3, 
              'SSH' : 0.05}
seed = 'thisIsInteresting'
expNamePrefix = 'QoS-Flows'

for rate, maxCli in zip(rates, maxNumCli):
    for qoE in targetQoE:
        for mult in assuredMulti:
            for ceil in ceils:
                data1sli = simpleAdmission(expNamePrefix+'Base_R'+str(int(rate))+'_Q'+str(int(qoE*10))+'_M'+str(int(mult*100))+'_C'+str(int(ceil*100)), rate*1000, qoE, trafficMix, maxCli, ceil, mult, [['VID', 'LVD', 'FDO', 'VIP', 'SSH']], seed)
                # data2sli = simpleAdmission(expNamePrefix+'GBR'+str(int(mult*100))+'No2_2sli_R'+str(int(rate))+'_Q'+str(int(qoE*10))+'_M'+str(int(mult*100))+'_C'+str(int(ceil*100)), rate*1000, qoE, trafficMix, maxCli, ceil, mult, [['VID', 'LVD', 'FDO'], ['VIP', 'SSH']], seed)
                data5sli = simpleAdmission(expNamePrefix+'_5sli_R'+str(int(rate))+'_Q'+str(int(qoE*10))+'_M'+str(int(mult*100))+'_C'+str(int(ceil*100)), rate*1000, qoE, trafficMix, maxCli, ceil, mult, [['VID'], ['LVD'], ['FDO'], ['VIP'], ['SSH']], seed)
                confDict = {
                    '1sli' : data1sli,
                    # '2sli' : data2sli,
                    '5sli' : data5sli
                }
                plotNumberAdmittedRejected(confDict, expNamePrefix+'_R'+str(int(rate))+'_Q'+str(int(qoE*10))+'_M'+str(int(mult*100))+'_C'+str(int(ceil*100)))
                plotNumberRejectionRate(confDict, expNamePrefix+'_R'+str(int(rate))+'_Q'+str(int(qoE*10))+'_M'+str(int(mult*100))+'_C'+str(int(ceil*100)))
                # exit()
                # genAllSliConfigsHTBRun(expNamePrefix+'GBR'+str(int(mult*100))+'No12Base_R'+str(int(rate))+'_Q'+str(int(qoE*10))+'_M'+str(int(mult*100))+'_C'+str(int(ceil*100)), 'liteCbaselineTestTokenQoS_base', expNamePrefix, trafficMix, rate, qoE, ['VID', 'LVD', 'FDO', 'VIP', 'SSH'], [['VID', 'LVD', 'FDO', 'VIP', 'SSH']], ['connFIX0'], maxCli, ceil, mult, 'False', seed)
                # genAllSliConfigsHTBRun(expNamePrefix+'GBR'+str(int(mult*100))+'No2_2sli_R'+str(int(rate))+'_Q'+str(int(qoE*10))+'_M'+str(int(mult*100))+'_C'+str(int(ceil*100)), 'liteCbaselineTestTokenQoS_base', expNamePrefix, trafficMix, rate, qoE, ['VID', 'LVD', 'FDO', 'VIP', 'SSH'], [['VID', 'LVD', 'FDO'], ['VIP', 'SSH']], ['connBWS', 'connDES'], maxCli, ceil, mult, 'False', seed)
                # genAllSliConfigsHTBRun(expNamePrefix+'GBR'+str(int(mult*100))+'No3_5sli_R'+str(int(rate))+'_Q'+str(int(qoE*10))+'_M'+str(int(mult*100))+'_C'+str(int(ceil*100)), 'liteCbaselineTestTokenQoS_base', expNamePrefix, trafficMix, rate, qoE, ['VID', 'LVD', 'FDO', 'VIP', 'SSH'], [['VID'], ['LVD'], ['FDO'], ['VIP'], ['SSH']], ['connVID', 'connLVD', 'connFDO', 'connVIP', 'connSSH'], maxCli, ceil, mult, 'False', seed)