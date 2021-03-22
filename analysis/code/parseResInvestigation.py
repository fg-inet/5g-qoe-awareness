import pandas
import csv
import statistics
# from termcolor import colored
import sys
import os

maxSimTime = 400
DEBUG = 0

downlink = ['Downlink', 'rxPkOk:vector(packetBytes)']
uplink = ['Uplink', 'txPk:vector(packetBytes)']

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

# Function that imports node information into a dataframe
#   - testName - name of the test
#   - numCLI - total number of clients in the test
#   - nodeSplit - number of nodes running certain applications in the test
#       [numVID, numFDO, numSSH, numVIP]
#   - nodeType - type of the node to import (String), curr. used
#       hostVID, hostFDO, hostSSH, hostVIP, links, serverSSH
#   - nodeNum - number of the node to import, omitted if -1
def importDF(testName, numCLI, nodeTypes, nodeSplit, nodeType, nodeNum):
    # File that will be read
    fullScenarioExportName = makeFullScenarioName(testName, numCLI, nodeTypes, nodeSplit)
    fileToRead = '../' + str(testName) + '/' + fullScenarioExportName + '/vectors/' + fullScenarioExportName + '_' + makeNodeIdentifier(nodeType, nodeNum) + '_vec.csv'
    print("Importing: " + fileToRead)
    # Read the CSV
    return pandas.read_csv(fileToRead)

def filterDFType(df, filterType):
    return df.filter(like=filterType)

def getFilteredDFtypeAndTS(df, filterType):
    filteredDF = filterDFType(df, filterType)
    if len(filteredDF.columns):
        colNoTS = df.columns.get_loc(df.filter(filteredDF).columns[0])
        return df.iloc[:,[colNoTS,colNoTS+1]].dropna()
    else:
        return pandas.DataFrame(columns=['ts', 'tp'])

def calculateThrougputPerSecondDirection(df, direction, nodeIdent):
    dirDF = getFilteredDFtypeAndTS(df, direction[1])
    dirDF = dirDF.rename(columns={str(dirDF.columns[0]) : "ts", str(dirDF.columns[1]) : "bytes"})
    tB = [0,1] # time bounds for calculation
    colName = direction[0] + ' Throughput ' + nodeIdent
    tpDirDF = pandas.DataFrame(columns=[colName])
    while tB[1] <= maxSimTime:
        if DEBUG: print(tB, end =" -> Throughput: ")
        throughput = dirDF.loc[(dirDF['ts'] > tB[0]) & (dirDF['ts'] <= tB[1])]["bytes"].sum()
        tpDirDF = tpDirDF.append({colName : throughput*8/1000}, ignore_index=True)
        if DEBUG: print(throughput*8/1000, end=" kbps\n")
        tB = [x+1 for x in tB]
    return tpDirDF

def extractNodeThroughputDirection(testName, numCLI, nodeTypes, nodeSplit, nodeType, nodeNum, direction):
    print('TP ' + direction[0], end=' - ')
    nodeDF = importDF(testName, numCLI, nodeTypes, nodeSplit, nodeType, nodeNum)
    nodeIdent = makeNodeIdentifier(nodeType, nodeNum)
    return calculateThrougputPerSecondDirection(nodeDF, direction, nodeIdent)

def extractAllThroughputsDirection(testName, numCLI, nodeTypes, nodeSplit, nodeTypesToExtract, numSlices, direction):
    # Prepare result dataframe
    tpDFall = pandas.DataFrame()
    # Add link tps
    for i in range(numSlices):
        tpDFall = pandas.concat([tpDFall,extractNodeThroughputDirection(testName, numCLI, nodeTypes, nodeSplit, 'resAllocLink', i ,direction)],axis=1,ignore_index=False)
    # Add nodes tps
    for nodeType,numNodes in zip(nodeTypesToExtract,nodeSplit):
        for nodeNum in range(numNodes):
            tpDFall = pandas.concat([tpDFall,extractNodeThroughputDirection(testName, numCLI, nodeTypes, nodeSplit, nodeType, nodeNum ,direction)],axis=1,ignore_index=False)
    if not os.path.exists('../exports/extracted/throughputs/'):
        os.makedirs('../exports/extracted/throughputs/')
    # Export to csv
    tpDFall.to_csv(path_or_buf='../exports/extracted/throughputs/'+makeFullScenarioName(testName, numCLI, nodeTypes, nodeSplit)+'_'+direction[0]+'.csv')

def extractNodeDataTypeToDF(testName, numCLI, nodeTypes, nodeSplit, nodeType, nodeNum, dataType, dataIdent):
    print(dataIdent, end=' - ')
    nodeDF = importDF(testName, numCLI, nodeTypes, nodeSplit, nodeType, nodeNum)
    dataTypeDF = getFilteredDFtypeAndTS(nodeDF, dataType)
    nodeIdent = makeNodeIdentifier(nodeType, nodeNum)
    dataTypeDF = dataTypeDF.rename(columns={str(dataTypeDF.columns[0]) : nodeIdent + " " + dataIdent + " TS", str(dataTypeDF.columns[1]) : nodeIdent + " " + dataIdent + " Val"})
    return dataTypeDF

def extractAllDataTypeToDF(testName, numCLI, nodeTypes, nodeSplit, nodeTypesToExtract, dataType, dataIdent, folderName):
    dfAll = pandas.DataFrame()
    for nodeType,numNodes in zip(nodeTypes,nodeSplit):
        if nodeType in nodeTypesToExtract:
            for nodeNum in range(numNodes):
                dfAll = pandas.concat([dfAll,extractNodeDataTypeToDF(testName, numCLI, nodeTypes, nodeSplit, nodeType, nodeNum, dataType, dataIdent)],axis=1,ignore_index=False)

    prePath = '../exports/extracted/'+str(folderName)+'/'
    if not os.path.exists(prePath):
        os.makedirs(prePath)
    dfAll.to_csv(path_or_buf=prePath + makeFullScenarioName(testName, numCLI, nodeTypes, nodeSplit) + '.csv')

