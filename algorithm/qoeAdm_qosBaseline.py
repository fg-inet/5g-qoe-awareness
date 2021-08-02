import xml.etree.ElementTree as ET
import numpy as np

import delayEstimation as delEst
import qoeEstimation as qoeEst

import shutil
import random
import matplotlib.pyplot as plt
import time

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

    print('\n' + resultString)

    f = open('./admissionData/'+expName+'.txt', 'w')
    f.write(resultString)
    f.close()

    return numHostsAdmittedPerType, assuredBitrates, ceilBitrates, sliAlloc

def prepareHTBClassXML(configElem, classType, className, clParent, clRate, clCeil, clBurst, clCburst, clLevel, clQuantum, clMbuffer, clPrio, clQueueNum):
    classElem = ET.SubElement(configElem, 'class')
    classElem.set('id', classType+className)

    parentId = ET.SubElement(classElem, 'parentId')
    parentId.text = clParent

    rate = ET.SubElement(classElem, 'rate')
    rate.set('type', 'int')
    rate.text = clRate

    ceil = ET.SubElement(classElem, 'ceil')
    ceil.set('type', 'int')
    ceil.text = clCeil

    burst = ET.SubElement(classElem, 'burst')
    burst.set('type', 'int')
    burst.text = clBurst

    cburst = ET.SubElement(classElem, 'cburst')
    cburst.set('type', 'int')
    cburst.text = clCburst

    level = ET.SubElement(classElem, 'level')
    level.set('type', 'int')
    level.text = clLevel

    quantum = ET.SubElement(classElem, 'quantum')
    quantum.set('type', 'int')
    quantum.text = clQuantum

    mbuffer = ET.SubElement(classElem, 'mbuffer')
    mbuffer.set('type', 'int')
    mbuffer.text = clMbuffer

    if classType == 'leaf':
        prio = ET.SubElement(classElem, 'priority')
        prio.text = clPrio

        queueNum = ET.SubElement(classElem, 'queueNum')
        queueNum.set('type', 'int')
        queueNum.text = clQueueNum

# {leafName:[assuredRate, ceilRate, priority, queueNum, parentId, level]}
# {innerName:[assuredRate, ceilRate, parentId, level]}
def genHTBconfigWithInner(configName, linkSpeed, leafClassesConfigs, innerClassesConfigs, numLevels):

    configElem = ET.Element('config')
    prepareHTBClassXML(configElem, 'root', '', 'NULL', str(linkSpeed), str(linkSpeed), '2000', '2000', str(numLevels), '1500', '60', '', '')
    
    for inner in innerClassesConfigs:
        prepareHTBClassXML(configElem, 'inner', inner, str(innerClassesConfigs[inner][2]), str(innerClassesConfigs[inner][0]), str(innerClassesConfigs[inner][1]), '2000', '2000', str(innerClassesConfigs[inner][3]), '1500', '60', '', '')
    
    for leaf in leafClassesConfigs:
        prepareHTBClassXML(configElem, 'leaf', leaf, str(leafClassesConfigs[leaf][4]), str(leafClassesConfigs[leaf][0]), str(leafClassesConfigs[leaf][1]), '2000', '2000', str(leafClassesConfigs[leaf][5]), '1500', '60', str(leafClassesConfigs[leaf][2]), str(leafClassesConfigs[leaf][3]))

    # create a new XML file with the results
    mydata = ET.tostring(configElem)
    myfile = open('../5gNS/simulations/configs/htbTree/'+configName+"HTB.xml", "wb")
    myfile.write(mydata)


