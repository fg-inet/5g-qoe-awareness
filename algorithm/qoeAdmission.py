import xml.etree.ElementTree as ET
import numpy as np

import delayEstimation as delEst
import qoeEstimation as qoeEst


def getBandForQoECli(host, desQoE):
    qoeEstimator = qoeEst.ClientQoeEstimator(host)
    # print(qoeEstimator.xAxis)
    # print(qoeEstimator.yAxis)
    # delays = [delEst.estDelay(host, x) for x in qoeEstimator.xAxis]
    qoe = np.array([qoeEstimator.estQoEb(x) for x in qoeEstimator.yAxis])
    # print(qoe)
    idx = np.abs(qoe - desQoE).argmin()
    # print('Selected values for', host,':')
    # print('\tDesired QoE:', desQoE)
    # print('\tClosest Selected QoE:', qoe[idx])
    # print('\tCorresponding bitrate:', qoeEstimator.yAxis[idx])
    return qoeEstimator.yAxis[idx]
    # delayEstimator = delEst.estDelay()
    # mosMap = np.array(qoeEstimator.mosMap)
    # print(mosMap)
    # qoeEstimator.xAxis
    # qoeEstimator.yAxis

    # print (np.abs(mosMap - desQoE).argmin())

def simpleAdmission(availBand, desiredQoE, cliTypes, maxNumCliType):
    usedBand = 0
    numHostsPerType = {}
    reqBitratesPerType = {}
    for host in cliTypes:
        reqBitratesPerType[host] = getBandForQoECli(host, desiredQoE)
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
                # print(host, numHostsPerType[host])
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
            ceilBitrates[host] = reqBitratesPerType[host] * 1.25

    return numHostsPerType, reqBitratesPerType, ceilBitrates

# print(simpleAdmission(100000, 3, ['hostVIP', 'hostSSH', 'hostVID', 'hostLVD', 'hostFDO'], 50))
# simpleAdmission(200000, 3.5, ['hostVIP', 'hostSSH', 'hostVID', 'hostLVD', 'hostFDO'], 50)
# simpleAdmission(200000, 4, ['hostVIP', 'hostSSH', 'hostVID', 'hostLVD', 'hostFDO'], 50)

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

# genHTBconfig('stasTest10a', 10000, {'One':[4000, 7000, 0, 0], 'Two':[2000, 5000, 0, 1]})

def genBaselineRoutingConfig(configName, hostTypes, hostNums, hostIPprefixes, serverTypes, serverIPprefixes):
    configElem = ET.Element('config')
    for host,nums in zip(hostTypes, hostNums):
        for num in range(nums):
            interfaceElem = ET.SubElement(configElem, 'interface')
            interfaceElem.set('hosts', host+'['+str(num)+']')
            interfaceElem.set('names', 'ppp0')
            interfaceElem.set('address', hostIPprefixes[host]+'.0.'+str(4*num))
            interfaceElem.set('netmask', '255.255.255.252')
        interfaceElem = ET.SubElement(configElem, 'interface')
        interfaceElem.set('hosts', 'router0')
        interfaceElem.set('towards', host+'[*]')
        interfaceElem.set('address', hostIPprefixes[host]+'.0.x')
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

# genBaselineRoutingConfig('stasTest10a', ['hostFDO'], [2], {'hostFDO':'10.3'}, ['serverFDO'],  {'serverFDO':'10.6'})

