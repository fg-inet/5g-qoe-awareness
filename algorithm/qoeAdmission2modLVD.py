import xml.etree.ElementTree as ET
import numpy as np

import delayEstimation as delEst
import qoeEstimation as qoeEst

import shutil

def getBandForQoECli(host, desQoE):
    qoeEstimator = qoeEst.ClientQoeEstimator(host)
    qoe = np.array([qoeEstimator.estQoEb(x) for x in qoeEstimator.yAxis])
    idx = np.abs(qoe - desQoE).argmin()
    return qoeEstimator.yAxis[idx]

# default: ceilMultiplier = 1.25; guaranteeMultiplier = 1.0
def simpleAdmission(availBand, desiredQoE, cliTypes, maxNumCliType, ceilMultiplier, guaranteeMultiplier):
    usedBand = 0
    numHostsPerType = {}
    reqBitratesPerType = {}
    for host in cliTypes:
        if host == 'hostLVD':
            if desiredQoE == 3.0:
                reqBitratesPerType[host] = 420.0 * 1.1
            elif desiredQoE == 3.5:
                reqBitratesPerType[host] = 660.0 * 1.1
            elif desiredQoE == 4.0:
                reqBitratesPerType[host] = 1820.0 * 1.1
        else:
            reqBitratesPerType[host] = getBandForQoECli(host, desiredQoE)*guaranteeMultiplier
        print('For a QoE of', desiredQoE, host, 'needs', reqBitratesPerType[host])
        numHostsPerType[host] = 0
    numSameRes = 0
    oldBand = 0
    while usedBand < availBand:
        for host in cliTypes:
            tryAdd = usedBand + reqBitratesPerType[host]
            if tryAdd < availBand and numHostsPerType[host] < maxNumCliType:
                usedBand = tryAdd
                numHostsPerType[host] += 1
        if oldBand == usedBand:
            numSameRes += 1
        else:
            numSameRes = 0
        oldBand = usedBand
        if numSameRes > 10:
            break
    
    print('Hosts admitted for desired QoE of', desiredQoE, 'and link bitrate of', availBand, 'Kbps is :', numHostsPerType)
    print('This allocation will use', usedBand, 'Kbps out of available', availBand, 'Kbps')

    ceilBitrates = {}
    for host in cliTypes:
        if host == 'hostFDO':
            ceilBitrates[host] = reqBitratesPerType[host]
        else:
            ceilBitrates[host] = reqBitratesPerType[host] * ceilMultiplier

    return numHostsPerType, reqBitratesPerType, ceilBitrates

# print(simpleAdmission(100000, 3, ['hostVIP', 'hostSSH', 'hostVID', 'hostLVD', 'hostFDO'], 50))
# simpleAdmission(200000, 3.5, ['hostVIP', 'hostSSH', 'hostVID', 'hostLVD', 'hostFDO'], 50)
# simpleAdmission(200000, 4, ['hostVIP', 'hostSSH', 'hostVID', 'hostLVD', 'hostFDO'], 50)

# print(simpleAdmission(100000, 2.5, ['hostVIP', 'hostSSH', 'hostVID', 'hostLVD', 'hostFDO'], 50, 2.0, 1.0))

# getBandForQoECli('hostFDO', 3)

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

# {leafName:[assuredRate, ceilRate, priority, queueNum]}
def genHTBconfig(configName, linkSpeed, leafClassesConfigs):

    configElem = ET.Element('config')
    prepareHTBClassXML(configElem, 'root', '', 'NULL', str(linkSpeed), str(linkSpeed), '1600', '1600', '1', '1600', '60', '', '')
    for leaf in leafClassesConfigs:
        prepareHTBClassXML(configElem, 'leaf', leaf, 'root', str(leafClassesConfigs[leaf][0]), str(leafClassesConfigs[leaf][1]), '1600', '1600', '0', '1600', '60', str(leafClassesConfigs[leaf][2]), str(leafClassesConfigs[leaf][3]))
    # prepareHTBClassXML(configElem, 'leaf', 'Two', 'root', '2000', '5000', '1600', '1600', '0', '1600', '60', '0', '1')

    # create a new XML file with the results
    mydata = ET.tostring(configElem)
    myfile = open(configName+"HTB.xml", "wb")
    myfile.write(mydata)
    shutil.copy2(configName+"HTB.xml", '../5gNS/simulations/configs/htbTree')