def makeIPhostNum(ipPrefix, hostNum):
    ipString = ipPrefix + '.'
    ipString += str(hostNum // 64) + '.'
    ipString += str(4*hostNum % 256)
    return ipString

def genBaselineRoutingConfig(configName, hostTypes, hostNums, hostIPprefixes, serverTypes, serverIPprefixes):
    configElem = ET.Element('config')
    for host,nums in zip(hostTypes, hostNums):
        for num in range(nums):
            interfaceElem = ET.SubElement(configElem, 'interface')
            interfaceElem.set('hosts', host+'['+str(num)+']')
            interfaceElem.set('names', 'ppp0')
            interfaceElem.set('address', makeIPhostNum(hostIPprefixes[host],num))
            interfaceElem.set('netmask', '255.255.255.252')
        interfaceElem = ET.SubElement(configElem, 'interface')
        interfaceElem.set('hosts', 'router0')
        interfaceElem.set('towards', host+'[*]')
        interfaceElem.set('address', hostIPprefixes[host]+'.x.x')
        interfaceElem.set('netmask', '255.255.255.252')
    
    for server in serverTypes:
        interfaceElem = ET.SubElement(configElem, 'interface')
        interfaceElem.set('hosts', server)
        interfaceElem.set('names', 'ppp0')
        interfaceElem.set('address', serverIPprefixes[server]+'.0.0')
        interfaceElem.set('netmask', '255.255.255.252')
    

    interfaceElem = ET.SubElement(configElem, 'interface')
    interfaceElem.set('hosts', '**')
    interfaceElem.set('address', '10.x.x.x')
    interfaceElem.set('netmask', '255.x.x.x')
    


    # create a new XML file with the results
    mydata = ET.tostring(configElem)
    myfile = open('../5gNS/simulations/configs/baseQoS/'+configName+"Routing.xml", "wb")
    myfile.write(mydata)


def genBaselineIniConfig(confName, base, numHostsPerType, hostIPprefixes, availBand, ceilMultiplier, guaranteeMultiplier):
    sumHosts = 0

    packFilters = '\"'
    packDataFiltersR0 = '\"'
    packDataFiltersR1 = '\"'

    for host in numHostsPerType:
        numHostsType = numHostsPerType[host]
        sumHosts += numHostsType
        for num in range(numHostsType):
            packFilters += '*;'
            packDataFiltersR0 += 'sourceAddress(' + makeIPhostNum(hostIPprefixes[host],num) + ');'
            packDataFiltersR1 += 'destinationAddress(' + makeIPhostNum(hostIPprefixes[host],num) + ');'


    packFilters = packFilters[:-1]
    packDataFiltersR0 = packDataFiltersR0[:-1]
    packDataFiltersR1 = packDataFiltersR1[:-1]

    packFilters += '\"'
    packDataFiltersR0 += '\"'
    packDataFiltersR1 += '\"'
    

    configString = '[Config ' + confName + ']\n'
    configString += 'description = \"Configuration for ' + confName + '. All five applications. QoS employed. Guarantee Multiplier: ' + str(guaranteeMultiplier) + '; Ceil multiplier: ' + str(ceilMultiplier) +'\"\n\n'
    configString += 'extends = ' + base + '\n\n'
    configString += '*.configurator.config = xmldoc(\"configs/baseQoS/' + confName + 'Routing.xml\")\n\n'
    if 'hostVID' in numHostsPerType:
        configString += '*.nVID = ' + str(numHostsPerType['hostVID']) + ' # Number of video clients\n'
    else: 
        configString += '*.nVID = 0 # Number of video clients\n'
    if 'hostLVD' in numHostsPerType:
        configString += '*.nLVD = ' + str(numHostsPerType['hostLVD']) + ' # Number of live video client\n'
    else: 
        configString += '*.nLVD = 0 # Number of live video client\n'
    if 'hostFDO' in numHostsPerType:
        configString += '*.nFDO = ' + str(numHostsPerType['hostFDO']) + ' # Number of file download clients\n'
    else: 
        configString += '*.nFDO = 0 # Number of file download clients\n'
    if 'hostSSH' in numHostsPerType:
        configString += '*.nSSH = ' + str(numHostsPerType['hostSSH']) + ' # Number of SSH clients\n'
    else: 
        configString += '*.nSSH = 0 # Number of SSH clients\n'
    if 'hostVIP' in numHostsPerType:
        configString += '*.nVIP = ' + str(numHostsPerType['hostVIP']) + ' # Number of VoIP clients\n\n'
    else: 
        configString += '*.nVIP = 0 # Number of VoIP clients\n\n'
    configString += '*.router*.ppp[0].ppp.queue.typename = \"HTBQueue\"\n'
    configString += '*.router*.ppp[0].ppp.queue.numQueues = ' + str(sumHosts) + '\n'
    configString += '*.router*.ppp[0].ppp.queue.queue[*].typename = \"DropTailQueue\"\n'
    configString += '*.router*.ppp[0].ppp.queue.packetCapacity = -1\n'
    configString += '*.router*.ppp[0].ppp.queue.htbHysterisis = false\n'
    configString += '*.router*.ppp[0].ppp.queue.htbTreeConfig = xmldoc(\"configs/htbTree/' + confName + 'HTB.xml\")\n'
    configString += '*.router*.ppp[0].ppp.queue.classifier.defaultGateIndex = 0\n'
    configString += '*.router*.ppp[0].ppp.queue.classifier.packetFilters = ' + packFilters + '\n'
    configString += '*.router0.ppp[0].ppp.queue.classifier.packetDataFilters = ' + packDataFiltersR0 + '\n'
    configString += '*.router1.ppp[0].ppp.queue.classifier.packetDataFilters = ' + packDataFiltersR1 + '\n\n'

    configString += '**.connFIX0.datarate = ' + str(availBand) + 'bps\n'
    configString += '**.connFIX0.delay = 40ms\n\n\n'

    f = open(confName+".txt", "w")
    f.write(configString)
    f.close()

    f2 = open('../5gNS/simulations/qosFlowsConfig.ini', 'a')
    f2.write(configString)
    f2.close()


def genAllSliConfigsHTBRun(configName, baseName, namePrefix, trafficMix, availBand, desiredQoE, types, hostToSlice, sliceNames, maxNumCliType, ceilMultiplier, guaranteeMultiplier, differentiatePrios, seed):
    cliTypes = ['host'+x for x in types]
    serverTypes = ['server'+x for x in types]
    numHostsPerType, reqBitratesPerType, ceilBitrates, sliAlloc = simpleAdmission(configName, availBand*1000, desiredQoE, trafficMix, maxNumCliType, ceilMultiplier, guaranteeMultiplier, hostToSlice, seed)
    hostIPprefixes = {}
    serverIPprefixes = {}
    leafClassesConfigs = {}
    innerClassConfigs = {}
    queueInt = 0
    # {leafName:[assuredRate, ceilRate, priority, queueNum, parentId, level]}
    # {innerName:[assuredRate, ceilRate, parentId, level]}
    numLev = 2
    for sliNum in range(len(hostToSlice)):
        parentName = 'inner'+sliceNames[sliNum]
        if sliceNames[sliNum] == 'connFIX0':
            parentName = 'root'
            numLev = 1
        for hType in hostToSlice[sliNum]:
            host = 'host'+hType
            priority = 0
            if differentiatePrios == True and host != 'hostVIP' and host != 'hostSSH':
                priority = 1
            for num in range(numHostsPerType[host]):
                leafClassesConfigs[host+str(num)] = [reqBitratesPerType[host], ceilBitrates[host], priority, queueInt, parentName, 0]
                queueInt += 1
        if sliceNames[sliNum] != 'connFIX0':
            # For inner class: assured, guaranteed, parent, level
            innerClassConfigs[sliceNames[sliNum]] = [sliAlloc[sliNum], sliAlloc[sliNum], 'root', 1]
    prefIPno = 0
    for host in cliTypes:
        hostIPprefixes[host] = '10.'+str(prefIPno)
        prefIPno += 1
    prefIPno = 0
    for server in serverTypes:
        serverIPprefixes[server] = '10.'+str(prefIPno+10)
        prefIPno += 1

    genHTBconfigWithInner(configName, int(availBand*1000), leafClassesConfigs, innerClassConfigs, numLev)
    hostNums = [numHostsPerType[x] for x in numHostsPerType]
    genBaselineRoutingConfig(configName, cliTypes, hostNums, hostIPprefixes, serverTypes, serverIPprefixes)
    genBaselineIniConfig(configName, baseName, numHostsPerType, hostIPprefixes, int(availBand*1000000), ceilMultiplier, guaranteeMultiplier)

    f2 = open('../5gNS/simulations/runCommandsFlowsV4.txt', 'a+')
    f2.write('./runAndExportSimConfigWithCleanup.sh -i qosFlowsConfig.ini -c ' + configName + ' -s 1\n')
    f2.close()

### !!! IMPORTANT !!! The generated configs are automatically integrated into qosFlowsConfig.ini and will only work if integrated into that file!!!
targetQoE = [3.5]
assuredMulti = [1.0]
rates = [100]
maxNumCli = [150]
ceils = [1.0, 1.25, 1.5, 1.75, 2.0]
trafficMix = {'VID' : 0.4, 
              'LVD' : 0.2, 
              'FDO' : 0.05, 
              'VIP' : 0.3, 
              'SSH' : 0.05}
seed = 'thisIsInteresting'
expNamePrefix = 'qosFlowsV5'
consideredClients = ['VID', 'LVD', 'FDO', 'VIP', 'SSH']
for rate, maxCli in zip(rates, maxNumCli):
    for qoE in targetQoE:
        for mult in assuredMulti:
            for ceil in ceils:
                genAllSliConfigsHTBRun(expNamePrefix+'Base_R'+str(int(rate))+'_Q'+str(int(qoE*10))+'_M'+str(int(mult*100))+'_C'+str(int(ceil*100)), 'liteCbaselineTestTokenQoS_base', expNamePrefix, trafficMix, rate, qoE, consideredClients, [consideredClients], ['connFIX0'], maxCli, ceil, mult, 'False', seed)
                genAllSliConfigsHTBRun(expNamePrefix+'5SlicesHTB_R'+str(int(rate))+'_Q'+str(int(qoE*10))+'_M'+str(int(mult*100))+'_C'+str(int(ceil*100)), 'liteCbaselineTestTokenQoS_base', expNamePrefix, trafficMix, rate, qoE, consideredClients, [[x] for x in consideredClients], ['conn'+x for x in consideredClients], maxCli, ceil, mult, 'False', seed)
                admitted, gbrs, mbrs, sliceRes = simpleAdmission(expNamePrefix, rate*1000, qoE, trafficMix, maxCli, ceil, mult, [[x] for x in consideredClients], seed)
                print(admitted, gbrs, mbrs, sliceRes)
                for cli in consideredClients:
                    numHosts = admitted['host'+cli]
                    availResources = sliceRes[consideredClients.index(cli)]
                    print(cli, numHosts, availResources)
                    cliIdent = cli[0]+'o'+cli[1:]
                    genAllSliConfigsHTBRun(expNamePrefix+'5SlicesNoHTB'+cliIdent+'Slice_R'+str(int(rate))+'_Q'+str(int(qoE*10))+'_M'+str(int(mult*100))+'_C'+str(int(ceil*100)), 'liteCbaselineTestTokenQoS_base', expNamePrefix, {cli : 1.0}, availResources/1000.0, qoE, [cli], [[cli]], ['connFIX0'], numHosts, ceil, mult, 'False', seed)