def genBaselineIniConfig(confName, base, numHostsPerType, hostIPprefixes, availBand):
    sumHosts = 0

    packFilters = '\"'
    packDataFiltersR0 = '\"'
    packDataFiltersR1 = '\"'

    for host in numHostsPerType:
        numHostsType = numHostsPerType[host]
        sumHosts += numHostsType
        for num in range(numHostsType):
            packFilters += '*;'
            packDataFiltersR0 += 'sourceAddress(' + hostIPprefixes[host]+'.0.'+str(4*num) + ');'
            packDataFiltersR1 += 'destinationAddress(' + hostIPprefixes[host]+'.0.'+str(4*num) + ');'


    packFilters = packFilters[:-1]
    packDataFiltersR0 = packDataFiltersR0[:-1]
    packDataFiltersR1 = packDataFiltersR1[:-1]

    packFilters += '\"'
    packDataFiltersR0 += '\"'
    packDataFiltersR1 += '\"'
    

    configString = '[Config ' + confName + ']\n'
    configString += 'description = \"Configuration for ' + confName + '. All five applications. No slicing. QoS employed.\"\n\n'
    configString += 'extends = ' + base + '\n\n'
    configString += '*.configurator.config = xmldoc(\"configs/baseQoS/' + confName + 'Routing.xml\")\n\n'
    configString += '*.nVID = ' + str(numHostsPerType['hostVID']) + ' # Number of video clients\n'
    configString += '*.nLVD = ' + str(numHostsPerType['hostLVD']) + ' # Number of live video client\n'
    configString += '*.nFDO = ' + str(numHostsPerType['hostFDO']) + ' # Number of file download clients\n'
    configString += '*.nSSH = ' + str(numHostsPerType['hostSSH']) + ' # Number of SSH clients\n'
    configString += '*.nVIP = ' + str(numHostsPerType['hostVIP']) + ' # Number of VoIP clients\n\n'
    configString += '*.router*.ppp[0].ppp.queue.typename = \"HTBQueue\"\n'
    configString += '*.router*.ppp[0].ppp.queue.numQueues = ' + str(sumHosts) + '\n'
    configString += '*.router*.ppp[0].ppp.queue.htbHysterisis = false\n'
    configString += '*.router*.ppp[0].ppp.queue.htbTreeConfig = xmldoc(\"configs/htbTree/' + confName + 'HTB.xml\")\n'
    configString += '*.router*.ppp[0].ppp.queue.classifier.defaultGateIndex = 0\n'
    configString += '*.router*.ppp[0].ppp.queue.classifier.packetFilters = ' + packFilters + '\n'
    configString += '*.router0.ppp[0].ppp.queue.classifier.packetDataFilters = ' + packDataFiltersR0 + '\n'
    configString += '*.router1.ppp[0].ppp.queue.classifier.packetDataFilters = ' + packDataFiltersR1 + '\n\n'

    configString += '**.connFIX0.datarate = ' + str(availBand) + 'Mbps\n'
    f = open(confName+".txt", "w")
    f.write(configString)
    f.close()
    # print(configString)

# genBaselineIniConfig('stasTest10a', 'baselineTestTokenQoS_base', {'hostVIP' : 5, 'hostSSH' : 5, 'hostVID' : 5, 'hostLVD' : 5, 'hostFDO' : 5}, {'hostVIP' : '10.1', 'hostSSH' : '10.2', 'hostVID' : '10.3', 'hostLVD' : '10.4', 'hostFDO' : '10.5'}, 100)

def genAllBaselineConfigsRun(configName, baseName, availBand, desiredQoE, types, maxNumCliType):
    cliTypes = ['host'+x for x in types]
    serverTypes = ['server'+x for x in types]
    numHostsPerType, reqBitratesPerType, ceilBitrates = simpleAdmission(availBand*1000, desiredQoE, cliTypes, maxNumCliType)
    print(numHostsPerType, reqBitratesPerType, ceilBitrates)
    # {'One':[4000, 7000, 0, 0], 'Two':[2000, 5000, 0, 1]}
    leafClassesConfigs = {}
    hostIPprefixes = {}
    serverIPprefixes = {}
    queueInt = 0
    prefIPno = 0
    for host in cliTypes:
        for num in range(numHostsPerType[host]):
            leafClassesConfigs[host+str(num)] = [reqBitratesPerType[host], ceilBitrates[host], 0, queueInt]
            queueInt += 1
        hostIPprefixes[host] = '10.'+str(prefIPno)
        prefIPno += 1
    prefIPno = 0
    for server in serverTypes:
        serverIPprefixes[server] = '10.'+str(prefIPno+10)
        prefIPno += 1
    genHTBconfig(configName, availBand*1000, leafClassesConfigs)
    hostNums = [numHostsPerType[x] for x in numHostsPerType]
    genBaselineRoutingConfig(configName, cliTypes, hostNums, hostIPprefixes, serverTypes, serverIPprefixes)
    genBaselineIniConfig(configName, baseName, numHostsPerType, hostIPprefixes, availBand)

genAllBaselineConfigsRun('test', 'baselineTestTokenQoS_base', 100, 3.0, ['VIP', 'SSH', 'VID', 'LVD', 'FDO'], 50)