# {leafName:[assuredRate, ceilRate, priority, queueNum, parentId, level]}
# {innerName:[assuredRate, ceilRate, parentId, level]}
def genHTBconfigWithInner(configName, linkSpeed, leafClassesConfigs, innerClassesConfigs, numLevels):

    configElem = ET.Element('config')
    prepareHTBClassXML(configElem, 'root', '', 'NULL', str(linkSpeed), str(linkSpeed), '1600', '1600', str(numLevels), '1600', '60', '', '')
    
    for inner in innerClassesConfigs:
        # print(inner)
        prepareHTBClassXML(configElem, 'inner', inner, str(innerClassesConfigs[inner][2]), str(innerClassesConfigs[inner][0]), str(innerClassesConfigs[inner][1]), '1600', '1600', str(innerClassesConfigs[inner][3]), '1600', '60', '', '')
    
    for leaf in leafClassesConfigs:
        prepareHTBClassXML(configElem, 'leaf', leaf, str(leafClassesConfigs[leaf][4]), str(leafClassesConfigs[leaf][0]), str(leafClassesConfigs[leaf][1]), '1600', '1600', str(leafClassesConfigs[leaf][5]), '1600', '60', str(leafClassesConfigs[leaf][2]), str(leafClassesConfigs[leaf][3]))
    
    
    # prepareHTBClassXML(configElem, 'leaf', 'Two', 'root', '2000', '5000', '1600', '1600', '0', '1600', '60', '0', '1')

    # create a new XML file with the results
    mydata = ET.tostring(configElem)
    myfile = open(configName+"HTB.xml", "wb")
    myfile.write(mydata)
    shutil.copy2(configName+"HTB.xml", '../5gNS/simulations/configs/htbTree')

# genHTBconfig('stasTest10a', 10000, {'One':[4000, 7000, 0, 0], 'Two':[2000, 5000, 0, 1]})

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
    myfile = open(configName+"Routing.xml", "wb")
    myfile.write(mydata)
    shutil.copy2(configName+"Routing.xml", '../5gNS/simulations/configs/baseQoS')


# genBaselineRoutingConfig('stasTest10a', ['hostFDO'], [2], {'hostFDO':'10.3'}, ['serverFDO'],  {'serverFDO':'10.6'})

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
    configString += '*.nVID = ' + str(numHostsPerType['hostVID']) + ' # Number of video clients\n'
    configString += '*.nLVD = ' + str(numHostsPerType['hostLVD']) + ' # Number of live video client\n'
    configString += '*.nFDO = ' + str(numHostsPerType['hostFDO']) + ' # Number of file download clients\n'
    configString += '*.nSSH = ' + str(numHostsPerType['hostSSH']) + ' # Number of SSH clients\n'
    configString += '*.nVIP = ' + str(numHostsPerType['hostVIP']) + ' # Number of VoIP clients\n\n'
    configString += '*.router*.ppp[0].ppp.queue.typename = \"HTBQueue\"\n'
    configString += '*.router*.ppp[0].ppp.queue.numQueues = ' + str(sumHosts) + '\n'
    configString += '*.router*.ppp[0].ppp.queue.queue[*].typename = \"DropTailQueue\"\n'
    configString += '*.router*.ppp[0].ppp.queue.htbHysterisis = false\n'
    configString += '*.router*.ppp[0].ppp.queue.htbTreeConfig = xmldoc(\"configs/htbTree/' + confName + 'HTB.xml\")\n'
    configString += '*.router*.ppp[0].ppp.queue.classifier.defaultGateIndex = 0\n'
    configString += '*.router*.ppp[0].ppp.queue.classifier.packetFilters = ' + packFilters + '\n'
    configString += '*.router0.ppp[0].ppp.queue.classifier.packetDataFilters = ' + packDataFiltersR0 + '\n'
    configString += '*.router1.ppp[0].ppp.queue.classifier.packetDataFilters = ' + packDataFiltersR1 + '\n\n'

    configString += '**.connFIX0.datarate = ' + str(availBand) + 'Mbps\n'
    configString += '**.connFIX0.delay = 40ms\n\n\n'

    f = open(confName+".txt", "w")
    f.write(configString)
    f.close()

    f2 = open('../5gNS/simulations/htbSimpleTestLite.ini', 'a')
    f2.write(configString)
    f2.close()
    # print(configString)