def extractRTO(testName, numCLI, nodeTypes, nodeSplit, nodeType, nodeNum):
    print('RTO', end=' - ')
    nodeDF = importDF(testName, numCLI, nodeTypes, nodeSplit, nodeType, nodeNum)
    filteredDF = filterDFType(nodeDF, 'RTO ')
    rtos = []
    colTSList = nodeDF.filter(filteredDF).columns
    for col in colTSList:
        colNoTS = nodeDF.columns.get_loc(col)
        rtos.extend(nodeDF.iloc[:,colNoTS+1].dropna().tolist())
    filteredDFnumSes = filterDFType(nodeDF, 'advertised window')
    numSession = len(list(filteredDFnumSes))
    print('Total Number of sessions at the SSH server: ' + str(numSession))
    filteredDF2 = filterDFType(nodeDF, 'RTOs ')
    print(filteredDF2)
    numSessionWithRTO = len(list(filteredDF2))
    print('Number of sessions at the SSH server where at least one retransmission timeout occured: ' + str(numSessionWithRTO))

    with open('../exports/extracted/rto/'+makeFullScenarioName(testName, numCLI, nodeTypes, nodeSplit)+'.csv', mode='w') as writeFile:
        fw = csv.writer(writeFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
        fw.writerow(rtos)
        fw.writerow([numSession])
        fw.writerow([numSessionWithRTO])

def getRTTValuesSingleNode(testName, numCLI, nodeTypes, nodeSplit, nodeType, nodeNum, valueType):
    df = importDF(testName, numCLI, nodeTypes, nodeSplit, nodeType, nodeNum)
    df = df.shift(periods=-1, axis='columns')
    valueDF = filterDFType(df, valueType).dropna()
    resList = []
    for col in valueDF:
        resList.extend(valueDF[col].tolist())
    return resList

def extractRTTValues(testName, numCLI, nodeTypes, nodeSplit, nodeTypesToExtract):
    dfAll = pandas.DataFrame()
    for nodeType,numNodes in zip(nodeTypes,nodeSplit):
        if nodeType in nodeTypesToExtract:
            for nodeNum in range(numNodes):
                clientDf = pandas.DataFrame({makeNodeIdentifier(nodeType, nodeNum) + " rtt Val" : getRTTValuesSingleNode(testName, numCLI, nodeTypes, nodeSplit, nodeType, nodeNum, 'rtt')})
                dfAll = pandas.concat([dfAll,clientDf], axis=1)
                # dfAll[makeNodeIdentifier(nodeType, nodeNum) + " rtt Val"] = getRTTValuesSingleNode(testName, numCLI, nodeTypes, nodeSplit, nodeType, nodeNum, 'rtt')
    prePath = '../exports/extracted/rtt/'
    if not os.path.exists(prePath):
        os.makedirs(prePath)
    dfAll.to_csv(path_or_buf=prePath + makeFullScenarioName(testName, numCLI, nodeTypes, nodeSplit) + '.csv')

def extractAll(testName, nodeTypes, nodeSplit, numSlices):
    numCLI = sum(nodeSplit)
    # Extract throughputs for all nodes
    extractAllThroughputsDirection(testName, numCLI, nodeTypes, nodeSplit, nodeTypes, numSlices, downlink)
    extractAllThroughputsDirection(testName, numCLI, nodeTypes, nodeSplit, nodeTypes, numSlices, uplink)

    # # Extract all mos values
    extractAllDataTypeToDF(testName, numCLI, nodeTypes, nodeSplit, nodeTypes, 'mos', 'Mos', 'mos')
    extractAllDataTypeToDF(testName, numCLI, nodeTypes, nodeSplit, nodeTypes, 'endToEndDelay', 'E2ED', 'endToEndDelay')

    # Extract mean client rtt for all node types except VoIP
    extractRTTValues(testName, numCLI, nodeTypes, nodeSplit, ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH'])

    # Extract additional data for SSH application
    # if 'hostSSH' in nodeTypes: 
    #     extractAllDataTypeToDF(testName, numCLI, nodeTypes, nodeSplit, ['hostSSH'], 'roundTripTime', 'RTT', 'rtt')
        # extractRTO(testName, numCLI, nodeTypes, nodeSplit, 'serverSSH', -1)
    
    # Extract additional data for VoIP application
    if 'hostVIP' in nodeTypes:
        extractAllDataTypeToDF(testName, numCLI, nodeTypes, nodeSplit, ['hostVIP'], 'endToEndDelay', 'E2ED', 'e2ed')
        extractAllDataTypeToDF(testName, numCLI, nodeTypes, nodeSplit, ['hostVIP'], 'packetLossRate', 'PkLR', 'pklr')
        extractAllDataTypeToDF(testName, numCLI, nodeTypes, nodeSplit, ['hostVIP'], 'playoutDelay', 'PlDel', 'pldel')
        extractAllDataTypeToDF(testName, numCLI, nodeTypes, nodeSplit, ['hostVIP'], 'playoutLossRate', 'PlLR', 'pllr')
        extractAllDataTypeToDF(testName, numCLI, nodeTypes, nodeSplit, ['hostVIP'], 'taildropLossRate', 'TDLR', 'tdlr')
    
    if 'hostLVD' in nodeTypes:
        extractAllDataTypeToDF(testName, numCLI, nodeTypes, nodeSplit, ['hostLVD'], 'DASHliveDelay', 'DLVD', 'dlvd')
    
    if 'hostVID' in nodeTypes and 'hostLVD' in nodeTypes:
        extractAllDataTypeToDF(testName, numCLI, nodeTypes, nodeSplit, ['hostVID', 'hostLVD'], 'DASHBufferLength', 'DABL', 'dabl')
        extractAllDataTypeToDF(testName, numCLI, nodeTypes, nodeSplit, ['hostVID', 'hostLVD'], 'DASHVideoBitrate', 'DAVB', 'davb')
        extractAllDataTypeToDF(testName, numCLI, nodeTypes, nodeSplit, ['hostVID', 'hostLVD'], 'DASHVideoResolution', 'DAVR', 'davr')
        extractAllDataTypeToDF(testName, numCLI, nodeTypes, nodeSplit, ['hostVID', 'hostLVD'], 'DASHmosScore', 'DAMS', 'dams')
        extractAllDataTypeToDF(testName, numCLI, nodeTypes, nodeSplit, ['hostVID', 'hostLVD'], 'DASHEstimatedBitrate', 'DAEB', 'daeb')

# extractAll('baselineTest', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [10,10,10,10,10], 1)
# extractAll('baselineTest', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [20,20,20,20,20], 1)
# extractAll('baselineTest', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [30,30,30,30,30], 1)
# extractAll('baselineTest', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [40,40,40,40,40], 1)
# extractAll('baselineTest', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [50,50,50,50,50], 1)

# extractAll('initialTestHTB_105mbps', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [1,1,1,1,1], 1)
# extractAll('initialTestHTB_105mbps_bla', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [1,1,1,1,1], 1)

# extractAll('test', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [36,36,36,50,37], 1)
# extractAll('test2', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [33,32,33,50,33], 1)


# extractAll('baselineTestNS_2sli_LVD-DES', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [50 for x in range(5)], 2)
# extractAll('baselineTestNS_2sli_LVD-BWS', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [50 for x in range(5)], 2)

# extractAll('baselineTestNS_2sliSingle_LVD-DES', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [50 for x in range(5)], 2)
# extractAll('baselineTestNS_2sliSingle_LVD-BWS', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [50 for x in range(5)], 2)

# extractAll('baselineTestNS_2sliSingle2sli_LVD-DES', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [50 for x in range(5)], 2)
# extractAll('baselineTestNS_2sliSingle2sli_LVD-BWS', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [50 for x in range(5)], 2)

# extractAll('baselineTestNS_2sliDouble_LVD-DES', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [50 for x in range(5)], 2)
# extractAll('baselineTestNS_2sliDouble_LVD-BWS', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [50 for x in range(5)], 2)


# extractAll('baselineTestNS_5sli', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [50 for x in range(5)], 5)

# extractAll('baselineTestNS_5sliSingle', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [50 for x in range(5)], 5)

# extractAll('baselineTestNS_5sliSingle5sli', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [50 for x in range(5)], 5)

# extractAll('baselineTestNS_5sliDouble', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [50 for x in range(5)], 0)

# extractAll('baselineTestTemp', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [10,10,10,10,10], 1)

# extractAll('baselineTestNSPrioQueue_2sliSingle2sliDW_LVD-DES', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [50 for x in range(5)], 2)
# extractAll('baselineTestNSPrioQueue_SingleDW_LVD-DES', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [50 for x in range(5)], 1)
# extractAll('baselineTestNSPrioQueue_SingleDW_LVD-BWS', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [50 for x in range(5)], 1)
# extractAll('baselineTestNSPrioQueueAF_2sliSingle2sliNBS_LVD-BWS', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [50 for x in range(5)], 2)
# extractAll('baselineTestNSPrioQueueAF_SingleNBS_LVD-DES', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [50 for x in range(5)], 1)

# extractAll('baselineTestNSPrioQueue_SingleDWR_LVD-DES', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [50 for x in range(5)], 1)
# extractAll('baselineTestNSPrioQueue_SingleDWR_LVD-BWS', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [50 for x in range(5)], 1)

# extractAll('baselineTestNSPrioQueueDES2_2sliSingle2sli_LVD-DES', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [50 for x in range(5)], 0)
# extractAll('baselineTestNSPrioQueueDES2_2sliSingle2sli_LVD-BWS', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [50 for x in range(5)], 0)
# extractAll('baselineTestNSPrioQueue_2sliSingle2sliDWR2_LVD-DES', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [50 for x in range(5)], 0)
# extractAll('baselineTestNSPrioQueue_2sliSingle2sliDWR2_LVD-BWS', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [50 for x in range(5)], 0)


# extractAll('baselineTestNSPrioQueueAF_Single_LVD-DES', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [50 for x in range(5)], 1)
# extractAll('baselineTestNSPrioQueueAF_SingleLBS_LVD-DES', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [50 for x in range(5)], 1)
# extractAll('baselineTestNSPrioQueueAF_Single50_LVD-DES', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [50 for x in range(5)], 1)

# extractAll('baselineTestNSPrioQueueDES4_2sliSingle2sli_LVD-DES', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [50 for x in range(5)], 0)
# extractAll('baselineTestNSPrioQueueDES4_2sliSingle2sli_LVD-BWS', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [50 for x in range(5)], 0)

# extractAll('baselineTestNSPrioQueue_SingleDWRLQ_LVD-DES', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [50 for x in range(5)], 1)
# extractAll('baselineTestNSPrioQueue_SingleDWRLQ_LVD-BWS', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [50 for x in range(5)], 1)

# extractAll('baselineTestNSPrioQueue_2sliSingle2sliDWRLQ_LVD-DES', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [50 for x in range(5)], 0)
# extractAll('baselineTestNSPrioQueue_2sliSingle2sliDWRLQ_LVD-BWS', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [50 for x in range(5)], 0)

# extractAll('baselineTestNSPrioQueue_2sliSingle2sliDWRLQPD_LVD-DES', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [50 for x in range(5)], 0)
# extractAll('baselineTestNSPrioQueue_2sliSingle2sliDWRLQPD_LVD-BWS', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [50 for x in range(5)], 0)

# extractAll('baselineTestNS_5sli_AlgoTest1', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [50 for x in range(5)], 5)
# extractAll('baselineTestNS_2sli_LVD-DES_AlgoTest3', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [50 for x in range(5)], 2)
# extractAll('baselineTestNS_2sli_LVD-BWS_AlgoTest3', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [50 for x in range(5)], 2)

# extractAll('optimizationAlgoFairness1_5sli_0alpha_SSH100VIP75VID20LVD5FDO50_sSSH3sVIP44sVID14sLVD2sFDO37_fairness_max', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [20,5,50,100,75], 5)
# extractAll('optimizationAlgoFairness1_5sli_5alpha_SSH100VIP20VID75LVD5FDO50_sSSH1sVIP12sVID51sLVD6sFDO30_fairness_max', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [75,5,50,100,20], 5)
# extractAll('optimizationAlgoFairness1_5sli_10alpha_SSH100VIP20VID75LVD5FDO50_sSSH1sVIP12sVID51sLVD6sFDO30_fairness_max', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [75,5,50,100,20], 5)
# extractAll('optimizationAlgoFairness1_5sli_0alpha_SSH100VIP20VID50LVD5FDO75_sSSH4sVIP12sVID35sLVD6sFDO43_min_max', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [50,5,75,100,20], 5)
# extractAll('optimizationAlgoFairness1_5sli_5alpha_SSH100VIP50VID20LVD5FDO75_sSSH1sVIP29sVID15sLVD6sFDO49_min_max', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [20,5,75,100,50], 5)
# extractAll('optimizationAlgoFairness1_5sli_10alpha_SSH100VIP50VID20LVD5FDO75_sSSH1sVIP29sVID15sLVD6sFDO49_min_max', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [20,5,75,100,50], 5)
# extractAll('optimizationAlgoFairness1_5sli_0alpha_SSH100VIP75VID20LVD5FDO50_sSSH3sVIP44sVID14sLVD2sFDO37_mean_max', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [20,5,50,100,75], 5)
# extractAll('optimizationAlgoFairness1_5sli_5alpha_SSH100VIP75VID50LVD5FDO20_sSSH2sVIP44sVID34sLVD6sFDO14_mean_max', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [50,5,20,100,75], 5)
# extractAll('optimizationAlgoFairness1_5sli_10alpha_SSH100VIP75VID50LVD5FDO20_sSSH1sVIP44sVID34sLVD6sFDO15_mean_max', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [50,5,20,100,75], 5)
# extractAll('optimizationAlgoFairness1_5sli_0alpha_SSH50VIP75VID100LVD5FDO20_sSSH7sVIP45sVID20sLVD7sFDO21_fairness_min', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [100,5,20,50,75], 5)
# extractAll('optimizationAlgoFairness1_5sli_5alpha_SSH20VIP100VID75LVD5FDO50_sSSH1sVIP58sVID37sLVD3sFDO1_fairness_min', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [75,5,50,20,100], 5)
# extractAll('optimizationAlgoFairness1_5sli_10alpha_SSH50VIP100VID5LVD20FDO75_sSSH1sVIP36sVID20sLVD20sFDO23_fairness_min', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [5,20,75,50,100], 5)
# extractAll('optimizationAlgoFairness1_5sli_0alpha_SSH5VIP75VID100LVD20FDO50_sSSH1sVIP44sVID48sLVD6sFDO1_min_min', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [100,20,50,5,75], 5)
# extractAll('optimizationAlgoFairness1_5sli_5alpha_SSH20VIP100VID75LVD5FDO50_sSSH1sVIP58sVID37sLVD3sFDO1_min_min', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [75,5,50,20,100], 5)
# extractAll('optimizationAlgoFairness1_5sli_10alpha_SSH5VIP50VID75LVD100FDO20_sSSH18sVIP28sVID29sLVD22sFDO3_min_min', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [75,100,20,5,50], 5)
# extractAll('optimizationAlgoFairness1_5sli_0alpha_SSH5VIP100VID50LVD75FDO20_sSSH1sVIP1sVID50sLVD22sFDO26_mean_min', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [50,75,20,5,100], 5)
# extractAll('optimizationAlgoFairness1_5sli_5alpha_SSH5VIP100VID75LVD20FDO50_sSSH25sVIP26sVID32sLVD6sFDO11_mean_min', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [75,20,50,5,100], 5)
# extractAll('optimizationAlgoFairness1_5sli_10alpha_SSH5VIP75VID50LVD100FDO20_sSSH15sVIP42sVID18sLVD22sFDO3_mean_min', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [50,100,20,5,75], 5)

# extractAll('baselineTestVCD_SSH100VIP75VID20LVD5FDO50', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [20, 5, 50, 100, 75], 1)
# extractAll('baselineTestVCD_SSH100VIP20VID75LVD5FDO50', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [75, 5, 50, 100, 20], 1)
# extractAll('baselineTestVCD_SSH50VIP75VID100LVD5FDO20', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [100, 5, 20, 50, 75], 1)
# extractAll('baselineTestVCD_SSH20VIP100VID75LVD5FDO50', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [75, 5, 50, 20, 100], 1)
# extractAll('baselineTestVCD_SSH50VIP100VID5LVD20FDO75', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [5, 20, 75, 50, 100], 1)
# extractAll('baselineTestVCD_SSH100VIP20VID50LVD5FDO75', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [50, 5, 75, 100, 20], 1)
# extractAll('baselineTestVCD_SSH100VIP50VID20LVD5FDO75', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [20, 5, 75, 100, 50], 1)
# extractAll('baselineTestVCD_SSH5VIP75VID100LVD20FDO50', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [100, 20, 50, 5, 75], 1)
# extractAll('baselineTestVCD_SSH5VIP50VID75LVD100FDO20', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [75, 100, 20, 5, 50], 1)
# extractAll('baselineTestVCD_SSH100VIP75VID50LVD5FDO20', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [50, 5, 20, 100, 75], 1)
# extractAll('baselineTestVCD_SSH5VIP100VID50LVD75FDO20', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [50, 75, 20, 5, 100], 1)
# extractAll('baselineTestVCD_SSH5VIP100VID75LVD20FDO50', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [75, 20, 50, 5, 100], 1)
# extractAll('baselineTestVCD_SSH5VIP75VID50LVD100FDO20', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [50, 100, 20, 5, 75], 1)

# extractAll('optimizationAlgoFairness1_2sli_LVD-BWS_0alpha_SSH100VIP75VID20LVD5FDO50_sDES46sBWS54_ndf_ndf', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [20, 5, 50, 100, 75], 2)
# extractAll('optimizationAlgoFairness1_2sli_LVD-BWS_5alpha_SSH100VIP20VID75LVD5FDO50_sDES14sBWS86_ndf_ndf', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [75, 5, 50, 100, 20], 2)
# extractAll('optimizationAlgoFairness1_2sli_LVD-BWS_10alpha_SSH100VIP20VID75LVD5FDO50_sDES14sBWS86_ndf_ndf', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [75, 5, 50, 100, 20], 2)
# extractAll('optimizationAlgoFairness1_2sli_LVD-BWS_0alpha_SSH50VIP75VID100LVD5FDO20_sDES46sBWS54_ndf_ndf', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [100, 5, 20, 50, 75], 2)
# extractAll('optimizationAlgoFairness1_2sli_LVD-BWS_5alpha_SSH20VIP100VID75LVD5FDO50_sDES58sBWS42_ndf_ndf', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [75, 5, 50, 20, 100], 2)
# extractAll('optimizationAlgoFairness1_2sli_LVD-BWS_10alpha_SSH50VIP100VID5LVD20FDO75_sDES59sBWS41_ndf_ndf', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [5, 20, 75, 50, 100], 2)
# extractAll('optimizationAlgoFairness1_2sli_LVD-BWS_0alpha_SSH100VIP20VID50LVD5FDO75_sDES15sBWS85_ndf_ndf', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [50, 5, 75, 100, 20], 2)
# extractAll('optimizationAlgoFairness1_2sli_LVD-BWS_5alpha_SSH100VIP50VID20LVD5FDO75_sDES31sBWS69_ndf_ndf', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [20, 5, 75, 100, 50], 2)
# extractAll('optimizationAlgoFairness1_2sli_LVD-BWS_10alpha_SSH100VIP50VID20LVD5FDO75_sDES31sBWS69_ndf_ndf', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [20, 5, 75, 100, 50], 2)
# extractAll('optimizationAlgoFairness1_2sli_LVD-BWS_0alpha_SSH5VIP75VID100LVD20FDO50_sDES47sBWS53_ndf_ndf', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [100, 20, 50, 5, 75], 2)
# extractAll('optimizationAlgoFairness1_2sli_LVD-BWS_5alpha_SSH20VIP100VID75LVD5FDO50_sDES58sBWS42_ndf_ndf', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [75, 5, 50, 20, 100], 2)
# extractAll('optimizationAlgoFairness1_2sli_LVD-BWS_10alpha_SSH5VIP50VID75LVD100FDO20_sDES18sBWS82_ndf_ndf', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [75, 100, 20, 5, 50], 2)
# extractAll('optimizationAlgoFairness1_2sli_LVD-BWS_0alpha_SSH100VIP75VID20LVD5FDO50_sDES46sBWS54_ndf_ndf', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [20, 5, 50, 100, 75], 2)
# extractAll('optimizationAlgoFairness1_2sli_LVD-BWS_5alpha_SSH100VIP75VID50LVD5FDO20_sDES46sBWS54_ndf_ndf', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [50, 5, 20, 100, 75], 2)
# extractAll('optimizationAlgoFairness1_2sli_LVD-BWS_10alpha_SSH100VIP75VID50LVD5FDO20_sDES46sBWS54_ndf_ndf', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [50, 5, 20, 100, 75], 2)
# extractAll('optimizationAlgoFairness1_2sli_LVD-BWS_0alpha_SSH5VIP100VID50LVD75FDO20_sDES60sBWS40_ndf_ndf', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [50, 75, 20, 5, 100], 2)
# extractAll('optimizationAlgoFairness1_2sli_LVD-BWS_5alpha_SSH5VIP100VID75LVD20FDO50_sDES57sBWS43_ndf_ndf', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [75, 20, 50, 5, 100], 2)
# extractAll('optimizationAlgoFairness1_2sli_LVD-BWS_10alpha_SSH5VIP75VID50LVD100FDO20_sDES43sBWS57_ndf_ndf', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [50, 100, 20, 5, 75], 2)


# extractAll('baselineTestNS_5sli_AlgoTest_alpha00', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [50 for x in range(5)], 5)
# extractAll('baselineTestNS_5sli_AlgoTest_alpha05', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [50 for x in range(5)], 5)
# extractAll('baselineTestNS_5sli_AlgoTest_alpha10', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [50 for x in range(5)], 5)

# extractAll('baselineTestNS_2sli_LVD-BWS_AlgoTest_alpha00', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [50 for x in range(5)], 2)
# extractAll('baselineTestNS_2sli_LVD-BWS_AlgoTest_alpha05', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [50 for x in range(5)], 2)
# extractAll('baselineTestNS_2sli_LVD-BWS_AlgoTest_alpha10', ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [50 for x in range(5)], 2)

def getTcpFilteredDFtypeAndTS(df, filterType):
    filteredDF = filterDFType(df, filterType)
    cols = df.filter(filteredDF).columns
    colNoList = []
    for col in cols:
        if filterType == 'rtt:vector' and 'srtt' in col:
            continue
        # print(col, end=', ')
        colNoTS = df.columns.get_loc(col)
        colNoList.append(colNoTS)
        colNoList.append(colNoTS+1)
    # print('')
    if len(colNoList) <= 0:
        return pandas.DataFrame(columns=['ts', 'tp'])
    return df.iloc[:,colNoList].dropna()

def extractTCPDataTypeToDF(testName, numCLI, nodeTypes, nodeSplit, nodeType, nodeNum, dataType, dataIdent):
    print(dataIdent, end=' - ')
    nodeDF = importDF(testName, numCLI, nodeTypes, nodeSplit, nodeType, nodeNum)
    dataTypeDF = getTcpFilteredDFtypeAndTS(nodeDF, dataType)
    
    nodeIdent = makeNodeIdentifier(nodeType, nodeNum)
    renameDict = {}
    for i in range(int(len(dataTypeDF.columns)/2)):
        renameDict[str(dataTypeDF.columns[2*i])] = nodeIdent + " " + dataIdent + " TS"
        renameDict[str(dataTypeDF.columns[2*i+1])] = nodeIdent + " " + dataIdent + " Val"
    dataTypeDF = dataTypeDF.rename(columns=renameDict)
    # print(dataTypeDF)
    resultDF = dataTypeDF.iloc[:,[0,1]]
    for i in range(int(len(dataTypeDF.columns)/2)):
        resultDF = resultDF.append(dataTypeDF.iloc[:,[2*i,2*i+1]], ignore_index=True)
    # print(resultDF)
    return resultDF

def extractAllTCPDataTypeToDF(testName, numCLI, nodeTypes, nodeSplit, nodeTypesToExtract, dataType, dataIdent, folderName):
    dfAll = pandas.DataFrame()
    for nodeType,numNodes in zip(nodeTypes,nodeSplit):
        if nodeType in nodeTypesToExtract:
            for nodeNum in range(numNodes):
                dfAll = pandas.concat([dfAll,extractTCPDataTypeToDF(testName, numCLI, nodeTypes, nodeSplit, nodeType, nodeNum, dataType, dataIdent)],axis=1,ignore_index=False)

    prePath = '../exports/extracted/'+str(folderName)+'/'
    if not os.path.exists(prePath):
        os.makedirs(prePath)
    dfAll.to_csv(path_or_buf=prePath + makeFullScenarioName(testName, numCLI, nodeTypes, nodeSplit) + '.csv')

def extractTCPDataTypeSesToDF(testName, numCLI, nodeTypes, nodeSplit, nodeType, nodeNum, dataType, dataIdent):
    print(dataIdent, end=' - ')
    nodeDF = importDF(testName, numCLI, nodeTypes, nodeSplit, nodeType, nodeNum)
    dataTypeDF = getTcpFilteredDFtypeAndTS(nodeDF, dataType)
    
    nodeIdent = makeNodeIdentifier(nodeType, nodeNum)
    renameDict = {}
    for i in range(int(len(dataTypeDF.columns)/2)):
        sessionNum = dataTypeDF.columns[2*i].split('conn-')[-1].split(' ')[0]
        renameDict[str(dataTypeDF.columns[2*i])] = nodeIdent + ' conn-' + str(sessionNum) + ' ' + dataIdent + " TS"
        renameDict[str(dataTypeDF.columns[2*i+1])] = nodeIdent + ' conn-' + str(sessionNum) + ' ' + dataIdent + " Val"
    dataTypeDF = dataTypeDF.rename(columns=renameDict)
    # print(dataTypeDF)
    # resultDF = dataTypeDF.iloc[:,[0,1]]
    # for i in range(int(len(dataTypeDF.columns)/2)):
    #     resultDF = resultDF.append(dataTypeDF.iloc[:,[2*i,2*i+1]], ignore_index=True)
    # print(resultDF)
    return dataTypeDF

def extractAllTCPDataTypeSesToDF(testName, numCLI, nodeTypes, nodeSplit, nodeTypesToExtract, dataType, dataIdent, folderName):
    dfAll = pandas.DataFrame()
    for nodeType,numNodes in zip(nodeTypes,nodeSplit):
        if nodeType in nodeTypesToExtract:
            for nodeNum in range(numNodes):
                dfAll = pandas.concat([dfAll,extractTCPDataTypeSesToDF(testName, numCLI, nodeTypes, nodeSplit, nodeType, nodeNum, dataType, dataIdent)],axis=1,ignore_index=False)

    prePath = '../exports/extracted/'+str(folderName)+'/'
    if not os.path.exists(prePath):
        os.makedirs(prePath)
    dfAll.to_csv(path_or_buf=prePath + makeFullScenarioName(testName, numCLI, nodeTypes, nodeSplit) + '.csv')

def extractServerTCPDataTypeToDF(testName, numCLI, nodeTypes, nodeSplit, nodeType, nodeNum, dataType, dataIdent):
    print(dataIdent, end=' - ')
    nodeDF = importDF(testName, numCLI, nodeTypes, nodeSplit, nodeType, nodeNum)
    dataTypeDF = getTcpFilteredDFtypeAndTS(nodeDF, dataType)
    # print(dataTypeDF)
    nodeIdent = makeNodeIdentifier(nodeType, nodeNum)
    renameDict = {}
    for i in range(int(len(dataTypeDF.columns)/2)):
        renameDict[str(dataTypeDF.columns[2*i])] = nodeIdent + " " + dataIdent + " TS"
        renameDict[str(dataTypeDF.columns[2*i+1])] = nodeIdent + " " + dataIdent + " Val"
    dataTypeDF = dataTypeDF.rename(columns=renameDict)
    # print(dataTypeDF)
    resultDF = dataTypeDF.iloc[:,[0,1]]
    for i in range(int(len(dataTypeDF.columns)/2)):
        resultDF = resultDF.append(dataTypeDF.iloc[:,[2*i,2*i+1]], ignore_index=True)
    # print(resultDF)
    return resultDF

def extractAllServerTCPDataTypeToDF(testName, numCLI, nodeTypes, nodeSplit, nodeTypesToExtract, dataType, dataIdent, folderName):
    dfAll = pandas.DataFrame()
    for nodeType in nodeTypesToExtract:
        dfAll = pandas.concat([dfAll,extractServerTCPDataTypeToDF(testName, numCLI, nodeTypes, nodeSplit, nodeType, -1, dataType, dataIdent)],axis=1,ignore_index=False)

    prePath = '../exports/extracted/'+str(folderName)+'/'
    if not os.path.exists(prePath):
        os.makedirs(prePath)
    dfAll.to_csv(path_or_buf=prePath + makeFullScenarioName(testName, numCLI, nodeTypes, nodeSplit) + 'server.csv')

def extractServerTCPDataTypeSessionToDF(testName, numCLI, nodeTypes, nodeSplit, nodeType, nodeNum, dataType, dataIdent):
    print(dataIdent, end=' - ')
    nodeDF = importDF(testName, numCLI, nodeTypes, nodeSplit, nodeType, nodeNum)
    dataTypeDF = getTcpFilteredDFtypeAndTS(nodeDF, dataType)
    # print(list(dataTypeDF))
    nodeIdent = makeNodeIdentifier(nodeType, nodeNum)
    renameDict = {}
    for i in range(int(len(dataTypeDF.columns)/2)):
        sessionNum = dataTypeDF.columns[2*i].split('conn-')[-1].split(' ')[0]
        renameDict[str(dataTypeDF.columns[2*i])] = nodeIdent + ' conn-' + str(sessionNum) + ' ' + dataIdent + " TS"
        renameDict[str(dataTypeDF.columns[2*i+1])] = nodeIdent + ' conn-' + str(sessionNum) + ' ' + dataIdent + " Val"
    # print(dataTypeDF)
    dataTypeDF = dataTypeDF.rename(columns=renameDict)
    # print(dataTypeDF)
    # resultDF = dataTypeDF.iloc[:,[0,1]]
    # for i in range(int(len(dataTypeDF.columns)/2)):
    #     resultDF = resultDF.append(dataTypeDF.iloc[:,[2*i,2*i+1]], ignore_index=True)
    # print(resultDF)
    return dataTypeDF

def extractAllServerTCPDataTypeSessionToDF(testName, numCLI, nodeTypes, nodeSplit, nodeTypesToExtract, dataType, dataIdent, folderName):
    dfAll = pandas.DataFrame()
    for nodeType in nodeTypesToExtract:
        dfAll = pandas.concat([dfAll,extractServerTCPDataTypeSessionToDF(testName, numCLI, nodeTypes, nodeSplit, nodeType, -1, dataType, dataIdent)],axis=1,ignore_index=False)

    prePath = '../exports/extracted/'+str(folderName)+'/'
    if not os.path.exists(prePath):
        os.makedirs(prePath)
    dfAll.to_csv(path_or_buf=prePath + makeFullScenarioName(testName, numCLI, nodeTypes, nodeSplit) + 'server.csv')


def calculateThrougputPerSecondDirectionFine(df, direction, nodeIdent):
    dirDF = getFilteredDFtypeAndTS(df, direction[1])
    dirDF = dirDF.rename(columns={str(dirDF.columns[0]) : "ts", str(dirDF.columns[1]) : "bytes"})
    tB = [0,0.1] # time bounds for calculation
    colName = direction[0] + ' Throughput ' + nodeIdent
    tpDirDF = pandas.DataFrame(columns=[colName])
    while tB[1] <= maxSimTime:
        if DEBUG: print(tB, end =" -> Throughput: ")
        throughput = dirDF.loc[(dirDF['ts'] > tB[0]) & (dirDF['ts'] <= tB[1])]["bytes"].sum()
        tpDirDF = tpDirDF.append({colName : throughput*8/100}, ignore_index=True)
        if DEBUG: print(throughput*8/1000, end=" kbps\n")
        tB = [x+0.1 for x in tB]
    return tpDirDF

def extractNodeThroughputDirectionFine(testName, numCLI, nodeTypes, nodeSplit, nodeType, nodeNum, direction):
    print('TP ' + direction[0], end=' - ')
    nodeDF = importDF(testName, numCLI, nodeTypes, nodeSplit, nodeType, nodeNum)
    nodeIdent = makeNodeIdentifier(nodeType, nodeNum)
    return calculateThrougputPerSecondDirectionFine(nodeDF, direction, nodeIdent)

def extractAllThroughputsDirectionFine(testName, numCLI, nodeTypes, nodeSplit, nodeTypesToExtract, numSlices, direction):
    # Prepare result dataframe
    tpDFall = pandas.DataFrame()
    # Add nodes tps
    for nodeType,numNodes in zip(nodeTypesToExtract,nodeSplit):
        for nodeNum in range(numNodes):
            tpDFall = pandas.concat([tpDFall,extractNodeThroughputDirectionFine(testName, numCLI, nodeTypes, nodeSplit, nodeType, nodeNum ,direction)],axis=1,ignore_index=False)
    if not os.path.exists('../exports/extracted/throughputs/'):
        os.makedirs('../exports/extracted/throughputs/')
    # Export to csv
    tpDFall.to_csv(path_or_buf='../exports/extracted/throughputs/'+makeFullScenarioName(testName, numCLI, nodeTypes, nodeSplit)+'_'+direction[0]+'_'+str(nodeTypesToExtract)+'.csv')

def extractCumulativeDequeueIndexToDF(testName, numCLI, nodeTypes, nodeSplit, nodeType, nodeNum, dataType, dataIdent):
    print(dataIdent, end=' - ')
    nodeDF = importDF(testName, numCLI, nodeTypes, nodeSplit, nodeType, nodeNum)
    dataTypeDF = getTcpFilteredDFtypeAndTS(nodeDF, dataType)
    # print(dataTypeDF)
    nodeIdent = makeNodeIdentifier(nodeType, nodeNum)
    renameDict = {}
    for i in range(int(len(dataTypeDF.columns)/2)):
        renameDict[str(dataTypeDF.columns[2*i])] = nodeIdent + " " + dataIdent + " TS"
        renameDict[str(dataTypeDF.columns[2*i+1])] = nodeIdent + " " + dataIdent + " Val"
    dataTypeDF = dataTypeDF.rename(columns=renameDict)
    # print(dataTypeDF)
    boundsVID = [0,nodeSplit[nodeTypes.index('hostVID')]-1]
    boundsLVD = [boundsVID[-1]+1,boundsVID[-1]+nodeSplit[nodeTypes.index('hostLVD')]]
    boundsFDO = [boundsLVD[-1]+1,boundsLVD[-1]+nodeSplit[nodeTypes.index('hostFDO')]]
    boundsVIP = [boundsFDO[-1]+1,boundsFDO[-1]+nodeSplit[nodeTypes.index('hostVIP')]]
    boundsSSH = [boundsVIP[-1]+1,boundsVIP[-1]+nodeSplit[nodeTypes.index('hostSSH')]]

    print(boundsVID, boundsLVD, boundsFDO, boundsVIP, boundsSSH)
    
    resultDF = pandas.DataFrame(columns=[nodeIdent + " " + dataIdent + "VID TS", nodeIdent + " " + dataIdent + "VID Val", nodeIdent + " " + dataIdent + "LVD TS", nodeIdent + " " + dataIdent + "LVD Val", nodeIdent + " " + dataIdent + "FDO TS", nodeIdent + " " + dataIdent + "FDO Val", nodeIdent + " " + dataIdent + "VIP TS", nodeIdent + " " + dataIdent + "VIP Val", nodeIdent + " " + dataIdent + "SSH TS", nodeIdent + " " + dataIdent + "SSH Val"])

    countVID = 0
    countLVD = 0
    countFDO = 0
    countVIP = 0
    countSSH = 0

    vid = {nodeIdent + " " + dataIdent + "VID TS" : [], nodeIdent + " " + dataIdent + "VID Val" : []}
    lvd = {nodeIdent + " " + dataIdent + "LVD TS" : [], nodeIdent + " " + dataIdent + "LVD Val" : []}
    fdo = {nodeIdent + " " + dataIdent + "FDO TS" : [], nodeIdent + " " + dataIdent + "FDO Val" : []}
    vip = {nodeIdent + " " + dataIdent + "VIP TS" : [], nodeIdent + " " + dataIdent + "VIP Val" : []}
    ssh = {nodeIdent + " " + dataIdent + "SSH TS" : [], nodeIdent + " " + dataIdent + "SSH Val" : []}

    for index, row in dataTypeDF.iterrows():
        if row[nodeIdent + " " + dataIdent + " Val"] <= boundsVID[1]:
            countVID += 1
            vid[nodeIdent + " " + dataIdent + "VID TS"].append(row[nodeIdent + " " + dataIdent + " TS"])
            vid[nodeIdent + " " + dataIdent + "VID Val"].append(countVID)
        elif row[nodeIdent + " " + dataIdent + " Val"] <= boundsLVD[1]:
            countLVD += 1
            lvd[nodeIdent + " " + dataIdent + "LVD TS"].append(row[nodeIdent + " " + dataIdent + " TS"])
            lvd[nodeIdent + " " + dataIdent + "LVD Val"].append(countLVD)
        elif row[nodeIdent + " " + dataIdent + " Val"] <= boundsFDO[1]:
            countFDO += 1
            fdo[nodeIdent + " " + dataIdent + "FDO TS"].append(row[nodeIdent + " " + dataIdent + " TS"])
            fdo[nodeIdent + " " + dataIdent + "FDO Val"].append(countFDO)
        elif row[nodeIdent + " " + dataIdent + " Val"] <= boundsVIP[1]:
            countVIP += 1
            vip[nodeIdent + " " + dataIdent + "VIP TS"].append(row[nodeIdent + " " + dataIdent + " TS"])
            vip[nodeIdent + " " + dataIdent + "VIP Val"].append(countVIP)
        elif row[nodeIdent + " " + dataIdent + " Val"] <= boundsSSH[1]:
            countSSH += 1
            ssh[nodeIdent + " " + dataIdent + "SSH TS"].append(row[nodeIdent + " " + dataIdent + " TS"])
            ssh[nodeIdent + " " + dataIdent + "SSH Val"].append(countSSH)
        
        if index > 1 and index % 2000 == 0:
            print(index, row[nodeIdent + " " + dataIdent + " TS"], end='; Nums: ')
            print('VID:', countVID, 'LVD:', countLVD, 'SSH:', countSSH, 'VIP:', countVIP, 'FDO:', countFDO)
    print(countVID, countLVD, countSSH, countVIP, countFDO)
    vidDF = pandas.DataFrame.from_dict(vid)
    # print(vid)
    lvdDF = pandas.DataFrame.from_dict(lvd)
    fdoDF = pandas.DataFrame.from_dict(fdo)
    vipDF = pandas.DataFrame.from_dict(vip)
    sshDF = pandas.DataFrame.from_dict(ssh)
    
    resultDF = pandas.concat([vidDF, lvdDF, fdoDF, vipDF, sshDF], axis=1)

    print(resultDF)
    return resultDF

def extractAllCumulativeDequeueIndexToDF(testName, numCLI, nodeTypes, nodeSplit, nodeTypesToExtract, dataType, dataIdent, folderName):
    dfAll = pandas.DataFrame()
    for nodeType in nodeTypesToExtract:
        dfAll = pandas.concat([dfAll,extractCumulativeDequeueIndexToDF(testName, numCLI, nodeTypes, nodeSplit, nodeType, -1, dataType, dataIdent)],axis=1,ignore_index=False)

    prePath = '../exports/extracted/'+str(folderName)+'/'
    if not os.path.exists(prePath):
        os.makedirs(prePath)
    dfAll.to_csv(path_or_buf=prePath + makeFullScenarioName(testName, numCLI, nodeTypes, nodeSplit) + '.csv')


def extractCumulativeDequeueIndexPerFlowToDF(testName, numCLI, nodeTypes, nodeSplit, nodeType, nodeNum, dataType, dataIdent):
    print(dataIdent, end=' - ')
    nodeDF = importDF(testName, numCLI, nodeTypes, nodeSplit, nodeType, nodeNum)
    dataTypeDF = getTcpFilteredDFtypeAndTS(nodeDF, dataType)
    print(list(dataTypeDF))
    nodeIdent = makeNodeIdentifier(nodeType, nodeNum)
    renameDict = {}
    for i in range(int(len(dataTypeDF.columns)/2)):
        renameDict[str(dataTypeDF.columns[2*i])] = nodeIdent + " " + dataIdent + " TS"
        renameDict[str(dataTypeDF.columns[2*i+1])] = nodeIdent + " " + dataIdent + " Val"
    dataTypeDF = dataTypeDF.rename(columns=renameDict)
    # print(dataTypeDF)
    boundsVID = [0,nodeSplit[nodeTypes.index('hostVID')]-1]
    boundsLVD = [boundsVID[-1]+1,boundsVID[-1]+nodeSplit[nodeTypes.index('hostLVD')]]
    boundsFDO = [boundsLVD[-1]+1,boundsLVD[-1]+nodeSplit[nodeTypes.index('hostFDO')]]
    boundsVIP = [boundsFDO[-1]+1,boundsFDO[-1]+nodeSplit[nodeTypes.index('hostVIP')]]
    boundsSSH = [boundsVIP[-1]+1,boundsVIP[-1]+nodeSplit[nodeTypes.index('hostSSH')]]

    print(boundsVID, boundsLVD, boundsFDO, boundsVIP, boundsSSH)
    
    # resultDF = pandas.DataFrame(columns=[nodeIdent + " " + dataIdent + "VID TS", nodeIdent + " " + dataIdent + "VID Val", nodeIdent + " " + dataIdent + "LVD TS", nodeIdent + " " + dataIdent + "LVD Val", nodeIdent + " " + dataIdent + "FDO TS", nodeIdent + " " + dataIdent + "FDO Val", nodeIdent + " " + dataIdent + "VIP TS", nodeIdent + " " + dataIdent + "VIP Val", nodeIdent + " " + dataIdent + "SSH TS", nodeIdent + " " + dataIdent + "SSH Val"])

    # countVID = 0
    # countLVD = 0
    # countFDO = 0
    # countVIP = 0
    # countSSH = 0

    vid = {}
    lvd = {}
    fdo = {}
    vip = {}
    ssh = {}

    for i in range(nodeSplit[nodeTypes.index('hostVID')]):
        vid['VID' + str(i) + ' ' + dataIdent + ' TS'] = [0]
        vid['VID' + str(i) + ' ' + dataIdent + ' Val'] = [0]
    for i in range(nodeSplit[nodeTypes.index('hostLVD')]):
        lvd['LVD' + str(i) + ' ' + dataIdent + ' TS'] = [0]
        lvd['LVD' + str(i) + ' ' + dataIdent + ' Val'] = [0]
    for i in range(nodeSplit[nodeTypes.index('hostFDO')]):
        fdo['FDO' + str(i) + ' ' + dataIdent + ' TS'] = [0]
        fdo['FDO' + str(i) + ' ' + dataIdent + ' Val'] = [0]
    for i in range(nodeSplit[nodeTypes.index('hostVIP')]):
        vip['VIP' + str(i) + ' ' + dataIdent + ' TS'] = [0]
        vip['VIP' + str(i) + ' ' + dataIdent + ' Val'] = [0]
    for i in range(nodeSplit[nodeTypes.index('hostSSH')]):
        ssh['SSH' + str(i) + ' ' + dataIdent + ' TS'] = [0]
        ssh['SSH' + str(i) + ' ' + dataIdent + ' Val'] = [0]
    
    for index, row in dataTypeDF.iterrows():
        nodeId = row[nodeIdent + " " + dataIdent + " Val"]
        if nodeId <= boundsVID[1]:
            countVID = vid['VID' + str(int(nodeId)) + ' ' + dataIdent + ' Val'][-1] + 1
            vid['VID' + str(int(nodeId)) + ' ' + dataIdent + ' TS'].append(row[nodeIdent + " " + dataIdent + " TS"])
            vid['VID' + str(int(nodeId)) + ' ' + dataIdent + ' Val'].append(countVID)
        elif nodeId <= boundsLVD[1]:
            nodeId = nodeId - boundsLVD[0]
            countLVD = lvd['LVD' + str(int(nodeId)) + ' ' + dataIdent + ' Val'][-1] + 1
            lvd['LVD' + str(int(nodeId)) + ' ' + dataIdent + ' TS'].append(row[nodeIdent + " " + dataIdent + " TS"])
            lvd['LVD' + str(int(nodeId)) + ' ' + dataIdent + ' Val'].append(countLVD)
        elif nodeId <= boundsFDO[1]:
            nodeId = nodeId - boundsFDO[0]
            countFDO = fdo['FDO' + str(int(nodeId)) + ' ' + dataIdent + ' Val'][-1] + 1
            fdo['FDO' + str(int(nodeId)) + ' ' + dataIdent + ' TS'].append(row[nodeIdent + " " + dataIdent + " TS"])
            fdo['FDO' + str(int(nodeId)) + ' ' + dataIdent + ' Val'].append(countFDO)
        elif nodeId <= boundsVIP[1]:
            nodeId = nodeId - boundsVIP[0]
            countVIP = vip['VIP' + str(int(nodeId)) + ' ' + dataIdent + ' Val'][-1] + 1
            vip['VIP' + str(int(nodeId)) + ' ' + dataIdent + ' TS'].append(row[nodeIdent + " " + dataIdent + " TS"])
            vip['VIP' + str(int(nodeId)) + ' ' + dataIdent + ' Val'].append(countVIP)
        elif nodeId <= boundsSSH[1]:
            nodeId = nodeId - boundsSSH[0]
            countSSH = ssh['SSH' + str(int(nodeId)) + ' ' + dataIdent + ' Val'][-1] + 1
            ssh['SSH' + str(int(nodeId)) + ' ' + dataIdent + ' TS'].append(row[nodeIdent + " " + dataIdent + " TS"])
            ssh['SSH' + str(int(nodeId)) + ' ' + dataIdent + ' Val'].append(countSSH)
        
        if index > 1 and index % 2000 == 0:
            print(index, row[nodeIdent + " " + dataIdent + " TS"], end='; Nums: ')
            print('VID:', countVID, 'LVD:', countLVD, 'SSH:', countSSH, 'VIP:', countVIP, 'FDO:', countFDO)
            # break
    print(countVID, countLVD, countSSH, countVIP, countFDO)
    vidDF = pandas.DataFrame.from_dict(dict([ (k,pandas.Series(v)) for k,v in vid.items() ]))
    # print(vid)
    lvdDF = pandas.DataFrame.from_dict(dict([ (k,pandas.Series(v)) for k,v in lvd.items() ]))
    fdoDF = pandas.DataFrame.from_dict(dict([ (k,pandas.Series(v)) for k,v in fdo.items() ]))
    vipDF = pandas.DataFrame.from_dict(dict([ (k,pandas.Series(v)) for k,v in vip.items() ]))
    sshDF = pandas.DataFrame.from_dict(dict([ (k,pandas.Series(v)) for k,v in ssh.items() ]))
    
    resultDF = pandas.concat([vidDF, lvdDF, fdoDF, vipDF, sshDF], axis=1)

    print(resultDF)
    return resultDF

def extractAllCumulativeDequeueIndexPerFlowToDF(testName, numCLI, nodeTypes, nodeSplit, nodeTypesToExtract, dataType, dataIdent, folderName):
    dfAll = pandas.DataFrame()
    for nodeType in nodeTypesToExtract:
        dfAll = pandas.concat([dfAll,extractCumulativeDequeueIndexPerFlowToDF(testName, numCLI, nodeTypes, nodeSplit, nodeType, -1, dataType, dataIdent)],axis=1,ignore_index=False)

    prePath = '../exports/extracted/'+str(folderName)+'/'
    if not os.path.exists(prePath):
        os.makedirs(prePath)
    dfAll.to_csv(path_or_buf=prePath + makeFullScenarioName(testName, numCLI, nodeTypes, nodeSplit) + '.csv')


def extractDequeueRateAppTypeDiff(testName, numCLI, nodeTypes, nodeSplit, nodeTypesToExtract, dataType, dataIdent, folderName):
    fullScenarioName = makeFullScenarioName(testName, numCLI, nodeTypes, nodeSplit)
    file_to_read = '../exports/extracted/' + str(dataType) + '/' + fullScenarioName + '.csv'
    print("Results from run: " + file_to_read)
    # Read the CSV
    df = pandas.read_csv(file_to_read)
    retDF = pandas.DataFrame()
    for nodeType in nodeTypesToExtract:
        tempDF = df.filter(like=nodeType).iloc[:,[0,1]]
        print(list(tempDF))
        tB = [0,0.1]
        rates = []
        while tB[1] <= 400:
            theDF = tempDF.loc[(tempDF[tempDF.columns[0]] > tB[0]) & (tempDF[tempDF.columns[0]] <= tB[1])]
            rates.append(len(theDF.index))
            tB = [x+0.1 for x in tB]
        typeDF = pandas.DataFrame(rates, columns=[nodeType + " " + dataIdent + " Rate"])
        retDF = pandas.concat([retDF,typeDF],axis=1,ignore_index=False)
    
    prePath = '../exports/extracted/'+str(folderName)+'/'
    if not os.path.exists(prePath):
        os.makedirs(prePath)
    retDF.to_csv(path_or_buf=prePath + makeFullScenarioName(testName, numCLI, nodeTypes, nodeSplit) + '_' + str(nodeTypesToExtract) + '.csv')

def extractInterDepartureTimeAppTypeDiff(testName, numCLI, nodeTypes, nodeSplit, nodeTypesToExtract, dataType, dataIdent, folderName):
    fullScenarioName = makeFullScenarioName(testName, numCLI, nodeTypes, nodeSplit)
    file_to_read = '../exports/extracted/' + str(dataType) + '/' + fullScenarioName + '.csv'
    print("Results from run: " + file_to_read)
    # Read the CSV
    df = pandas.read_csv(file_to_read)
    retDF = pandas.DataFrame()
    for nodeType in nodeTypesToExtract:
        for nodeNum in range(nodeSplit[nodeTypes.index('host'+nodeType)]):
            tempDF = df.filter(like=nodeType+str(nodeNum)).iloc[:,[0,1]]
            print(list(tempDF))
            idtTS = []
            idtVal = [-1]
            for index, row in tempDF.iterrows():
                idtTS.append(row[tempDF.columns[0]])
                if len(idtTS) > 1:
                    idtVal.append(idtTS[-1] - idtTS[-2])
            # d = {nodeType + str(nodeNum) + " " + dataIdent + " TS":idtTS, nodeType + str(nodeNum) + " " + dataIdent + " Val":idtVal}
            # typeDF = pandas.DataFrame(data=[idtTS, idtVal], columns=[nodeType + str(nodeNum) + " " + dataIdent + " TS", nodeType + str(nodeNum) + " " + dataIdent + " Val"])
            typeDF = pandas.DataFrame(data={nodeType + str(nodeNum) + " " + dataIdent + " TS":idtTS, nodeType + str(nodeNum) + " " + dataIdent + " Val":idtVal})
            retDF = pandas.concat([retDF,typeDF],axis=1,ignore_index=False)
    
    prePath = '../exports/extracted/'+str(folderName)+'/'
    if not os.path.exists(prePath):
        os.makedirs(prePath)
    retDF.to_csv(path_or_buf=prePath + makeFullScenarioName(testName, numCLI, nodeTypes, nodeSplit) + '_' + str(nodeTypesToExtract) + '.csv')

def extractHTBdataToDF(testName, numCLI, nodeTypes, nodeSplit, nodeType, nodeNum, dataType, dataIdent):
    print(dataIdent, end=' - ')
    nodeDF = importDF(testName, numCLI, nodeTypes, nodeSplit, nodeType, nodeNum)
    print(list(nodeDF))
    print(len(nodeDF.index))
    # dataTypeDF = getTcpFilteredDFtypeAndTS(nodeDF, dataType)
    # print(list(dataTypeDF))
    boundsVID = [0,nodeSplit[nodeTypes.index('hostVID')]-1]
    boundsLVD = [boundsVID[-1]+1,boundsVID[-1]+nodeSplit[nodeTypes.index('hostLVD')]]
    boundsFDO = [boundsLVD[-1]+1,boundsLVD[-1]+nodeSplit[nodeTypes.index('hostFDO')]]
    boundsVIP = [boundsFDO[-1]+1,boundsFDO[-1]+nodeSplit[nodeTypes.index('hostVIP')]]
    boundsSSH = [boundsVIP[-1]+1,boundsVIP[-1]+nodeSplit[nodeTypes.index('hostSSH')]]
    
    # nodeIdent = makeNodeIdentifier(nodeType, nodeNum)
    renameDict = {}
    for i in range(int(len(nodeDF.columns)/2)):
        col = nodeDF.columns[2*i]
        if 'queue[' not in col:
            renameDict[str(nodeDF.columns[2*i])] = "ignore TS"
            renameDict[str(nodeDF.columns[2*i+1])] = "ignore Val"
            continue
        print(col)
        nodeId = int(col.split('queue.queue[')[1].split(']')[0])
        print(nodeId)
        if nodeId <= boundsVID[1]:
            renameDict[str(nodeDF.columns[2*i])] = 'VID' + str(int(nodeId)) + ' ' + dataIdent + ' TS'
            renameDict[str(nodeDF.columns[2*i+1])] = 'VID' + str(int(nodeId)) + ' ' + dataIdent + ' Val'
        elif nodeId <= boundsLVD[1]:
            nodeId = nodeId - boundsLVD[0]
            renameDict[str(nodeDF.columns[2*i])] = 'LVD' + str(int(nodeId)) + ' ' + dataIdent + ' TS'
            renameDict[str(nodeDF.columns[2*i+1])] = 'LVD' + str(int(nodeId)) + ' ' + dataIdent + ' Val'
        elif nodeId <= boundsFDO[1]:
            nodeId = nodeId - boundsFDO[0]
            renameDict[str(nodeDF.columns[2*i])] = 'FDO' + str(int(nodeId)) + ' ' + dataIdent + ' TS'
            renameDict[str(nodeDF.columns[2*i+1])] = 'FDO' + str(int(nodeId)) + ' ' + dataIdent + ' Val'
        elif nodeId <= boundsVIP[1]:
            nodeId = nodeId - boundsVIP[0]
            renameDict[str(nodeDF.columns[2*i])] = 'VIP' + str(int(nodeId)) + ' ' + dataIdent + ' TS'
            renameDict[str(nodeDF.columns[2*i+1])] = 'VIP' + str(int(nodeId)) + ' ' + dataIdent + ' Val'
        elif nodeId <= boundsSSH[1]:
            nodeId = nodeId - boundsSSH[0]
            renameDict[str(nodeDF.columns[2*i])] = 'SSH' + str(int(nodeId)) + ' ' + dataIdent + ' TS'
            renameDict[str(nodeDF.columns[2*i+1])] = 'SSH' + str(int(nodeId)) + ' ' + dataIdent + ' Val'

        
    # print(dataTypeDF)
    nodeDF = nodeDF.rename(columns=renameDict)
    retDF = nodeDF.filter(like=dataIdent)
    print(list(retDF))
    return retDF.dropna(axis=0, how='all')

def extractHTBdataAllToDF(testName, numCLI, nodeTypes, nodeSplit, nodeTypesToExtract, dataType, dataIdent, folderName):
    dfAll = pandas.DataFrame()
    for nodeType in nodeTypesToExtract:
        dfAll = pandas.concat([dfAll,extractHTBdataToDF(testName, numCLI, nodeTypes, nodeSplit, nodeType, -1, dataType, dataIdent)],axis=1,ignore_index=False)

    prePath = '../exports/extracted/'+str(folderName)+'/'
    if not os.path.exists(prePath):
        os.makedirs(prePath)
    dfAll.to_csv(path_or_buf=prePath + makeFullScenarioName(testName, numCLI, nodeTypes, nodeSplit) + '.csv')

def extractHTBdataFlowTypeToDF(testName, numCLI, nodeTypes, nodeSplit, nodeTypeToExtract, numNodesToExport, dataType, dataIdent, folderName):
    fullScenarioName = makeFullScenarioName(testName, numCLI, nodeTypes, nodeSplit)
    file_to_read = '../exports/extracted/' + str(dataType) + '/' + fullScenarioName + '.csv'
    print("Results from run: " + file_to_read)
    # Read the CSV
    dfAll = pandas.read_csv(file_to_read)
    
    dfAll = dfAll.filter(like=nodeTypeToExtract)

    dfExport = pandas.DataFrame()

    for i in numNodesToExport:
        dfExport = pandas.concat([dfExport,dfAll.filter(like=nodeTypeToExtract+str(i)+' '+dataIdent)],axis=1,ignore_index=False)

    prePath = '../exports/extracted/'+str(folderName)+'/'
    if not os.path.exists(prePath):
        os.makedirs(prePath)
    dfExport.to_csv(path_or_buf=prePath + makeFullScenarioName(testName, numCLI, nodeTypes, nodeSplit) + '.csv')

if __name__ == "__main__":
    name = sys.argv[3]
    print(name)
    numVID = int(name.split('VID')[1].split('_LVD')[0])
    numLVD = int(name.split('LVD')[1].split('_FDO')[0])
    numFDO = int(name.split('FDO')[1].split('_SSH')[0])
    numSSH = int(name.split('SSH')[1].split('_VIP')[0])
    numVIP = int(name.split('VIP')[1])
    # print('test')
    # extractAllTCPDataTypeSesToDF(sys.argv[1], numVID + numLVD + numFDO + numSSH + numVIP, ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [numVID, numLVD, numFDO, numSSH, numVIP], ['hostVID', 'hostLVD', 'hostFDO'], 'dupAcks', 'dAck', 'dAckSes')
    # extractAllTCPDataTypeSesToDF(sys.argv[1], numVID + numLVD + numFDO + numSSH + numVIP, ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [numVID, numLVD, numFDO, numSSH, numVIP], ['hostVID', 'hostLVD', 'hostFDO'], 'numRtos', 'nRto', 'nRtoSes')
    # extractAllTCPDataTypeSesToDF(sys.argv[1], numVID + numLVD + numFDO + numSSH + numVIP, ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [numVID, numLVD, numFDO, numSSH, numVIP], ['hostVID', 'hostLVD', 'hostFDO'], 'cwnd', 'cwnd', 'cwndSes')
    # extractAllServerTCPDataTypeSessionToDF(sys.argv[1], numVID + numLVD + numFDO + numSSH + numVIP, ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [numVID, numLVD, numFDO, numSSH, numVIP], ['serverVID', 'serverLVD', 'serverFDO'], 'dupAcks', 'dAck', 'dAckSes')
    # extractAllServerTCPDataTypeSessionToDF(sys.argv[1], numVID + numLVD + numFDO + numSSH + numVIP, ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [numVID, numLVD, numFDO, numSSH, numVIP], ['serverVID', 'serverLVD', 'serverFDO'], 'numRtos', 'nRto', 'nRtoSes')
    # extractAllServerTCPDataTypeSessionToDF(sys.argv[1], numVID + numLVD + numFDO + numSSH + numVIP, ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [numVID, numLVD, numFDO, numSSH, numVIP], ['serverVID', 'serverLVD', 'serverFDO'], 'cwnd', 'cwnd', 'cwndSes')
    # extractAllServerTCPDataTypeSessionToDF(sys.argv[1], numVID + numLVD + numFDO + numSSH + numVIP, ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [numVID, numLVD, numFDO, numSSH, numVIP], ['serverVID', 'serverLVD', 'serverFDO'], 'rtt:vector', 'rtt', 'rttSes')
    # extractAllServerTCPDataTypeSessionToDF(sys.argv[1], numVID + numLVD + numFDO + numSSH + numVIP, ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [numVID, numLVD, numFDO, numSSH, numVIP], ['serverVID', 'serverLVD', 'serverFDO'], 'srtt:vector', 'srtt', 'srttSes')
    # extractAllServerTCPDataTypeSessionToDF(sys.argv[1], numVID + numLVD + numFDO + numSSH + numVIP, ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [numVID, numLVD, numFDO, numSSH, numVIP], ['serverVID', 'serverLVD', 'serverFDO'], 'rttvar:vector', 'rttvar', 'rttvarSes')
    # extractAllServerTCPDataTypeSessionToDF(sys.argv[1], numVID + numLVD + numFDO + numSSH + numVIP, ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [numVID, numLVD, numFDO, numSSH, numVIP], ['serverVID', 'serverLVD', 'serverFDO'], 'rto:vector', 'rto', 'rtoSes')
    # extractAllThroughputsDirectionFine(sys.argv[1], numVID + numLVD + numFDO + numSSH + numVIP, ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [numVID, numLVD, numFDO, numSSH, numVIP], ['hostVIP'], 1, downlink)
    # extractAllCumulativeDequeueIndexToDF(sys.argv[1], numVID + numLVD + numFDO + numSSH + numVIP, ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [numVID, numLVD, numFDO, numSSH, numVIP], ['router1_dI'], 'dequeueIndex:vector', 'dI', 'dI')

    # extractAllTCPDataTypeToDF(sys.argv[1], numVID + numLVD + numFDO + numSSH + numVIP, ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [numVID, numLVD, numFDO, numSSH, numVIP], ['hostVID', 'hostLVD', 'hostFDO'], 'rtt:vector', 'rtt', 'rttClis')

    # extractAllCumulativeDequeueIndexPerFlowToDF(sys.argv[1], numVID + numLVD + numFDO + numSSH + numVIP, ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [numVID, numLVD, numFDO, numSSH, numVIP], ['router1_dI'], 'dequeueIndex:vector', 'dIpF', 'dIpF')

    # extractHTBdataAllToDF(sys.argv[1], numVID + numLVD + numFDO + numSSH + numVIP, ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [numVID, numLVD, numFDO, numSSH, numVIP], ['router1_qL'], 'queueLength', 'qL', 'qL')

    # extractHTBdataFlowTypeToDF(sys.argv[1], numVID + numLVD + numFDO + numSSH + numVIP, ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [numVID, numLVD, numFDO, numSSH, numVIP], 'VID', [0,1,2,3,4], 'qL', 'qL', 'qLVID')

    extractHTBdataFlowTypeToDF(sys.argv[1], numVID + numLVD + numFDO + numSSH + numVIP, ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [numVID, numLVD, numFDO, numSSH, numVIP], 'hostVID', [0,1,2,3,4], 'endToEndDelay', 'E2ED', 'e2edVID')
    extractHTBdataFlowTypeToDF(sys.argv[1], numVID + numLVD + numFDO + numSSH + numVIP, ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [numVID, numLVD, numFDO, numSSH, numVIP], 'hostVID', [0,1,2,3,4], 'dabl', 'DABL', 'dablVID')
    extractHTBdataFlowTypeToDF(sys.argv[1], numVID + numLVD + numFDO + numSSH + numVIP, ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [numVID, numLVD, numFDO, numSSH, numVIP], 'hostVID', [0,1,2,3,4], 'davb', 'DAVB', 'davbVID')

    # extractInterDepartureTimeAppTypeDiff(sys.argv[1], numVID + numLVD + numFDO + numSSH + numVIP, ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [numVID, numLVD, numFDO, numSSH, numVIP], ['VIP'], 'dIpF', 'interDepartureTime', 'interDepartureTime')
    # extractInterDepartureTimeAppTypeDiff(sys.argv[1], numVID + numLVD + numFDO + numSSH + numVIP, ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [numVID, numLVD, numFDO, numSSH, numVIP], ['VID'], 'dIpF', 'interDepartureTime', 'interDepartureTime')
    # extractDequeueRateAppTypeDiff(sys.argv[1], numVID + numLVD + numFDO + numSSH + numVIP, ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [numVID, numLVD, numFDO, numSSH, numVIP], ['VIP'], 'dI', 'dIrate', 'dIrate')
    
    # extractAll(sys.argv[1], ['hostVID', 'hostLVD', 'hostFDO', 'hostSSH', 'hostVIP'], [numVID, numLVD, numFDO, numSSH, numVIP], int(sys.argv[2]))