def genAllSliConfigsHTBRun(configName, baseName, availBand, desiredQoE, types, hostToSlice, sliceNames, maxNumCliType, ceilMultiplier, guaranteeMultiplier, differentiatePrios):
    cliTypes = ['host'+x for x in types]
    serverTypes = ['server'+x for x in types]
    numHostsPerType, reqBitratesPerType, ceilBitrates = simpleAdmission(availBand*1000, desiredQoE, ['host'+x for x in types], maxNumCliType, ceilMultiplier, guaranteeMultiplier)
    hostIPprefixes = {}
    serverIPprefixes = {}
    leafClassesConfigs = {}
    innerClassConfigs = {}
    queueInt = 0
    # {leafName:[assuredRate, ceilRate, priority, queueNum, parentId, level]}
    # {innerName:[assuredRate, ceilRate, parentId, level]}
    numLev = 2
    for sliNum in range(len(hostToSlice)):
        sumGuaranteesBandSli = 0
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
            sumGuaranteesBandSli += reqBitratesPerType[host] * numHostsPerType[host]
        if sliceNames[sliNum] != 'connFIX0':
            # For inner class: assured, guaranteed, parent, level
            innerClassConfigs[sliceNames[sliNum]] = [sumGuaranteesBandSli, sumGuaranteesBandSli, 'root', 1]

    prefIPno = 0
    for host in cliTypes:
        hostIPprefixes[host] = '10.'+str(prefIPno)
        prefIPno += 1
    prefIPno = 0
    for server in serverTypes:
        serverIPprefixes[server] = '10.'+str(prefIPno+10)
        prefIPno += 1

    genHTBconfigWithInner(configName, availBand*1000, leafClassesConfigs, innerClassConfigs, numLev)
    hostNums = [numHostsPerType[x] for x in numHostsPerType]
    genBaselineRoutingConfig(configName, cliTypes, hostNums, hostIPprefixes, serverTypes, serverIPprefixes)
    genBaselineIniConfig(configName, baseName, numHostsPerType, hostIPprefixes, availBand, ceilMultiplier, guaranteeMultiplier)

    f2 = open('../5gNS/simulations/runCommandsModL2iQ.txt', 'a+')
    f2.write('./runAndExportSimConfig.sh -i htbSimpleTestLite.ini -c ' + configName + ' -s 1\n')
    f2.close()


targetQoE = [3.0,3.5,4.0]
assuredMulti = [1.0]
rates = [100]
maxCliRate = [50]
ceils = [1.0, 1.2]
dPrio = [False]


# targetQoE = [4.0, 3.5, 3.0]
# assuredMulti = [1.0]
# rates = [100, 200]
# maxCliRate = [50, 100]
# ceils = [1.0, 1.1, 1.25, 1.4]
for rate, maxCli in zip(rates, maxCliRate):
    for qoE in targetQoE:
        for mult in assuredMulti:
            for ceil in ceils:
                for dp in dPrio:
                    genAllSliConfigsHTBRun('expQoeAdmissionModL2aW40msNo1Base_R'+str(int(rate))+'_Q'+str(int(qoE*10))+'_M'+str(int(mult*100))+'_C'+str(int(ceil*100))+'_P'+str(dp), 'liteCbaselineTestTokenQoS_base', rate, qoE, ['VID', 'LVD', 'FDO', 'VIP', 'SSH'], [['VID', 'LVD', 'FDO', 'VIP', 'SSH']], ['connFIX0'], maxCli, ceil, mult, dp)
                    genAllSliConfigsHTBRun('expQoeAdmissionModL2aW40msNo2_2sli_R'+str(int(rate))+'_Q'+str(int(qoE*10))+'_M'+str(int(mult*100))+'_C'+str(int(ceil*100))+'_P'+str(dp), 'liteCbaselineTestTokenQoS_base', rate, qoE, ['VID', 'LVD', 'FDO', 'VIP', 'SSH'], [['VID', 'LVD', 'FDO'], ['VIP', 'SSH']], ['connBWS', 'connDES'], maxCli, ceil, mult, dp)
                    genAllSliConfigsHTBRun('expQoeAdmissionModL2aW40msNo3_5sli_R'+str(int(rate))+'_Q'+str(int(qoE*10))+'_M'+str(int(mult*100))+'_C'+str(int(ceil*100))+'_P'+str(dp), 'liteCbaselineTestTokenQoS_base', rate, qoE, ['VID', 'LVD', 'FDO', 'VIP', 'SSH'], [['VID'], ['LVD'], ['FDO'], ['VIP'], ['SSH']], ['connVID', 'connLVD', 'connFDO', 'connVIP', 'connSSH'], maxCli, ceil, mult, dp)
